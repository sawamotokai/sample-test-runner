import sys
import tempfile
import unittest
from email.utils import formatdate
from pathlib import Path
from unittest.mock import Mock, call, patch

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import parse

TASKS = '''<table><thead><tr><th>Task</th></tr></thead><tbody>
<tr><td><a href="/contests/abc086/tasks/abc086_a">A</a></td></tr>
<tr><td><a href="/contests/abc086/tasks/arc089_a">C</a></td></tr>
</tbody></table>'''
SAMPLES = '''<div class="lang-ja">
<section><h3>入力</h3><pre><var>a b</var></pre></section>
<section><h3>入力例 1</h3><pre>3 4\n</pre></section>
<section><h3>出力例 1</h3><pre>Even\n</pre></section>
<section><h3>入力例 2</h3><pre>1 21\n</pre></section>
<section><h3>出力例 2</h3><pre>Odd\n</pre></section>
</div><div class="lang-en">
<section><h3>Input</h3><pre><var>a b</var></pre></section>
<section><h3>Sample Input 1</h3><pre>3 4\n</pre></section>
<section><h3>Sample Output 1</h3><pre>Even\n</pre></section>
<section><h3>Sample Input 2</h3><pre>1 21\n</pre></section>
<section><h3>Sample Output 2</h3><pre>Odd\n</pre></section>
</div>'''


def response(html, status=200):
    result = requests.Response()
    result.status_code = status
    result._content = html.encode()
    result.encoding = "utf-8"
    return result


class AtCoderTests(unittest.TestCase):
    def test_public_samples_do_not_require_login(self):
        with patch.object(parse, "atcoder_username", ""), \
             patch.object(parse, "atcoder_password", ""), \
             patch.object(parse.Ask, "list_input", return_value="AtCoder"), \
             patch.object(parse.AtCoderParser, "login") as login:
            parser = parse.ParserFactory.get()
        login.assert_not_called()
        self.assertIsInstance(parser.session, requests.Session)

    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory(prefix="atcoder samples ")
        self.addCleanup(self.workspace.cleanup)
        self.parser = parse.AtCoderParser.__new__(parse.AtCoderParser)
        self.parser.session = Mock()
        self.sleep = self.enterContext(patch.object(parse.time, "sleep"))
        self.contest = Path(self.workspace.name) / "AtCoder" / "ABC" / "086"
        self.parser.folderName = str(self.contest)
        # Existing solutions must survive fetching samples again.
        for label in ("A", "B", "C"):
            directory = self.contest / label
            directory.mkdir(parents=True)
            (directory / f"{label}.cpp").write_text("existing solution\n")

    def fetch_samples(self):
        with patch.object(parse, "rootPath", self.workspace.name), \
             patch.object(parse.Ask, "list_input", return_value="ABC"), \
             patch.object(parse.Ask, "text", return_value="086"):
            self.parser.parse()

    def test_follows_actual_task_urls_and_writes_samples_once(self):
        self.parser.session.get.side_effect = lambda url, **kwargs: response(TASKS if url.endswith('/tasks') else SAMPLES)
        self.fetch_samples()
        urls = [call.args[0] for call in self.parser.session.get.call_args_list]
        self.assertCountEqual(urls, [
            "https://atcoder.jp/contests/abc086/tasks",
            "https://atcoder.jp/contests/abc086/tasks/abc086_a",
            "https://atcoder.jp/contests/abc086/tasks/arc089_a",
        ])
        for label in ("A", "C"):
            directory = self.contest / label
            self.assertEqual((directory / "1.in").read_text(), "3 4\n")
            self.assertEqual((directory / "2.out").read_text(), "Odd\n")
            self.assertEqual(len(list(directory.glob("*.in"))), 2)
            self.assertEqual((directory / f"{label}.cpp").read_text(), "existing solution\n")
        self.assertEqual(self.sleep.call_args_list, [call(2), call(2)])

    def test_rate_limit_waits_then_downloads_samples(self):
        self.parser.session.get.side_effect = [response("", 429), response("", 429), response(SAMPLES)]
        self.parser.parseProblem("A", "https://atcoder.jp/contests/abc483/tasks/abc483_a")
        self.assertEqual(self.parser.session.get.call_count, 3)
        self.assertEqual(self.sleep.call_args_list, [call(10), call(20)])
        self.assertEqual((self.contest / "A" / "1.in").read_text(), "3 4\n")

    def test_retry_after_seconds_and_http_date_are_respected(self):
        now = 1700000000
        for retry_after in ("90", formatdate(now + 90, usegmt=True)):
            with self.subTest(retry_after=retry_after):
                limited = response("", 429)
                limited.headers["Retry-After"] = retry_after
                self.parser.session.get.side_effect = [limited, response(SAMPLES)]
                self.sleep.reset_mock()
                with patch.object(parse.time, "time", return_value=now):
                    self.parser.parseProblem("A", "https://atcoder.jp/contests/abc483/tasks/abc483_a")
                self.sleep.assert_called_once_with(90)

    def test_invalid_retry_after_uses_default_delay(self):
        limited = response("", 429)
        limited.headers["Retry-After"] = "invalid"
        self.parser.session.get.side_effect = [limited, response(SAMPLES)]
        self.parser.parseProblem("A", "https://atcoder.jp/contests/abc483/tasks/abc483_a")
        self.sleep.assert_called_once_with(10)

    def test_repeated_rate_limit_stops_after_five_retries(self):
        self.parser.session.get.return_value = response("", 429)
        with self.assertRaises(requests.HTTPError):
            self.parser.parseProblem("A", "https://atcoder.jp/contests/abc483/tasks/abc483_a")
        self.assertEqual(self.parser.session.get.call_count, 6)
        self.assertEqual(self.sleep.call_args_list, [call(10), call(20), call(40), call(60), call(60)])

    def test_contest_list_rate_limit_is_retried(self):
        self.parser.contestURL = "https://atcoder.jp/contests/abc483/tasks"
        self.parser.session.get.side_effect = [response("", 429), response(TASKS)]
        self.assertEqual(len(self.parser.fetch_problems()), 2)
        self.sleep.assert_called_once_with(10)

    def test_forbidden_response_is_not_retried(self):
        self.parser.session.get.return_value = response("", 403)
        with self.assertRaises(requests.HTTPError):
            self.parser.parseProblem("A", "https://atcoder.jp/contests/abc483/tasks/abc483_a")
        self.assertEqual(self.parser.session.get.call_count, 1)
        self.sleep.assert_not_called()

    def test_http_error_stops_instead_of_retrying_forever(self):
        self.parser.session.get.side_effect = lambda url, **kwargs: response(TASKS if url.endswith('/tasks') else '<html>Missing</html>', 200 if url.endswith('/tasks') else 404)
        with self.assertRaises(requests.HTTPError):
            self.fetch_samples()
        self.assertLessEqual(self.parser.session.get.call_count, 3)

    def test_missing_samples_is_reported_as_failure(self):
        self.parser.session.get.side_effect = lambda url, **kwargs: response(TASKS if url.endswith('/tasks') else '<html>No samples</html>')
        with self.assertRaisesRegex(ValueError, 'sample'):
            self.fetch_samples()

    def test_restricted_contest_requires_credentials(self):
        login_page = response("<html>Login</html>")
        login_page.url = "https://atcoder.jp/login?continue=contest"
        self.parser.session.get.return_value = login_page
        self.parser.username = self.parser.password = ""
        with self.assertRaisesRegex(ValueError, "requires ATCODER_USERNAME"):
            self.fetch_samples()

    def test_login_is_only_used_after_a_login_redirect(self):
        login_page = response("<html>Login</html>")
        login_page.url = "https://atcoder.jp/login?continue=contest"
        self.parser.session.get.return_value = login_page
        self.parser.username, self.parser.password = "test user", "test password"
        authenticated_session = Mock()
        authenticated_session.get.side_effect = lambda url, **kwargs: response(TASKS if url.endswith('/tasks') else SAMPLES)
        with patch.object(self.parser, "login", return_value=authenticated_session) as login:
            self.fetch_samples()
        login.assert_called_once_with()
        self.assertEqual((self.contest / "C" / "2.out").read_text(), "Odd\n")


if __name__ == "__main__":
    unittest.main()

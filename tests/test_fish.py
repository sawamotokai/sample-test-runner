import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FISH = shutil.which("fish")
VARIABLES = (
    "ATCODER_USERNAME", "ATCODER_PASSWORD", "CODEFORCES_USERNAME",
    "CODEFORCES_PASSWORD", "SAMPLE_TEST_RUNNER_ROOT", "XDG_STATE_HOME", "CXX",
)


@unittest.skipUnless(FISH, "fish is not installed")
class FishIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory(prefix="fish runner ")
        self.addCleanup(self.workspace.cleanup)
        self.directory = Path(self.workspace.name)
        self.bin_directory = self.directory / "bin"
        self.bin_directory.mkdir()
        (self.bin_directory / "cprun").symlink_to(ROOT / "src" / "cprun")
        self.state_directory = self.directory / "state"
        self.contest = self.directory / "contest with spaces"
        self.contest.mkdir()
        self.state_file = self.state_directory / "sample-test-runner" / "workspace"
        self.state_file.parent.mkdir(parents=True)
        self.environment = os.environ.copy()
        for name in VARIABLES:
            self.environment.pop(name, None)
        self.environment.update({
            "TEST_INTEGRATION": str(ROOT / "integrations/fish/sample-test-runner.fish"),
            "TEST_BIN": str(self.bin_directory),
            "TEST_STATE": str(self.state_directory),
            "TEST_CONTEST": str(self.contest),
            "TEST_ROOT": str(ROOT),
        })

    def executable(self, name, content):
        path = self.bin_directory / name
        path.write_text(content)
        path.chmod(0o755)
        return path

    def fish(self, script):
        return subprocess.run(
            [FISH, "--no-config", "-c", 'source "$TEST_INTEGRATION"\n'
             'set -gx PATH "$TEST_BIN" $PATH\n' + script],
            cwd=self.directory, env=self.environment,
            capture_output=True, text=True, timeout=30,
        )

    def test_cpget_forwards_unexported_settings_and_enters_workspace(self):
        self.executable("cpget", '''#!/usr/bin/env python3
import os
import sys
from pathlib import Path
expected = {
    "ATCODER_USERNAME": "test user", "ATCODER_PASSWORD": "test password $;!",
    "CODEFORCES_USERNAME": "test cf user", "CODEFORCES_PASSWORD": "test cf password",
    "SAMPLE_TEST_RUNNER_ROOT": os.environ["TEST_CONTEST"],
    "XDG_STATE_HOME": os.environ["TEST_STATE"],
}
for name, value in expected.items():
    if os.environ.get(name) != value:
        sys.exit("Setting was not forwarded: " + name)
assert sys.argv[1:] == ["argument with spaces"]
state = Path(os.environ["XDG_STATE_HOME"]) / "sample-test-runner" / "workspace"
state.write_text(os.environ["SAMPLE_TEST_RUNNER_ROOT"])
''')
        result = self.fish('''
set -gu ATCODER_USERNAME 'test user'
set -gu ATCODER_PASSWORD 'test password $;!'
set -gu CODEFORCES_USERNAME 'test cf user'
set -gu CODEFORCES_PASSWORD 'test cf password'
set -gu SAMPLE_TEST_RUNNER_ROOT "$TEST_CONTEST"
set -gu XDG_STATE_HOME "$TEST_STATE"
cpget 'argument with spaces'; or exit $status
test "$PWD" = "$TEST_CONTEST"; or exit 90
for name in ATCODER_USERNAME ATCODER_PASSWORD CODEFORCES_USERNAME CODEFORCES_PASSWORD SAMPLE_TEST_RUNNER_ROOT XDG_STATE_HOME
    if set -qx $name
        echo "Setting remained exported: $name" >&2
        exit 91
    end
end
''')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_cpget_failure_preserves_status_and_does_not_enter_stale_workspace(self):
        self.state_file.write_text(str(self.contest))
        self.executable("cpget", "#!/bin/sh\nexit 23\n")
        result = self.fish('''
set -gx XDG_STATE_HOME "$TEST_STATE"
set -l original_directory "$PWD"
cpget
set -l result $status
test "$PWD" = "$original_directory"; or exit 90
exit $result
''')
        self.assertEqual(result.returncode, 23, result.stdout + result.stderr)

    def test_cpget_preserves_exported_credentials(self):
        self.executable("cpget", '''#!/usr/bin/env python3
import os
import sys
sys.exit(0 if os.environ.get("ATCODER_PASSWORD") == "exported password" else 91)
''')
        result = self.fish('''
set -gx ATCODER_PASSWORD 'exported password'
set -gx XDG_STATE_HOME "$TEST_STATE"
cpget; or exit $status
set -qx ATCODER_PASSWORD; or exit 92
''')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_cprun_uses_unexported_compiler_override(self):
        source = self.contest / "solution.cpp"
        source.write_text('int main() {}\n')
        (self.contest / "1.in").write_text("")
        (self.contest / "1.out").write_text("")
        compiler = self.executable("test compiler", '#!/bin/sh\necho "test compiler selected" >&2\nexit 37\n')
        self.environment["TEST_COMPILER"] = str(compiler)
        result = self.fish('''
set -gu CXX "$TEST_COMPILER"
cprun "$TEST_CONTEST/solution.cpp"
set -l result $status
if set -qx CXX
    exit 91
end
exit $result
''')
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("test compiler selected", result.stderr)
        self.assertIn("Compilation Error", result.stdout)

    def test_cprun_forwards_arguments_and_compiles_solution(self):
        (self.contest / "solution.cpp").write_text(
            '#include <iostream>\nint main(){int n;std::cin>>n;std::cout<<n*2<<"\\n";}\n'
        )
        (self.contest / "1.in").write_text("21\n")
        (self.contest / "1.out").write_text("42\n")
        result = self.fish('cprun "$TEST_CONTEST/solution.cpp"')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Passed [1/1] tests", result.stdout)


if __name__ == "__main__":
    unittest.main()

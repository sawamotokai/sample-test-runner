import os
import sys
import time
import requests
import concurrent.futures
import re
from datetime import timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from bs4 import BeautifulSoup
from colorama import Fore, init
import inquirer
from inquirer.themes import GreenPassion

init()

class ParserFactory(object):
    @staticmethod
    def get():
        ac = "AtCoder"
        cf = "CodeForces"
        website = Ask.list_input(
            message="Which website?",
            choices=[ac,cf])
        if website == ac:
            return AtCoderParser(atcoder_username, atcoder_password)
        elif website == cf:
            if codeforces_password == "" or codeforces_username == "":
                raise Exception("Environment variables are not set properly.\n"
                + "Make sure to set CODEFORCES_USERNAME and CODEFORCES_PASSWORD environment variables.")
            return CodeForcesParser(codeforces_username, codeforces_password)
        else:
            raise Exception("Ilegal Input")

class Parser(object):
    def __init__(self):
        super().__init__()

    def parse(self):
        raise Exception("This method has to be overridden.")

    def login(self):
        raise Exception("This method has to be overridden.")

class AtCoderParser(Parser):
    def  __init__(self, username, password):
        super().__init__()
        self.folderName = None
        self.username = username
        self.password = password
        self.session = requests.Session()

    def fetch_page(self, url, session=None):
        client = self.session if session is None else session
        retry_limit = 5
        for attempt in range(retry_limit + 1):
            page = client.get(url, timeout=30)
            if page.status_code != 429 or attempt == retry_limit:
                page.raise_for_status()
                return page

            delay = min(10 * 2 ** attempt, 60)
            retry_after = page.headers.get("Retry-After", "").strip()
            if retry_after:
                try:
                    if retry_after.isdigit():
                        server_delay = int(retry_after)
                    else:
                        retry_at = parsedate_to_datetime(retry_after)
                        if retry_at.tzinfo is None:
                            retry_at = retry_at.replace(tzinfo=timezone.utc)
                        server_delay = retry_at.timestamp() - time.time()
                    delay = max(delay, server_delay)
                except (TypeError, ValueError, OverflowError):
                    pass
            print(
                f"HTTP 429: retry {attempt + 1}/{retry_limit} in {delay:g}s: {url}",
                file=sys.stderr, flush=True,
            )
            time.sleep(delay)

    # returns a logged in session
    def login(self):
        URL = 'https://atcoder.jp/login?continue=https%3A%2F%2Fatcoder.jp%2F'
        client = requests.Session()
        r1 = self.fetch_page(URL, session=client)
        soup = BeautifulSoup(r1.content, features="lxml")
        t = soup.find('input', {'name': 'csrf_token'})
        if t is None:
            raise ValueError("AtCoder login is unavailable: no CSRF token in the login page")
        csrf_token = t.get('value')
        payload = {
            'username': self.username,
            'password': self.password,
            'csrf_token': csrf_token
        }
        result = client.post(URL, data=payload, headers={'referer': URL}, timeout=30)
        result.raise_for_status()
        if urlsplit(result.url).path == "/login":
            raise ValueError("AtCoder login failed; check your credentials or log in through a browser")
        return client

    def parseProblem(self, label, problem_url):
        page = self.fetch_page(problem_url)
        soup = BeautifulSoup(page.content, features="lxml")
        language = soup.select_one(".lang-en") or soup.select_one(".lang-ja") or soup
        inputs, outputs = {}, {}
        for section in language.select("section"):
            heading, sample = section.find("h3"), section.find("pre")
            if heading is None or sample is None:
                continue
            title = heading.get_text(" ", strip=True)
            input_match = re.fullmatch(r"(?:Sample Input|入力例)\s*(\d+)", title, re.IGNORECASE)
            output_match = re.fullmatch(r"(?:Sample Output|出力例)\s*(\d+)", title, re.IGNORECASE)
            match = input_match or output_match
            if match:
                samples = inputs if input_match else outputs
                samples[int(match.group(1))] = sample.get_text().replace("\r\n", "\n")
        if not inputs or inputs.keys() != outputs.keys():
            raise ValueError(f"Missing or mismatched samples for {label}: {problem_url}")

        directory = Path(self.folderName) / label
        directory.mkdir(parents=True, exist_ok=True)
        for number in sorted(inputs):
            for extension, samples in (("in", inputs), ("out", outputs)):
                content = samples[number]
                if not content.endswith("\n"):
                    content += "\n"
                (directory / f"{number}.{extension}").write_text(content)
        touch(str(directory / f"{label}.{solutionLangExtension}"))
        print(Fore.WHITE + f"parsing {label}" + Fore.GREEN + "  [Success]  " + Fore.WHITE)

    def parse(self):
        abc = "ABC"
        arc = "ARC"
        agc = "AGC"
        contest = Ask.list_input(
            message = "Which contest?",
            choices=[abc, arc, agc]
        ).lower()
        code = Ask.text(message="Contest Code") 
        while len(code) < 3:
            code = '0' + code
        try:
            int(code)
            self.contestName = f"{contest}{code}"
        except:
            self.contestName = code
        self.contestURL = f"https://atcoder.jp/contests/{self.contestName}/tasks"
        self.folderName = f"{rootPath}/{atCoder}/{contest.upper()}/{code}"
        problems = self.fetch_problems()
        # Concurrent downloads keep hitting the rate limit while another request backs off.
        for label, url in problems:
            time.sleep(2)
            self.parseProblem(label, url)

    def fetch_problems(self):
        page = self.fetch_page(self.contestURL)
        if urlsplit(page.url or "").path == "/login":
            if not self.username or not self.password:
                raise ValueError("This contest requires ATCODER_USERNAME and ATCODER_PASSWORD")
            self.session = self.login()
            page = self.fetch_page(self.contestURL)
        soup = BeautifulSoup(page.content, features="lxml")
        problems = [
            (link.get_text(strip=True).upper(), urljoin(self.contestURL, link["href"]))
            for link in soup.select("table tbody tr td:first-child a[href]")
        ]
        if not problems:
            raise ValueError(f"No problems found: {self.contestURL}")
        print(Fore.GREEN + "Connected!\n" + Fore.WHITE)
        return problems


class CodeForcesParser(Parser):
    def  __init__(self, username, password):
        super().__init__()
        self.code = 0
        self.folderName = None
        self.username = username
        self.password = password
        self.session = self.login()

    def parseProblem(self, c):
        try:
            url = f"{codeForcesURL}{str(self.code)}/problem/{str(c)}"
            self.folderName = f"{rootPath}/{codeForces}/{self.code}"
            page = self.session.get(url)
            soup = BeautifulSoup(page.content, features="lxml")
            PRE = soup.find_all("pre")
            L = len(PRE)
            inde = 1
            skipped = 0
            for i in range(L):
                classAttr = PRE[i].parent.get("class")
                if classAttr is None or "note" in classAttr:
                    skipped += 1
                    continue
                elif i % 2 == skipped % 2:
                    In = str(PRE[i])
                    In = In.replace("<pre>", "").replace("</pre>", "")
                    In = In.replace("&gt;", ">")
                    In = In.replace("&lt;", "<")
                    In = In.replace("&quot;", '"')
                    In = In.replace("&amp;", "&")
                    In = In.replace("<br />", "\n")
                    In = In.replace("<br/>", "\n")
                    In = In.replace("</ br>", "\n")
                    In = In.replace("</br>", "\n")
                    In = In.replace("<br>", "\n")
                    In = In.replace("< br>", "\n")
                    In = In.split("\n")
                    filename = f"{self.folderName}/{str(c)}/{str(inde)}.in"
                    writeFile(In, filename)
                else:
                    Out = str(PRE[i])
                    Out = Out.replace("<pre>", "").replace("</pre>", "")
                    Out = Out.replace("&gt;", ">")
                    Out = Out.replace("&lt;", "<")
                    Out = Out.replace("&quot;", '"')
                    Out = Out.replace("&amp;", "&")
                    Out = Out.replace("<br />", "\n")
                    Out = Out.replace("<br/>", "\n")
                    Out = Out.replace("</ br>", "\n")
                    Out = Out.replace("<br>", "\n")
                    Out = Out.split("\n")
                    
                    filename = f"{self.folderName}/{str(c)}/{str(inde)}.out"
                    writeFile(Out, filename)
                    inde += 1
            touch(f"{self.folderName}/{str(c)}/{str(c).upper()}.{solutionLangExtension}")
            print(
                (Fore.WHITE + "parsing " + str(c))
                + (Fore.GREEN + "  [Success]  ")
                + (Fore.WHITE + "")

            )
        except:
            print(
                (Fore.WHITE + "parsing " + str(c))
                + (Fore.RED + "  [Error]  ")
                + (Fore.WHITE + "")
            )
            print("Retrying parsing " + str(c))
            self.parseProblem(c)

    def login(self):
        URL = 'https://codeforces.com/enter?back=%2F'
        client = requests.Session()
        r1 = client.get(URL)
        soup = BeautifulSoup(r1.content, features="lxml")
        t = soup.find('input', {'name': 'csrf_token'})
        csrf_token = t.get('value')
        payload = {
            'handleOrEmail': self.username,
            'password': self.password,
            'csrf_token': csrf_token,
            'action': 'enter',
        }
        headers = {
            'referer': URL,
        }
        client.post(URL, data=payload, headers=headers)
        return client

    def parse(self):
        self.code = int(Ask.text(message="Contest Code"))
        while True:
            url = codeForcesURL + str(self.code)
            page = self.session.get(url)
            soup = BeautifulSoup(page.content, features="lxml")
            sz = soup.find_all(title="Submit")
            if len(sz) == 0:
                print((Fore.RED + "Failed to connect!"))
                print(Fore.WHITE + "Trying again...")
                time.sleep(1)
                continue

            ch = []
            for p in soup.find_all("td", attrs={"class": "id"}):
                for s in p.find("a").stripped_strings:
                    ch.append(s)
            break
            

        print(Fore.GREEN + "Connected!" + Fore.WHITE + "")
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = {executor.submit(self.parseProblem, c) for c in ch}
         
##############################################################
## CONFIG ####################################################

## User
atcoder_username = os.getenv('ATCODER_USERNAME', default="")
atcoder_password = os.getenv('ATCODER_PASSWORD', default="")
codeforces_username = os.getenv('CODEFORCES_USERNAME', default="")
codeforces_password = os.getenv('CODEFORCES_PASSWORD', default="")

## path constants i.e., {rootPath}/{atCoder}/<ABC | ARC | AGC>/<contest code>
rootPath = os.path.expanduser(os.getenv("SAMPLE_TEST_RUNNER_ROOT", "~/workspace/competitive-programming"))
atCoder = 'AtCoder'
atCoder_abc = 'ABC'
atCoder_arc = 'ARC'
atCoder_agc = 'AGC'

codeForces = 'codeForces'

## URL constants
atCoderURL = "https://atcoder.jp/"
codeForcesURL = "https://www.codeforces.com/contest/"

## Misc
solutionLangExtension = 'cpp'

## END CONFIG ################################################
##############################################################

##############################################################
## UTIL ######################################################

def writeFile(data, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        rows = []
        for d in data:
            for t in d.split("\n"):
                rows.append(t.strip())
        for row in rows:
            if row != "" and row != " ":
                f.write(row + "\n")

def touch(fname):
    try:
        os.utime(fname, None)
    except OSError as e:
        open(fname, 'a').close()

class Ask():
    @staticmethod
    def text(message):
        answers = inquirer.prompt(
            questions=[
                inquirer.Text('ans',
                message=message)],
            theme=GreenPassion())
        if answers is None:
            raise KeyboardInterrupt
        return answers['ans']

    @staticmethod
    def list_input(message, choices):
        answers = inquirer.prompt(
            questions=[
                inquirer.List('ans',
                message=message,
                choices=choices)],
            theme=GreenPassion())
        if answers is None:
            raise KeyboardInterrupt
        return answers['ans']

## END UTIL ##################################################
##############################################################

if __name__ == '__main__':
    try:
        parser = ParserFactory.get()
        parser.parse()
        dirPath = os.path.join(os.getenv("XDG_STATE_HOME", os.path.expanduser("~/.local/state")), "sample-test-runner", "workspace")
        print(f"Workspace has been created under {parser.folderName}")
        os.makedirs(os.path.dirname(dirPath), exist_ok=True)
        with open(dirPath, 'w') as f:
            f.write(parser.folderName)
    except KeyboardInterrupt:
        sys.exit(130)
    except (requests.RequestException, ValueError) as error:
        print(f"Sample download failed: {error}", file=sys.stderr)
        sys.exit(1)

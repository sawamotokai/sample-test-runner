import os
import time
import requests
import concurrent.futures
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
        self.session = self.login()

    # returns a logged in session
    def login(self):
        URL = 'https://atcoder.jp/login?continue=https%3A%2F%2Fatcoder.jp%2F'
        client = requests.Session()
        r1 = client.get(URL)
        soup = BeautifulSoup(r1.content, features="lxml")
        t = soup.find('input', {'name': 'csrf_token'})
        csrf_token = t.get('value')
        csrf = client.cookies.get_dict()['REVEL_SESSION']
        payload = {
            'username': self.username,
            'password': self.password,
            'csrf_token': csrf_token
        }
        headers = {
            'referer': URL,
            'REVEL_SESSION': csrf,
            'X-XSRF-token': csrf
        }
        client.post(URL, data=payload, headers=headers)
        return client

    def parseProblem(self, problemChar):
        try:
            problemURL = f"{self.contestURL}/{self.contestName}_{problemChar}"
            page = self.session.get(problemURL)
            soup = BeautifulSoup(page.content, features="lxml")
            rows = list(filter(lambda tag: tag.contents[0].name != "var", soup.findAll("pre")))
            rows = rows[:len(rows) // 2]
            rows = [tag.text.split("\r\n") for tag in rows]
            for i in range(len(rows) // 2):
                filename = f"{self.folderName}/{problemChar.upper()}/{i+1}.in"
                writeFile(rows[i*2], filename)
                filename = f"{self.folderName}/{problemChar.upper()}/{i+1}.out"
                writeFile(rows[i*2+1], filename)
            touch(f"{self.folderName}/{problemChar.upper()}/main.{solutionLangExtension}")
            print(
                (Fore.WHITE + "parsing " + str(problemChar))
                + (Fore.GREEN + "  [Success]  ")
                + (Fore.WHITE + "")
            )
        except:
            print(
                (Fore.WHITE + "parsing " + str(problemChar))
                + (Fore.RED + "  [Error]  ")
                + (Fore.WHITE + "")
            )

    
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
        numProblems = self.getNumberOfProblems(self.contestURL)
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            for i in range(numProblems):
                problemChar= chr(ord('a') + i)
                try: # if enterprise contests, code is not integer
                    # old contests have different problem IDs
                    if (contest == abc.lower() and int(code) < 20) or (contest == arc.lower() and int(code) < 35):
                        problemChar = i + 1
                    # old ARC starts from problem c
                    if contest == arc.lower() and int(code) <= 113 and int(code) >= 58:
                        problemChar= chr(ord('a') + i + 2)
                except:
                    pass
                executor.submit(self.parseProblem, problemChar)

    def getNumberOfProblems(self, URL):
        while True:
            page = self.session.get(URL)
            soup = BeautifulSoup(page.content, features="lxml")
            rows = soup.findAll("tr")
            ln = len(rows)
            if ln == 0:
                print((Fore.RED + "Failed to connect!"))
                print(Fore.WHITE + "Trying again...")
                time.sleep(1)
                continue
            print(Fore.GREEN + "Connected!\n")
            return ln - 1 # subtract the title row

        

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
            PRE = soup.findAll("pre")
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
            touch(f"{self.folderName}/{str(c)}/main.{solutionLangExtension}")
            print(
                (Fore.WHITE + "parsing " + str(c))
                + (Fore.GREEN + "  [Success]  ")
                + (Fore.WHITE + "")

            )
        except:
            print(
                (Fore.WHITE + "parsing " + str(problemChar))
                + (Fore.RED + "  [Error]  ")
                + (Fore.WHITE + "")
            )

    def login(self):
        URL = 'https://codeforces.com/enter?back=%2F'
        client = requests.Session()
        r1 = client.get(URL)
        soup = BeautifulSoup(r1.content, features="lxml")
        t = soup.find('input', {'name': 'csrf_token'})
        csrf_token = t.get('value')
        print(csrf_token)
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
            sz = soup.findAll(title="Submit")
            if len(sz) == 0:
                print((Fore.RED + "Failed to connect!"))
                print(Fore.WHITE + "Trying again...")
                time.sleep(1)
                continue

            ch = []
            for p in soup.findAll("td", attrs={"class": "id"}):
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
rootPath = f"{os.environ['HOME']}/workspace/competitive-programming"
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
        for _row in data:
            row = _row.replace("\n", "")
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
        return inquirer.prompt(
            questions=[
                inquirer.Text('ans',
                message=message)],
            theme=GreenPassion())['ans']

    @staticmethod
    def list_input(message, choices):
        return inquirer.prompt(
            questions=[
                inquirer.List('ans',
                message=message,
                choices=choices)],
            theme=GreenPassion())['ans']

## END UTIL ##################################################
##############################################################

if __name__ == '__main__':
    parser = ParserFactory.get()
    parser.parse()
    dirPath=f"/tmp/sample-test-runner-pwd.txt"
    print(f"Workspace has been created under {parser.folderName}")
    os.makedirs(os.path.dirname(dirPath), exist_ok=True)
    with open(dirPath, 'w') as f:
        f.write(parser.folderName)


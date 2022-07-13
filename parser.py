# parse.py 'sukeesh'
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
import urllib3
import os
import concurrent.futures
from os.path import expanduser
from colorama import Fore, Back, Style, init
import inquirer
from inquirer.themes import GreenPassion

from utils import *
from config import *

#TODO organize import

home = expanduser("~")
PWD = os.getcwd()
http = urllib3.PoolManager()
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
            return AtCoderParser()
        elif website == cf:
            return CodeForcesParser()
        else:
            raise Exception("Ilegal Input")

class Parser(object):
    def __init__(self):
        super().__init__()

    def parse(self):
        raise Exception("This method has to be overridden.")

class AtCoderParser(Parser):
    def  __init__(self):
        super().__init__()
        self.folderName = None

    def parseProblem(self, problemChar):
        try:
            problemURL = f"{self.contestURL}/{self.contestName}_{problemChar}"
            page = http.request("Get", problemURL)
            soup = BeautifulSoup(page.data, features="lxml")
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
        page = http.request("Get", URL)
        soup = BeautifulSoup(page.data, features="lxml")
        rows = soup.findAll("tr")
        ln = len(rows)
        if ln == 0:
            raise Exception("Failed getting the number of problems")
        print(Fore.GREEN + "Connected!\n")
        return ln - 1 # subtract the title row

        

class CodeForcesParser(Parser):
    def  __init__(self):
        super().__init__()
        self.code = 0
        self.folderName = f"{rootPath}/{codeForces}"

    def parseProblem(self, c):
        try:
            url = f"{codeForcesURL}{str(self.code)}/problem/{str(c)}"
            page = http.request("Get", url)
            soup = BeautifulSoup(page.data, features="lxml")
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
                    filename = f"{self.folderName}/{self.code}/{str(c)}/{str(inde)}.in"
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
                    
                    filename = f"{self.folderName}/{self.code}/{str(c)}/{str(inde)}.out"
                    writeFile(Out, filename)
                    inde += 1
            touch(f"{self.folderName}/{self.code}/{str(c)}/main.{solutionLangExtension}")
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


    def parse(self):
        self.code = int(Ask.text(message="Contest Code"))
        url = codeForcesURL + str(self.code)
        http.request("Get", url)
        page = http.request("Get", url)
        soup = BeautifulSoup(page.data, features="lxml")
        sz = soup.findAll(title="Submit")

        ch = []
        for p in soup.findAll("td", attrs={"class": "id"}):
            for s in p.find("a").stripped_strings:
                ch.append(s)

        print(Fore.GREEN + "Connected!\n")
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = {executor.submit(self.parseProblem, c) for c in ch}
        os.chdir(f"{self.folderName}/{self.code}")
         

if __name__ == '__main__':
    parser = ParserFactory.get()
    parser.parse()

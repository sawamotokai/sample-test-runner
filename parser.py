# parse.py 'sukeesh'
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
import urllib3
import subprocess
import os
import sys
import concurrent.futures
import urllib.request
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
            message="Which contest website?",
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

    def parseProblem(self, problemChar):
        problemURL = f"{self.contestURL}/{self.contest}{self.code}_{problemChar}"
        print(problemURL)
        print(
            (Fore.WHITE + "parsing " + str(problemChar))
            + (Fore.GREEN + "  [Success]  ")
            + (Fore.WHITE + "")
        )

    
    def parse(self):
        abc = "ABC"
        arc = "ARC"
        agc = "AGC"
        self.contest = Ask.list_input(
            message = "Which contest?",
            choices=[abc, arc, agc]
        ).lower()
        self.code = Ask.text(message="Contest Code") 
        self.contestURL = f"https://atcoder.jp/contests/{self.contest}{self.code}/tasks"

        # TODO: 
        numProblems = 8
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            for i in range(numProblems):
                problemChar= chr(ord('a') + i)
                executor.submit(self.parseProblem, problemChar)
        pass

class CodeForcesParser(Parser):
    def  __init__(self):
        super().__init__()
        self.code = 0

    def parseProblem(self, c):
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
                filename = f"{PWD}/{str(c)}/{str(inde)}.in"
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
                filename = f"{PWD}/{str(c)}/{str(inde)}.out"
                writeFile(Out, filename)
                inde += 1
        print(
            (Fore.WHITE + "parsing " + str(c))
            + (Fore.GREEN + "  [Success]  ")
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

        print("   Connected!\n")
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = {executor.submit(self.parseProblem, c) for c in ch}
         

parser = ParserFactory.get()
parser.parse()

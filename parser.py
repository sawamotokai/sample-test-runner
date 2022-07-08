# parse.py 'sukeesh'
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
import urllib3
import subprocess
import os
import sys
from os.path import expanduser
from colorama import init
from colorama import Fore, Back, Style

from utils import *
from config import *

#TODO organize import

home = expanduser("~")
PWD = os.getcwd()

class ParserFactory(object):
    @staticmethod
    def get(website):
        if website == "atcoder":
            return AtCoderParser()
        elif website == "codeforces":
            return CodeForcesParser()
        else:
            raise Exception("Ilegal Input")


class Parser(object):
    def __init__(self):
        super().__init__()

    def parse(self):
        pass

class AtCoderParser(Parser):
    def  __init__(self):
        super().__init__()
    

class CodeForcesParser(Parser):
    def  __init__(self):
        super().__init__()

    def parse(self):
        code = int(input("Contest code XXX: "))

        http = urllib3.PoolManager()

        url = codeForcesURL + str(code)
        http.request("Get", url)
        page = http.request("Get", url)
        soup = BeautifulSoup(page.data, features="lxml")
        sz = soup.findAll(title="Submit")

        url2 = "/problem/"
        ch = []
        chtest = []
        for p in soup.findAll("td", attrs={"class": "id"}):
            for s in p.find("a").stripped_strings:
                ch.append(s)
                chtest.append(0)

        jj = 0
        print("   Connected!\n")
        while jj < len(sz):
            url = f"{codeForcesURL}{str(code)}{url2}{str(ch[jj])}"
            page = http.request("Get", url)
            soup = BeautifulSoup(page.data, features="lxml")
            PRE = soup.findAll("pre")
            L = len(PRE)
            inde = 1
            for i in range(L):
                classAttr = PRE[i].parent.get("class")
                if classAttr is None or "note" in classAttr:
                    break
                elif i % 2 == 0:
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
                    filename = f"{PWD}/{str(ch[jj])}/{str(inde)}.in"
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
                    filename = f"{PWD}/{str(ch[jj])}/{str(inde)}.out"
                    writeFile(Out, filename)
                    inde += 1
                    chtest[jj] += 1

            print(
                (Fore.WHITE + "parsing " + str(ch[jj]))
                + (Fore.GREEN + "  [Success]  ")
                + (Fore.WHITE + "")
            )
            jj = jj + 1

        f = open(f'{PWD}/random.txt', "w")
        f.write(str(code) + "\n")
        jj = 0
        while jj < len(sz):
            f.write(str(ch[jj]) + " " + str(chtest[jj]) + "\n")
            jj = jj + 1
        f.close()


website = "codeforces"
parser = ParserFactory.get(website)
parser.parse()

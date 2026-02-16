"""Customize everything, but nothing more."""



from AST_generator import generate_AST
from utils import get_input

from os.path import abspath, exists
from os import remove
from time import time
from sys import argv



if '-x' in argv:
    exists("AST.py") and remove("AST.py")
    exists("eval.py") and remove("eval.py")
    quit()

iFlag = "-i" in argv 
iFlag and argv.remove("-i")

dFlag = "-d" in argv 
dFlag and argv.remove("-d")

vFlag = "-v" in argv 
vFlag and argv.remove("-v")

if len(argv) == 1:
    print("Language folder not found.")
    quit()

print()
generate_AST(abspath(argv[1]))
print()

from parser import parse
from eval import evaluate

for arg in argv:
    if arg.endswith(".banter"):
        with open(arg) as file:
            for line in file.readlines():
                out = evaluate(parse(line).AST)
                if out: print(out)

if iFlag:
    for line in iter(lambda: get_input("</> "), "quit"):
        if dFlag: start = time()
        if vFlag:
            print(evaluate(parse(line).AST))
        else:
            print(parse(line))
        if dFlag: print(f"Runtime: {time() - start}")

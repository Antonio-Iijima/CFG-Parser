"""Customize everything, but nothing more."""



from AST_generator import generate_AST

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

if len(argv) == 1:
    print("Language folder not found.")
    quit()

print()
generate_AST(abspath(argv[1]))
print()

from parser import parse
from eval import evaluate

if iFlag:
    for line in iter(lambda: input("> "), "quit"):
        if dFlag: start = time()
        print(evaluate(parse(line).AST))
        if dFlag: print(f"Runtime: {time() - start}")

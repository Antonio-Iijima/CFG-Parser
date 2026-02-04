from AST_generator import generate_AST
from utils import preprocess_text

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

language = abspath(argv[1])

with open(f"{language}/syntax.txt") as text: 
    print()
    generate_AST(
        syntax=preprocess_text(text.read().splitlines()),
        semantics=f"{language}/semantics.py",
        debug=dFlag
    )
    print()

from parser import parse
from eval import evaluate

if iFlag:
    for line in iter(lambda: input("> "), "quit"):
        if dFlag: start = time()
        print(evaluate(parse(line)))
        if dFlag: print(f"Runtime: {time() - start}")

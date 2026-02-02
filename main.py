from AST_generator import generate_AST
from utils import preprocess_text

from os.path import abspath, exists
from os import listdir, remove
from time import time
from sys import argv



if '-x' in argv:
    exists("parser.py") and remove("parser.py")
    exists("eval.py") and remove("eval.py")
    quit()

iFlag = "-i" in argv 
iFlag and argv.remove("-i")

dFlag = "-d" in argv 
dFlag and argv.remove("-d")

if len(argv) > 1:
    path = abspath(argv[0])
    language = abspath(argv[1])
    for file in (s for s in listdir(language) if not s.startswith("__")):
        path = f"{language}/{file}"
        match file:
            case "semantics.py":
                SEMANTICS = path
            case "syntax.txt":
                with open(path) as text: 
                    SYNTAX = preprocess_text(text.read().splitlines())
            case _:
                print(f"Unrecognized file: {path}")
else:
    print("Language folder not found.")
    quit()

print()
generate_AST(
    syntax=SYNTAX,
    semantics=SEMANTICS,
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

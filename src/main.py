"""Customize everything, but nothing more."""



from AST_generator import generate_AST
from utils import get_input

from os.path import abspath, exists
from sys import exit, argv
from time import time
from os import remove



# Remove generated files
if '-x' in argv:
    exists("AST.py") and remove("AST.py")
    exists("eval.py") and remove("eval.py")
    exit()

# Interactive
iFlag = "-i" in argv 
iFlag and argv.remove("-i")

# Debug
dFlag = "-d" in argv 
dFlag and argv.remove("-d")

# Test
tFlag = "-t" in argv
tFlag and argv.remove("-t")

# Compile
cFlag = "-c" in argv
cFlag and argv.remove("-c")

if __name__ == "__main__":
    argv = argv[1:]

    if cFlag: 
        LANGUAGE = abspath(argv.pop(0))
        print()
        generate_AST(LANGUAGE)
        print()
    
    else:
        from AST import LANGUAGE
    
        print(f"Using compiled language: {LANGUAGE.rsplit("/")[-1]}.")


    if tFlag:
        from tests import test
    
        test(LANGUAGE.rsplit("/")[-1], argv)
    
    from eval import process
    
    for arg in argv:
        if exists(arg):
            with open(arg) as file:
                process(file.read(), dFlag=dFlag)

    if iFlag:
        for line in iter(lambda: get_input("</> "), "quit"):
            if dFlag: start = time()
            process(line, dFlag)
            if dFlag: print(f"Runtime: {time() - start}")

"""Customize everything, but nothing more."""



from AST_generator import generate_AST
from utils import get_input

from os.path import abspath, exists
# from rich import print
from os import remove
from time import time
from sys import argv


if __name__ == "__main__": argv.pop(0)

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

tFlag = "-t" in argv
tFlag and argv.remove("-t")

cFlag = "-c" in argv
cFlag and argv.remove("-c")

if __name__ == "__main__":
    if cFlag: 
        LANGUAGE = abspath(argv.pop(0))
        print()
        generate_AST(LANGUAGE)
        print()
    else:
        from AST import LANGUAGE
        print(f"Using compiled language: {LANGUAGE.rsplit("/")[-1]}.")

    from parser import parse
    from eval import interpret

    if tFlag:
        from parser import validate

        while argv:
            match LANGUAGE.split("/")[-1] + argv.pop(0):
                case "calculator1":
                    tests = [
                        ("123", 123),
                        ("1 + 2 + 3", 6),
                        ("8 ** 2", 64),
                        ("(2 + 3) * 5", 25),
                        ("10 - (3 - 2)", 9),
                        ("10 - 3 - 2", 5), 
                        ("1 + -12", -11),
                        ("1 + - 12", -11),
                        ("--12", 12),
                        ("|-26|", 26),
                        ("|---12|", 12),
                        ("|10-20| * 3", 30),
                        ("-( | 10 - 20 | ** 3 )", -1000),
                        ("1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1", 10),
                        ("1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1", 1)
                    ]
                case "calculator2":
                    from sys import setrecursionlimit
                    setrecursionlimit(2**31-1)
                    tests = [
                        (" + ".join(["1"]*n), n) for n in range(100, 901, 100)
                    ]
                case "calculator3":
                    N = 367
                    tests = [
                        ("".join(map(str, range(N))), int("".join(map(str, range(N))))),
                        ("12345678982 + 123456773657984", 123469119336966)
                    ]
                case "slist1":
                    tests = [
                        ("(x)", "(x)"),
                        ("(x, y)", "(x, y)"),
                        ("(x, y, (z))", "(x, y, (z))"),
                        ("(x , (y) , z)", "(x , (y) , z)")
                    ]
                case "palindromes1":
                    tests = [
                        ("a", "a"),
                        ("b", "b"),
                        ("aa", "aa"),
                        ("abba", "abba"),
                        ("aabbaa", "aabbaa"),
                        ("aaba", None),
                    ]
                case "palindromes2":
                    tests = [
                        ("a"*n, "a"*n) for n in range(0, 30, 5)
                    ]
                case "lisp1":
                    tests = [
                        ("(+ 1 2)", 3),
                        ("(* 10 3)", 30),
                        ("(** 2 11)", 2048),
                    ]

            for test, solution in tests:

                start = time()

                parsed = parse(test, dFlag=dFlag)
                print("\nPARSED\n")
                
                for s, v in {
                    # "Sentence" : str(parsed),
                    # "AST" : parsed.AST,
                    "Eval" : validate(parsed, solution),
                    "Max States" : parsed.max_states,
                }.items(): print(f"{s:10s} : {v}")
                
                print()

                print(f"Runtime: {time()-start}")

    else:
        for arg in argv:
            if exists(arg):
                with open(arg) as file:
                    interpret(file.read(), dFlag=dFlag)
        if iFlag:
                for line in iter(lambda: get_input("</> "), "quit"):
                    if dFlag: start = time()
                    if vFlag:
                        interpret(line, dFlag)
                    else:
                        print(parse(line))
                    if dFlag: print(f"Runtime: {time() - start}")

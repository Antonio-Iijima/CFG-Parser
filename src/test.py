from main import *
from rich import print

from time import time


args = argv[2:]

while args:
    match args.pop(0):
        case "calc1":
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
        case "calc2":
            from sys import setrecursionlimit
            setrecursionlimit(2**31-1)
            tests = [
                (" + ".join(["1"]*n), n) for n in range(100, 901, 100)
            ]
        case "calc3":
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
        case "pal1":
            tests = [
                ("a", "a"),
                ("b", "b"),
                ("aa", "aa"),
                ("abba", "abba"),
                ("aabbaa", "aabbaa"),
                ("aaba", None),
            ]
        case "pal2":
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

        AST, max_states = parse(test)
        print("\nPARSED\n")
        
        result = evaluate(AST)
        
        for s, v in {
            "Max States" : max_states,
            "AST" : AST,
            "Type" : type(AST),
            "Eval" : result if result == solution else f"ERROR: value of {test} should be {solution}, but received {result or "False|None"}"
        }.items(): print(f"{s:10s} : {v}")
        
        print()

        print(f"Runtime: {time()-start}")

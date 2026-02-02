from main import *
from rich import print

from time import time


args = argv[2:]

while args:
    match args.pop(0):
        case "1":
            tests = [
                ("123", 123),
                ("1 + 2 + 3", 6),
                ("8 ** 2", 64),
                ("(2 + 3) * 5", 25),
                ("10 - (3 - 2)", 9),
                ("10 - 3 - 2", 5), 
                ("1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1", 10),
                ("1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1", 1)
            ]
        case "2":
            from sys import setrecursionlimit
            setrecursionlimit(2**31-1)
            tests = [
                (" + ".join(["1"]*n), n) for n in range(100, 901, 100)
            ]
        case "3":
            N = 367 # largest number we can currently process without a recursion error or changing the limit. Avg. Time: 0.24 sec.
            tests = [
                ("".join(map(str, range(N))), int("".join(map(str, range(N))))),
                ("12345678982 + 123456773657984", 123469119336966)
            ]
        case "4":
            tests = [
                ("(x)", "(x)")
            ]
        case "5":
            tests = [
                ("a", "a"),
                ("b", "b"),
                ("aa", "aa"),
                ("abba", "abba"),
                ("aabbaa", "aabbaa"),
                ("aaba", None),
            ]

    for test, solution in tests:

        start = time()

        # print(validate(test))
        AST = parse(test)
        print("\nPARSED\n")
        print("AST  :", AST)
        print("Type :", type(AST))
        result = evaluate(AST)
        print("Eval :", result if result == solution else f"ERROR: value of {test} should be {solution}, but received {result or "False|None"}")
        print()

        print(f"Runtime: {time()-start}")

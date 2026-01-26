from main import *
from rich import print

from time import time


# tests = [
#     ("123", 123),
#     ("1 + 2 + 3", 6),
#     ("8 ** 2", 64),
#     ("(2 + 3) * 5", 25),
#     ("10 - (3 - 2)", 9),
#     ("10 - 3 - 2", 5), 
#     ("1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1", 10),
#     ("1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1", 1)
# ]

from sys import setrecursionlimit
setrecursionlimit(2**31-1)
tests = [
    (" + ".join(["1"]*n), n) for n in range(100, 901, 100)
]

# N = 367 # largest number we can currently process without a recursion error or changing the limit. Avg. Time: 0.24 sec.
# tests = [
#     ("".join(map(str, range(N))), int("".join(map(str, range(N))))),
#     # ("12345678982 + 123456773657984", 123469119336966)
# ]

# tests = [
#     ("(x)", "(x)")
# ]

for test, solution in tests:

    start = time()

    # print(validate(test))
    AST = parse(test)
    print("\nPARSED\n")
    print(AST)
    print(type(AST))
    result = evaluate(AST)
    print(result if result == solution else f"ERROR: value of {test} should be {solution}, but received {result or "False|None"}")
    print()

    print(f"Runtime: {time()-start}")
from main import *



tests = [
    "123",          # 123
    "1 + 2 + 3",    # 6
    "8 ** 2",       # 64
    "(2 + 3) * 5",  # 25
    "10 - (3 - 2)"  # 9
]

# for test in tests:
#     # print(validate(test))
#     print(evaluate(parse(test)))

import re

DIGIT = lambda: r"[0-9]"

INT = lambda: rf"-?{DIGIT()}+"

FLOAT = lambda: rf"-?{INT()}\.{INT()}"

NUMBER = lambda: rf"{INT()}|{FLOAT()}"

EXP = lambda: rf"{FACTOR()} \*\* {FACTOR()}"

FACTOR = lambda: rf"\({EXPR()}\)|{EXP()}|{NUMBER()}"

FDIVIDE = lambda: rf"{TERM()} / {FACTOR()}"

IDIVIDE = lambda: rf"{TERM()} // {FACTOR()}"

DIVIDE = lambda: rf"{FDIVIDE()}|{IDIVIDE()}"

MULTIPLY = lambda: rf"{TERM()} \* {FACTOR()}"

TERM = lambda: rf"{MULTIPLY()}|{DIVIDE()}|{FACTOR()}"

ADD = lambda: rf"{EXPR()} \+ {TERM()}"

SUBTRACT = lambda: rf"{EXPR()} \- {TERM()}"

EXPR = lambda: rf"{ADD()}|{SUBTRACT()}|{TERM()}"


print(re.fullmatch(r".*(-).*", tests[-1]))
print(re.split(SUBTRACT(), tests[-1]))
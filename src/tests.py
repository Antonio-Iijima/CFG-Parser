from utils import get_config
from parser.eval import validate
from parser import parse

from sys import setrecursionlimit
from time import time



def test(tests: list[int] = None) -> None:
    name = get_config("language")
    
    setrecursionlimit(2**31-1)
        
    testcases = {
        "calculator" : [
            [ # 0
                ("123", 123),
                ("1 + 2 + 3", 6),
                ("8 ** 2", 64),
                ("(2 + 3) * 5", 25),
                ("10 - (3 - 2)", 9),
                ("10 - 3 - 2", 5), 
                ("1 + -12", -11),
                ("1 + - 12", -11),
                ("--12", 12),
                ("10 % 3", 1),
                ("-3 % 7", 4),
                ("|-26|", 26),
                ("|---12|", 12),
                ("|10-20| * 3", 30),
                ("-( | 10 - 20 | ** 3 )", -1000),
                ("1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1", 10),
                ("1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1 * 1", 1)
            ],
            [ # 1
                (" + ".join(["1"]*n), n) for n in range(100, 901, 100)
            ],
            [ # 2
                ("".join(map(str, range(1, 367))), int("".join(map(str, range(1, 367))))),
                ("12345678982 + 123456773657984", 123469119336966)
            ]
        ],
        "slist" : [
            [
                ("(x)", "(x)"),
                ("(x, y)", "(x, y)"),
                ("(x, y, (z))", "(x, y, (z))"),
                ("(x , (y) , z)", "(x , (y) , z)")
            ]
        ],
        "palindromes" : [
            [ # 0
                ("a", "a"),
                ("b", "b"),
                ("aa", "aa"),
                ("abba", "abba"),
                ("aabbaa", "aabbaa"),
                ("aaba", None),
            ],
            [ # 1
                ("a"*n, "a"*n) for n in range(0, 30, 5)
            ]
        ],
        "lisp" : [
            [
                ("(+ 1 2)", 3),
                ("(* 10 3)", 30),
                ("(** 2 11)", 2048),
            ]
        ]
    }.get(name)

    if testcases is None: return print(f"No test cases found for {name}.")
    
    tests = tests or list(range(len(testcases)))

    for i in tests:
        try:
            for test, solution in testcases[i]:
                start = time()

                parsed = parse(test)
                print("\nPARSED\n")
                
                for s, v in {
                    "Eval" : validate(parsed, solution),
                    "Max States" : parsed.max_states,
                }.items(): print(f"{s:10s} : {v}")
                
                print()

                print(f"Runtime: {time()-start}")
        except IndexError:
            raise IndexError(f"tried to access test {i}, but {name} has only {len(testcases)} tests.")

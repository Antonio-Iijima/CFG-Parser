from processing.syntax import Grammar
from processing.semantics import Eval

from utils import get_config

import sys


def compile() -> None:
    
    if (getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')):
        return print("Cannot compile from bundled language.")
    
    print(f"Compiling...")
    print()

    with open("parser/AST.py", "w") as file:
        grammar = Grammar()
        file.write(grammar.compile().strip()+"\n")
    
    with open("parser/eval.py", "w") as file:
        file.write(Eval(grammar.dependencies).compile().strip()+"\n")

    debug = get_config("flags", "debug")

    if debug:
        print()
        print("GRAMMAR")
        print()
        print(grammar)

    from parser import Parser
    Parser(debug).generate()

    print()
    print("Done!")
    print()

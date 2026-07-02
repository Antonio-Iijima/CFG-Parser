from compiler.syntax import Grammar
from compiler.semantics import Eval

from utils import get_config

import sys


def compile() -> None:
    
    if (getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')):
        return print("Cannot compile from bundled language.")
    
    with open(f"{get_config("paths", "generated")}/AST.py", "w") as file:
        grammar = Grammar()
        file.write(grammar.compile().strip()+"\n")
    
    with open(f"{get_config("paths", "generated")}/eval.py", "w") as file:
        file.write(Eval(grammar.dependencies).compile().strip()+"\n")

    debug = get_config("flags", "debug")

    from parser import Parser
    Parser(debug).generate()

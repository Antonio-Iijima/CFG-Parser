from parser.eval import _evaluate, Expr
from parser.lalr import LALR1

from datatypes import *
from utils import *



# potential future logic to swap parsing algorithms
Parser = LALR1



def evaluate(string: str) -> any:
    """Eval-Print"""
    try:
        out = _evaluate(Expr(parse(string).AST)) # can replace with Expr(parse(string)); parse should return AST (maybe)
        if out is not None: print(out)

    except Exception as e:
        if get_config("flags", "debug"): raise e
        else: print(f"{type(e).__name__}: {e}")
    

def parse(expr: str) -> Parsed:
    """To-do: Implement GLR parser."""
    
    dFlag = get_config("flags", "debug")

    parser = Parser(debug=dFlag).cache()

    # from temp.data import parse as PARSE
    # return Parsed(expr, PARSE(tokens), 0)
    return Parsed(expr, parser.parse(expr), 0)

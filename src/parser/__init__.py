from parser.parserdata import (
    terminals,
    rules,
    table,
    indentation,
    newlines,
    PROGRAM
)
from parser.evaluation import __Expr__

import processing



def parse(input: str, symbols: list = None, state: list = None) -> object:
    """Parses input string to AST.
    When metacompiling, the string must be a grammar specification.
    
    :param input: Input as a string.
    :returns: AST (recursive hierarchy of `Rule` types)."""

    return processing.parse(
        input=input,
        terminals=terminals,
        rules=rules,
        table=table,
        indentation=indentation,
        newlines=newlines,
        PROGRAM=PROGRAM,
        symbols=symbols,
        state=state
    )


def evaluate(input: str) -> any:
    """Wrapper for parse and evaluation operations. Returns the value of the passed AST.
    
    :param AST: An abstract syntax tree.
    :returns: The evaluated output (may write to a file instead if the language implements a compiler, or when metacompiling)."""

    return processing.evaluate(
        input=input,
        parse=parse,
        Expr=__Expr__
    )

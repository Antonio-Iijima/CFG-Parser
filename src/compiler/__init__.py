from compiler.parserdata import (
    rules,
    table,
    indentation,
    newlines,
    PROGRAM
)
from compiler.evaluation import __Expr__

import processing

import sys



def parse(input: str, symbols: list = None, state: list = None) -> object:
    """Parses input string to AST.
    When metacompiling, the string must be a grammar specification.
    
    :param input: Input as a string.
    :returns: AST (recursive hierarchy of `Rule` types)."""

    return processing.parse(
        remaining=input,
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

    if not (getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')):
        return processing.evaluate(
            input=input,
            parse=parse,
            Expr=__Expr__
        )

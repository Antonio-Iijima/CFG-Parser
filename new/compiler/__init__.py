from compiler.parserdata import (
    terminals,
    rules,
    table,
    PROGRAM
)
from compiler.evaluation import Expr
from utils import *



def parse(input: str, symbols: list = None, state: list = None) -> Rule:
    """Parses input string to AST.
    When metacompiling, the string must be a grammar specification.
    
    :param input: Input as a string.
    :returns: AST (recursive hierarchy of `Rule` types)."""
    
    input = lexer(input, terminals)
    if symbols is None: symbols = []
    if state is None: state = [0]

    step = -1
    while input:
        step += 1
        
        action, data = table[state[-1]].get(input[0].regex, [("E", False)])[0]

        match action:
            
            case "S":
                symbols.append(input.pop(0))
                state.append(data)

            case "R":
                rule, module, variant, n = rules[data]
                reduction = []

                for _ in range(n):
                    reduction.append(symbols.pop())
                    state.pop()
                
                symbols.append(rule(reversed(reduction), module, variant))
                
                # Handle goto as part of reduce action
                action, data = table[state[-1]][rule][0]
                if action == "G": state.append(data)
                else: raise ParseError(f"expected goto on token {state[-1]}")

            case "A":
                if len(symbols) == 1 and isinstance(symbols[0], PROGRAM): break
                raise ParseError("could not parse expression")
            
            case "E": 
                expected = set(tok for tok in table[state[-1]].keys() if isinstance(tok, str))
                
                raise ParseError(f'''unexpected {
                    f"{input[0].info} (Token matched r'{input[0].regex}')" if isinstance(input[0], Token) 
                    else f" {input[0]}"
                }
expected {", ".join(expected)}''')
            
            case _: raise ParseError(f"unknown action {action} in state {state}")

    return symbols.pop()



def evaluate(input: str) -> any:
    """Wrapper for parse and evaluation operations. Returns the value of the passed AST.
    
    :param AST: An abstract syntax tree.
    :returns: The evaluated output (may write to a file instead if the language implements a compiler, or when metacompiling)."""

    return Expr(parse(input))()

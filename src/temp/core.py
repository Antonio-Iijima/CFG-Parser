# from data import *
from temp.syntax import (
    _TERMINALS, 
    _RULES, 
    _TABLE,
    Rule,
    EOI,
    PROGRAM
    )
from utils import *

import re
from collections.abc import Sequence



class Token:
    def __init__(self, tok: str, regex: str, lineno: int, i: int):
        self.tok = tok
        self.regex = regex
        self.lineno = lineno
        self.i = i

        self.depth = 1

    
    @property
    def info(self) -> str:
        return f"{self.tok.__repr__()} at line {self.lineno}, col {self.i}"


    def __str__(self):
        return f"{self.tok}"
    

    def __repr__(self):
        return f"Token{self.tok, self.regex, self.lineno, self.i}"

        
def lexer(unprocessed: str) -> list[Token]:
    string = preprocess_input(unprocessed)
    tokens = []

    lineno, col = 1, 1
    while string:
        matches = []
        
        for regex in _TERMINALS:
            match = re.match(regex, string)
            if match: matches.append((match.group(), regex))

        if not matches: 
            raise SyntaxError(f"invalid token '{string[0]}' at line {lineno}, col {col}")

        # Prioritize the longest match; if multiple regular expressions
        # match the same characters, prioritize exact matches to handle reserved words.
        match, regex = max(matches, key=lambda tup: len(tup[0]) + int(tup[0] == tup[1]))
        
        if match.startswith("\n"): col = 1

        if (tokens or ("\n" not in match)): tokens.append(Token(match, regex, lineno, col))
        
        # Print warning in case of ambiguity between multiple matched patterns;
        # but assume exact matches are keywords and skip warning
        if len(matches) > 1 and (not re.escape(match) == regex):
            print_warnings(
                msg=f"multiple token matches at line {lineno}, col {col}",
                log={
                    "found " \
                    + ", ".join(set(tup[0] for tup in matches)) \
                    + f" | matched {match}" : [tup[1] for tup in matches]
                }
            )

        lineno += match.count("\n")
        col += len(match)
        if ("\n" in match): col -= match.rfind("\n")
        
        string = string.removeprefix(match).lstrip(" ")

    filtered = list(filter(None, tokens))

    return filtered + [ EOI() ]


def autoIndent(lines: list[str]) -> list:
    indented = []
    emptyLines = []
    curr_indent = prev_indent = 0

    levels = list((len(line)-len(line.lstrip(" "))) for line in lines)
    level = max(set(levels).difference({0}) or {1}, key=lambda val: levels.count(val))

    indentation = " " * level
    formatting = get_config("formatting")
    indent, dedent = formatting["indent"], formatting["dedent"]

    for i, line in enumerate(lines):
        
        if (not line.strip()):
            emptyLines.append(line)
            continue

        while line.startswith(indentation):
            line = line.removeprefix(indentation)
            curr_indent += 1

        if line.startswith(" "): 
            expected = (len(line)-len(line.lstrip(" ")))%level
            raise IndentationError(f"line {i+1}, {expected} space{"s" * (expected != 1)}.")

        diff = curr_indent - prev_indent

        while diff < 0:
            indented[-1] += dedent
            diff += 1

        # Newline will come after DEDENTs but before INDENTS
        indented.extend(emptyLines)
        indented.append("")
        
        while diff > 0:
            indented[-1] += indent
            diff -= 1
            
        indented[-1] += line
        emptyLines = []
        prev_indent, curr_indent = curr_indent, 0

    # Handle any final DEDENTs
    while prev_indent > 0:
        indented[-1] += dedent
        prev_indent -= 1

    return indented


def preprocess_input(string: str) -> list:

    lines = string.splitlines()

    for i, line in enumerate(lines):
        if "#" in line:
            lines[i] = line[:line.index("#")]

    formatting = get_config("formatting")
    indentation, newlines = formatting["indentation"], formatting["newlines"]

    return (
        "\n".join(autoIndent(lines)) if indentation
        else ("\n" if newlines else " ").join(lines).strip()
    )


def parse(input: str, symbols: list = None, state: list = None) -> Rule:
    input = lexer(input)
    if symbols is None: symbols = []
    if state is None: state = [0]

    step = -1
    while input:
        step += 1
        
        action, data = _TABLE[state[-1]].get(input[0].regex, [("E", False)])[0]

        match action:
            
            case "S":
                symbols.append(input.pop(0))
                state.append(data)

            case "R":
                rule, module, variant, n = _RULES[data]
                reduction = []

                for _ in range(n):
                    reduction.append(symbols.pop())
                    state.pop()
                
                symbols.append(rule(reversed(reduction), module, variant))
                
                # Handle goto as part of reduce action
                action, data = _TABLE[state[-1]][rule][0]
                if action == "G": state.append(data)
                else: raise ParseError(f"expected goto on token {state[-1]}")

            case "A":
                if len(symbols) == 1 and isinstance(symbols[0], PROGRAM): break
                raise ParseError("could not parse expression")
            
            case "E": 
                expected = set(tok for tok in _TABLE[state[-1]].keys() if isinstance(tok, str))
                
                raise ParseError(f'''unexpected {
                    f"{input[0].info} (Token matched r'{input[0].regex}')" if isinstance(input[0], Token) 
                    else f" {input[0]}"
                }
expected {", ".join(expected)}''')
            
            case _: raise ParseError(f"unknown action {action} in state {state}")

    return symbols.pop()



class Expr(Sequence):
    '''Immutable, callable `Sequence` object which returns its elements as instances of itself.'''

    ATTRIBUTES = { fname : func for fname, func in globals().items() if fname.startswith("p_")}

    def __new__(cls, node):
        return (
            super().__new__(cls) if isinstance(node, Rule)
            else node.tok if isinstance(node, Token)
            else node
        )
        
    def __init__(self, node: Rule):
        self._children = node.children
        self._node = node

    def __getitem__(self, index: int|slice):
        item = self._children[index]
        if isinstance(index, slice):
            return tuple(Expr(e) for e in item)
        return Expr(item)
  
    def __len__(self):
        return len(self._children)
   
    def __str__(self):
        return self._node.__str__()

    def __repr__(self):
        return self._node.__repr__()

    def __call__(self, i: int = None, *args, **kwargs):
        e = self if (i == None) else self[i]
        return _evaluate(e, *args, **kwargs)


def _default(x: Expr): return x(0)


def _get_function(node: Rule):
    return (
        Expr.ATTRIBUTES.get(f"{node.fname}_{node.variant}")
        or Expr.ATTRIBUTES.get(node.fname)
        or _default
    )


def _evaluate(expr, *args, **kwargs):
    return (
        _get_function(expr._node)(expr, *args, **kwargs) if isinstance(expr, Expr)
        else expr
    )

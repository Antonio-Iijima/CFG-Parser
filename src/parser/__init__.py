from parser.lalr import (
    LALR1
)

# try:
from parser.AST import (
    GRAMMAR,
    TERMINALS,
    TOKENS,
    START,
    PROGRAM
)
# except:

from parser.eval import _evaluate, Expr

from utils import *
from datatypes import *
from parser.lalr import LALR1



# potential future logic to swap parsing algorithms
Parser = LALR1



def evaluate(string: str) -> any:
    """Eval-Print"""
    try:
        out = _evaluate(Expr(parse(string).AST))
        if out is not None: print(out)

    except Exception as e:
        raise e
    

def parse(expr: str, state_limit: int = 2**100) -> Parsed:
    """To-do: Implement GLR parser."""
    
    dFlag = get_config("flags", "debug")

    tokens = tokenize(expr)
    parser = Parser(dFlag).cache()

    return Parsed(expr, parser.parse(tokens), 0)


def tokenize(unprocessed: str) -> list:
    """Fully tokenize a raw unprocessed string and add EOI marker."""
    # from parser.AST import TERMINALS
    
    string = preprocess_input(unprocessed)
    tokens = []

    lineno, i = 0, 0
    while string:
        matches = []
        
        for regex in TERMINALS:
            match = re.match(regex, string)
            if match: matches.append((match.group(), regex))

        if not matches: 
            raise SyntaxError(f"invalid token '{string[0]}' at line {lineno}, col {i}")

        match, regex = max(matches, key=lambda tup: len(tup[0]))
        
        if (tokens or ("\n" not in match)): tokens.append(Token(match, regex, lineno, i))
        lineno += match.count("\n")
        i = match.rfind("\n") if ("\n" in match) else (i+len(match))
        
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
    """Strips # comments and wraps automatic indentation processing."""

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

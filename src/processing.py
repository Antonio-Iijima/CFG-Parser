from datatypes import *
from utils import *

from rich import print
from time import time

import re



def parse(
        input: str, 
        terminals: set[str],
        rules: tuple[tuple],
        table: dict[int, dict],
        indentation: bool,
        newlines: bool,
        PROGRAM: Rule,
        symbols: list = None, 
        state: list = None
    ) -> Rule:
    """Parses input string to AST.
    When metacompiling, the string must be a grammar specification.
    
    :param input: Input as a string.
    :returns: AST (recursive hierarchy of `Rule` types)."""

    input = lexer(
        unprocessed=input,
        terminals=terminals,
        indentation=indentation,
        newlines=newlines
    )
    
    if symbols is None: symbols = []
    if state is None: state = [0]
    
    if CONFIG.flags.debug: 
        parserOutput = displayTable(
            title="Parser Output",
            columns={
                "Step" : {"justify" : "center"},
                "State" : {},
                "Symbols" : {},
                "Input" : {"justify" : "right"},
                "Action" : {"justify" : "center"}
            }
        )

    if CONFIG.flags.time: start = time()

    try:
        step = -1
        while input:
            step += 1
            
            action, data = table[state[-1]].get(input[0].regex, [("E", False)])[0]

            if CONFIG.flags.debug:
                parserOutput.add_row(
                    str(step), 
                    lstToStr(state),
                    lstToStr(symbols),
                    lstToStr(input),
                    { "A" : "ACC", "E" : "ERR" }.get(action, f"{action} {data}")
                )

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

                case "E": 
                    expected = set({EOI : "EOI"}.get(tok, tok) for tok in table[state[-1]].keys() if (isinstance(tok, str) or tok == EOI))
                    
                    raise ParseError(f'''unexpected {
                        f"{input[0].info} (Token matched r'{input[0].regex}')" if isinstance(input[0], Token) 
                        else f" {input[0]}"
                    }
    expected {", ".join(expected)}''')
                
                case _: raise ParseError(f"unknown action {action} in state {state}")

    finally:
        if CONFIG.flags.time:
            end = time() - start
            print(f"Parse time: {end*1000:.7} ms")

        if CONFIG.flags.debug: print(parserOutput, "")

    if tuple(map(type, symbols)) == (PROGRAM, EOI): return symbols[0]
    raise ParseError("could not parse expression")



def evaluate(input: str, parse, Expr: object) -> any:
    """Wrapper for parse and evaluation operations. Returns the value of the passed AST.
    
    :param AST: An abstract syntax tree.
    :returns: The evaluated output (may write to a file instead if the language implements a compiler, or when metacompiling)."""

    return Expr(parse(input))()


def lexer(unprocessed: str, terminals: set, indentation: bool, newlines: bool) -> list[Token]:
    string = preprocess_input(
        string=unprocessed,
        indentation=indentation,
        newlines=newlines
    )
    
    tokens = []
    lineno, col = 1, 1
    
    while string:
        matches = []
        
        for regex in terminals:
            match = re.match(regex, string)
            if match: matches.append((match.group(), regex))

        if not matches: 
            raise SyntaxError(f"invalid token '{string[0]}' at line {lineno}, col {col}")

        # Prioritize the longest match; if multiple regular expressions match
        # the same characters, prioritize exact matches to handle reserved words.
        match, regex = max(matches, key=lambda tup: len(tup[0]) + int(tup[0] == tup[1]))
        
        if match.startswith("\n"): col = 1

        if (tokens or ("\n" not in match)): tokens.append(Token(match, regex, lineno, col))
        
        # Print warning in case of ambiguity between multiple matched 
        # patterns, but assume exact matches are keywords and skip warning
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
    indent, dedent = f" {CONFIG.formatting.indent} ", f" {CONFIG.formatting.dedent} "

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


def preprocess_input(string: str, indentation, newlines) -> list:
    lines = string.splitlines()
    return (
        "\n".join(autoIndent(lines)) if indentation
        else ("\n" if newlines else " ").join(lines).strip()
    )

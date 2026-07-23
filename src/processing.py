from datatypes import *
from utils import *

from rich import print
from time import time

import re



def parse(
        remaining: str,
        scansets: set,
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

    lineno, col = 1, 1
    token = None
    
    if symbols is None: symbols = []
    if state is None: state = [0]
    
    remaining = preprocess_input(
        string=remaining,
        indentation=indentation,
        newlines=newlines
    )


    def scan() -> None:
        """Scans the input for the next token that is valid in the current state.
        
        :param state: Current state of the parser.
        :param input: Remaining input.
        :returns: The next valid token and the remaining input."""
        nonlocal token, lineno, col, remaining, scansets
        
        if not remaining: 
            if token == EOI(): token = None
            else: token = EOI()
            return

        matches = []        
        
        # for regex in terminals:
        for regex in scansets[token if token is None else token.regex]:
            if regex == EOI: continue
        # for regex in filter(lambda tok: isinstance(tok, str), table[state[-1]].keys()):
            match = re.match(regex, remaining)
            if match: matches.append((match.group(), regex))
        
        if not matches: 
            raise SyntaxError(f"invalid token '{remaining[0]}' at line {lineno}, col {col}")

        # Prioritize the longest match; if multiple regular expressions match
        # the same characters, prioritize exact matches to handle reserved words.
        match, regex = max(matches, key=lambda tup: len(tup[0]) + int(tup[0] == tup[1]))
        if match.startswith("\n"): col = 1

        token = Token(match, regex, lineno, col)
        remaining = remaining.removeprefix(match).lstrip(" ") 

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
        if ("\n" in match): col = len(match) - match.rfind("\n")


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

    scan()
    try:
        step = -1
        parsing = True
        while parsing:
            step += 1
            
            action, data = table[state[-1]].get(token if token is None else token.regex, [("E", False)])[0]
            
            if CONFIG.flags.debug:
                parserOutput.add_row(
                    str(step), 
                    lstToStr(state),
                    lstToStr(symbols),
                    remaining,
                    { "A" : "ACC", "E" : "ERR" }.get(action, f"{action} {data}")
                )

            match action:
                
                case "S":
                    symbols.append(token)
                    state.append(data)
                    scan()

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
                    if tuple(map(type, symbols)) == (PROGRAM, EOI): return symbols[0]
                    raise ParseError("could not parse expression")

                case "E": 
                    expected = set({EOI : "EOI"}.get(tok, tok) for tok in table[state[-1]].keys() if (isinstance(tok, str) or tok == EOI))
                    
                    raise ParseError(f'''unexpected {
                        f"{token.info} (Token matched r'{token.regex}')" if isinstance(token, Token) 
                        else f" {token}"
                    }
    expected {", ".join(expected)}''')
                
                case _: raise ParseError(f"unknown action {action} in state {state}")

    finally:
        if CONFIG.flags.time: print(f"Parse time: {(time() - start)*1000:.7} ms")

        if CONFIG.flags.debug: print(parserOutput, "")



def evaluate(input: str, parse, Expr: object) -> any:
    """Wrapper for parse and evaluation operations. Returns the value of the passed AST.
    
    :param AST: An abstract syntax tree.
    :returns: The evaluated output (may write to a file instead if the language implements a compiler, or when metacompiling)."""

    return Expr(parse(input))()



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
        else ("\n" if newlines else " ").join(lines)
    ).strip()

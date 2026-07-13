from datatypes import *
from config import CONFIG

from rich.table import Table
import re



def lexer(unprocessed: str, terminals: set) -> list[Token]:
    string = preprocess_input(unprocessed)
    tokens = []

    lineno, col = 1, 1
    while string:
        matches = []
        
        for regex in terminals:
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
    indent, dedent = CONFIG.formatting.indent, CONFIG.formatting.dedent

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

    # for i, line in enumerate(lines):
    #     if "#" in line:
    #         lines[i] = line[:line.index("#")]

    indentation, newlines = CONFIG.formatting.indentation, CONFIG.formatting.newlines

    return (
        "\n".join(autoIndent(lines)) if indentation
        else ("\n" if newlines else " ").join(lines).strip()
    )


def print_warnings(msg: str, log: dict[str, list]) -> None:
    """Prints warnings. Uses the following structure, where `key[i]` and `val[i,j]` come from `log`:
```
WARNING: <msg> (<key[1]>)
       | <val[1,1]>
       | <val[1,2]>
...
WARNING: <msg> (<key[n]>)
       | <val[n,1]>
       | <val[n,2]>
```
    
    :param msg: The warning message.
    :param log: Dictionary of applicable info for the warning."""
    
    for type, warnings in sorted(log.items(), key=lambda tup: len(tup[0]), reverse=True):
        if warnings:
            print("WARNING: " + msg + f" ({type})")
            for path in warnings:
                print(f"       | {path}")
    print()


# def table(title: str, headers: dict, rows: list = None, grid: bool = False) -> Table:
#     """Construct a renderable table from the headers and data."""

#     rows = rows or []

#     if grid:
#         display = Table.grid()
#     else:
#         display = Table()
#         for header, kwargs in headers.items():
#             display.add_column(header, **kwargs)
    
#     for row in rows:
#         display.add_row(*row)

#     display.title = title

#     return display


def get_input(prompt: str = "", s: str = "") -> str:
    if s.endswith("\nquit"):
        from sys import exit
        exit()
    
    elif s.endswith("\nclear"):
        from os import system, name as OS
        system('cls' if OS == 'nt' else 'clear')
        print(f"magicc v{CONFIG.version} </> {CONFIG.language} {CONFIG.implementation}")
        return ""
    
    elif s.endswith("\n"):
        return s
    
    return get_input("." * (len(prompt)-1) + " ", s + "\n" + input(prompt))


def regularize(path: str) -> None:
    import os
    
    if os.path.isdir(path):
        for file in os.listdir(path):
            regularize(os.path.join(path, file))
            
    elif path.endswith("syntax.txt"):
        print(f"Regularizing {path}")
        
        with open(path) as file:
            text = file.read()
            text = text.splitlines()
        
        offset = 0

        for i, line in enumerate(s.strip() for s in text):
            text[i] = [s.strip() for s in line.split("->", 1)]
            if len(text[i]) == 2:
                offset = max(offset, len(text[i][0]))

        for i, line in enumerate(text):
            if isinstance(line, list):
                if len(line) == 1:  
                    text[i] = line[0]
                else:
                    rule, production = line
                    text[i] = f"{rule.upper()}{" " * (offset-len(rule))} -> {" ".join([s if (len(s) > 1 and s[::len(s)-1] == "\"\"") else s.upper() for s in production.split()])}"

        text = "\n".join(text).strip() + "\n"

        with open(path, "w") as file:
            file.write(text)



if __name__ == "__main__":
    from sys import argv

    regularize(argv[-1])
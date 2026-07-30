from config import CONFIG

from rich.table import Table
from rich import print

import sys
import os



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
    
    if not (CONFIG.flags.verbose and log): return
    
    for note, warnings in sorted(log.items(), key=lambda tup: len(tup[0]), reverse=True):
        if warnings:
            print("WARNING: " + msg + f" ({note})")
            for details in warnings:
                print(f"       | {details}")
    print()


def displayTable(title: str, columns: dict, rows: list = None, grid: bool = False) -> Table:
    """Construct a renderable table from the column labels and data."""

    rows = rows or []

    if grid:
        display = Table.grid()
    else:
        display = Table()
        for column, kwargs in columns.items():
            display.add_column(column, **kwargs)
    
    for row in rows:
        display.add_row(*row)

    display.title = title

    return display


def lstToStr(lst: list) -> str:
    return " ".join(map(str, lst))


def get_input(prompt: str = "", s: str = "") -> str|None:
    match s:
        case "\nquit": 
            return "quit"
        case "\nclear":
            os.system('cls' if os.name == 'nt' else 'clear')
            print(CONFIG.info)
            return None
        case _:
            if s.endswith("\n"): return s
            return get_input("... ", s + "\n" + input(prompt))


def ation():
    i = 0
    while True: yield i; i += 1


def regularize(path: str) -> None:    
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
    regularize(sys.argv[-1])

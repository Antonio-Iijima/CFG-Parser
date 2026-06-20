from io import TextIOWrapper
from json import load, dump
from rich.table import Table

import re
import os



### Errors and Exceptions ###



class ParseError(Exception): pass
class TableGenerationError(Exception): pass
class ValidationError(Exception): pass



### Utility Functions ###



def get_config(*keys): 
    """Look up a value from the config, applying keys sequentially.
    No arguments returns the config itself."""
    
    with open(os.path.join(os.path.dirname(__file__), "config.json")) as file:
        cfg = load(file)

    for key in keys: cfg = cfg[key]

    return cfg


def set_config(cfg: dict, indent: int = 3):
    """Writes a provided `dict` to the config.json file."""
    
    with open(os.path.join(os.path.dirname(__file__), "config.json"), "w") as file:
        dump(cfg, file, indent=indent)


def preprocess_text(text: TextIOWrapper) -> list[str]: 
    return list(filter(lambda line: any(line.startswith(s) for s in ("<", "#require")), map(lambda s: s.strip(), text.read().splitlines())))


def is_nonterminal(prod: str) -> bool: 
    return isinstance(prod, str) and re.fullmatch(r"<.*>", prod)


def is_terminal(prod: str) -> bool: 
    return not is_nonterminal(prod)


def get_input(prompt: str = "", s: str = "") -> str:
    if s.endswith("\nquit"):
        from sys import exit
        exit()
    
    elif s.endswith("\nclear"):
        from os import system, name as OS
        system('cls' if OS == 'nt' else 'clear')
        print(f"magicc v{get_config("version")} </> {get_config("language")} {get_config("implementation")}")
        return ""
    
    elif s.endswith("\n"):
        return s
    
    return get_input("." * (len(prompt)-1) + " ", s + "\n" + input(prompt))


def regularize(path: str) -> None:
    if os.path.isdir(path):
        for file in os.listdir(path):
            regularize(os.path.join(path, file))
            
    elif path.endswith(".txt"):
        print(f"Regularizing {path}")
        
        with open(path) as file:
            text = file.read()
            text = text.splitlines()
        
        offset = 0

        for i, line in enumerate(s.strip() for s in text):
            text[i] = [s.strip() for s in line.split("::=")]
            if len(text[i]) == 2:
                offset = max(offset, len(text[i][0]))

        for i, line in enumerate(text):
            if isinstance(line, list):
                if len(line) == 1:  
                    text[i] = line[0]
                else:
                    rule, production = line
                    text[i] = f"{rule.upper()}{" " * (offset-len(rule))} ::= {" ".join([s.upper() if (len(s) > 1 and s[::len(s)-1] == "<>") else s for s in production.split()])}"

        text = "\n".join(text).strip() + "\n"

        with open(path, "w") as file:
            file.write(text)


def pathToFunc(path: str) -> str:
    """Converts a path .lib/path/to/somewhere to a function prefix p_path_to_somewhere_<fname>."""
    return f"p_{path.lower().removeprefix(".lib/").replace("/", "_")}_".lower()


def print_warnings(msg: str, log: dict) -> None:
    from datatypes import OrderedSet

    for type, warnings in sorted(log.items(), key=lambda tup: len(tup[0]), reverse=True):
        if warnings:
            print("WARNING: " + msg + f" ({type})")
            for path in OrderedSet(warnings):
                print(f"       | {path}")


def tostr(l: list) -> list[str]:
    """Shorthand for `list(map(str, l))`"""
    return list(map(str, l))


def lib(path: str) -> str:
    """Prepend `.lib/` to `path` and replace all `.` with `/`."""
    return f".lib/{path.replace(".", "/")}"


def table(title: str, headers: dict, rows: list = None, grid: bool = False) -> Table:
    """Construct a renderable table from the headers and data."""

    rows = rows or []

    if grid:
        display = Table.grid()
    else:
        display = Table()
        for header, kwargs in headers.items():
            display.add_column(header, **kwargs)
    
    for row in rows:
        display.add_row(*row)

    display.title = title

    return display



if __name__ == "__main__":
    from sys import argv

    regularize(argv[-1])

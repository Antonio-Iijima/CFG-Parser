from io import TextIOWrapper
from datatypes import Nonterminal



LIB_PATH = ".lib"



def preprocess_text(text: TextIOWrapper) -> list[str]: 
    return [line for line in text.read().splitlines() if line.strip() and not line.startswith("--")]


def is_nonterminal(prod: str) -> bool: 
    return isinstance(prod, str) and prod.startswith("<") and prod.endswith(">")


def is_terminal(prod: str) -> bool: 
    return not is_nonterminal(prod)


def split_pattern(prod: str, lbrace: str = "<", rbrace: str = ">") -> list:
    """Converts a string representation of a single production rule pattern into a list."""

    if not prod: return []
    
    remap = {
        "NEWLINE" : "\\n",
        "INDENT"  : "INDENT",
        "DEDENT"  : "DEDENT",
    }

    out = []
    is_nonterminal = False

    charlist = list(prod.strip())

    # Short circuit for empty list
    if not charlist: return []

    # Preload first element; not included in loop
    out.append(charlist[0])

    for prev, curr in zip(charlist[:-1], charlist[1:]):
        
        is_nonterminal = (is_nonterminal or prev == lbrace) and not (curr == rbrace)

        # Conditions to start a new word
        if (
            (curr == lbrace) 
            or (prev == rbrace) 
            or (curr == " ")
        ) and not (out[-1] == ""): out.append("")
        
        if not curr == " ":
            curr = {lbrace : "<", rbrace : ">"}.get(curr, curr)
            out[-1] += curr.upper() if is_nonterminal else curr

    pattern = Nonterminal.update_modifiers([ remap.get(token, token) for token in out ])

    return pattern


def comparative(x): 
    return x if isinstance(x, str) else x.__name__


def compare(a: list, b: list) -> bool:
    """Check if all the elements of `a` and `b` match."""
    return len(a) == len(b) and all(comparative(x) == comparative(y) for x, y in zip(a, b))


def get_input(prompt: str = "", s: str = "") -> str:
    if s.endswith("\nquit"):
        from sys import exit
        exit()
    if s.endswith("\n"):
        return s
    return get_input("." * (len(prompt)-1) + " ", s + "\n" + input(prompt))
    

def ordinal(s: str) -> int:
    return abs(hash(s)%100000)


def show_grammar(grammar: dict, max_lines: int = 7) -> None:
    offset = max(len(p) for p in grammar)

    for rule, alternatives in grammar.items(): 
        for i, pattern in enumerate(alternatives):
            if i == 0:
                print(f"<{rule}>{" " * (offset - len(rule))} ::= {" ".join(pattern)}")
            else:
                print(" "*(offset+5), end='')
                if i < max_lines:
                    print("| " + " ".join(pattern))
                else:
                    print("...")
                    break
    
    return offset

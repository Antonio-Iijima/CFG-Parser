from io import TextIOWrapper



LIB_PATH = ".lib"



def preprocess_text(text: TextIOWrapper) -> list[str]: 
    return [line for line in text.read().splitlines() if line and not line.startswith("--")]


def filterl(f, x): 
    return list(filter(f, x))


def is_nonterminal(prod: str) -> bool: 
    return isinstance(prod, str) and prod.startswith("<") and prod.endswith(">")


def is_terminal(prod: str) -> bool: 
    return not is_nonterminal(prod)


def embed_nonterminal(s: str) -> str:
    if is_nonterminal(s):
        s = s[1:-1]
    if s.startswith("!"):
        s = s[1:]
        
    return s


def split_pattern(prod: str, lbrace: str = "<", rbrace: str = ">") -> list:
    """Converts a string representation of a RH production rule into a list."""

    if not prod: return []
    
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

    return out


def comparative(x): 
    return x if isinstance(x, str) else x.__name__


def compare(a: list, b: list) -> bool:
    """Check if all the elements of `a` and `b` match."""
    return len(a) == len(b) and all(comparative(x) == comparative(y) for x, y in zip(a, b))


def get_input(prompt: str = "", s: str = "") -> str:
    if s.endswith("\nquit"):
        quit()
    if s.endswith("\n"):
        return s
    return get_input("." * (len(prompt)-1) + " ", s + "\n" + input(prompt))
    

def ordinal(s: str) -> int:
    return abs(hash(s)%100000)

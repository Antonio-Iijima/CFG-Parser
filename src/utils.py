def preprocess_text(text: list[str]) -> list[str]: 
    return [line for line in text if line and not line.startswith("--")]


def filterl(f, x): 
    return list(filter(f, x))


def is_nonterminal(prod: str) -> bool: 
    return isinstance(prod, str) and prod.startswith("<") and prod.endswith(">")


def is_terminal(prod: str) -> bool: 
    return not is_nonterminal(prod)


def embed_nonterminal(s: str) -> str: 
    return s[1:-1] if is_nonterminal(s) else s


def split_pattern(prod: str) -> list:
    """Converts a string representation of a RH production rule into a list."""

    if not prod: return []
    
    out = []
    is_nonterminal = False
    is_param = False
    nextWord = False

    for c in list(prod.strip()):
        
        if not c: continue

        is_nonterminal = (is_nonterminal or c == "<") and not c == ">"
        is_param = (is_param or (c == "[")) and not (c == "]")
        nextWord = (not out) or (
            (not is_param) and (c == "<")
        )

        if nextWord: out.append("")
        
        out[-1] += c.upper() if is_nonterminal else c
        
        if not is_param and c == ">": out.append("")

    out = [c.strip() for c in out if c.strip()]

    return out


def comparative(x): 
    return x if isinstance(x, str) else x.__name__


def compare(a: list, b: list) -> bool:
    """Check if all the elements of `a` and `b` match, filtering epsilons from both."""
    from AST import EPSILON
    

    f = lambda x: not (x == EPSILON)
    a, b = filterl(f, a), filterl(f, b)

    return len(a) == len(b) and all(comparative(x) == comparative(y) for x, y in zip(a, b))

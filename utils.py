def is_nonterminal(prod: str) -> bool:
    return all((
        prod.startswith("<"),
        prod.endswith(">"),
        prod[1:-1].isalpha()
    ))


def is_terminal(prod: str) -> bool: return not is_nonterminal(prod)


def embed_nonterminal(s: str) -> str: return s[1:-1] if is_nonterminal(s) else s


def split(prod: str) -> list:
    out = []
    nextWord = False

    for c in prod:
        if nextWord:
            out.append("")
            nextWord = False

        match c:
            case "<":
                out.append(c)
            case ">":
                out[-1] += c
                nextWord = True
            case _:
                if not out: out.append(c)
                else: out[-1] += c

    return out

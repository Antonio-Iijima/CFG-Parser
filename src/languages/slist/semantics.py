def p_symbolexpr_3(expr):
    return f"({expr[1]})"

def p_symbolexpr(expr): 
    return expr[0]

def p_slist_0(expr):
    return expr[0]

def p_slist(expr):
    return "".join(({ None : " " }.get(e, e) for e in expr))

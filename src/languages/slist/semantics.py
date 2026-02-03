def p_symbolexpr(expr): 
    return "".join(expr) if len(expr) == 3 else expr[0]

def p_slist(expr):
    return "".join(expr) if len(expr) == 3 else expr[0]

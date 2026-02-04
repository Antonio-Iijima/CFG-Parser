def p_mathexpr(expr):
    return expr[0]

def p_add(expr): 
    return expr[1] + expr[2]

def p_subtract(expr): 
    return expr[1] - expr[2]

def p_term(expr): 
    return expr[0]

def p_multiply(expr): 
    return expr[1] * expr[2]

def p_divide(expr):
    return expr[0]

def p_factor(expr): 
    return expr[1] if len(expr) == 3 else expr[0]

def p_idivide(expr): 
    return expr[1] // expr[2]

def p_fdivide(expr): 
    return expr[1] / expr[2]

def p_exp(expr): 
    return expr[1] ** expr[2]
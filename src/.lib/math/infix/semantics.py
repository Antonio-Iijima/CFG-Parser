def p_add(expr): 
    return expr(0) + expr(2)

def p_subtract(expr): 
    return expr(0) - expr(2)

def p_multiply(expr): 
    return expr(0) * expr(2)

def p_factor_0(expr):
    return expr(1)

def p_factor_4(expr):
    return -expr(1)

def p_abs(expr):
    return abs(expr(1))

def p_idivide(expr): 
    return expr(0) // expr(2)

def p_fdivide(expr): 
    return expr(0) / expr(2)

def p_exp(expr): 
    return expr(0) ** expr(2)

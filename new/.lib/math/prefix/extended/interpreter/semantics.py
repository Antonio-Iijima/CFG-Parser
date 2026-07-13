def p_negative(expr):
    return - expr(1)

def p_modulo(expr):
    return expr(0) % expr(2)

def p_abs(expr):
    return abs(expr(1))

def p_exp(expr): 
    return expr(0) ** expr(2)

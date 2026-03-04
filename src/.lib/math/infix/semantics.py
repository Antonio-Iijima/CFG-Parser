def p_factor_3(expr):
    return -expr(1)

def p_abs(expr):
    return abs(expr(1))

def p_exp_0(expr): 
    return expr(0) ** expr(2)

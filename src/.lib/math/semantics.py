def p_float(expr):
    return float(f"{expr(0)}.{expr(2)}")

def p_int_0(expr): 
    return int(f"{expr(0)}{expr(1)}")

def p_int(expr): 
    return int(expr(0))

def p_digit(expr): 
    return int(expr(0))

def p_expr(expr):
    return expr[0]

def p_add(expr): 
    return expr[0] + expr[2]

def p_subtract(expr): 
    return expr[0] - expr[2]

def p_term(expr): 
    return expr[0]

def p_multiply(expr): 
    return expr[0] * expr[2]

def p_idivide(expr): 
    return expr[0] // expr[2]

def p_fdivide(expr): 
    return expr[0] // expr[2]

def p_factor(expr): 
    return expr[1] if len(expr) == 3 else expr[0]

def p_exp(expr): return expr[0] ** expr[2]

def p_number(expr): 
    return expr[0]

def p_float(expr): 
    return float("".join(expr))

def p_int(expr): 
    return int("".join(map(str, expr))) if len(expr) == 2 else int(expr[0])

def p_digit(expr): 
    return int(expr[0])

def p_op_add(expr): return None

def p_op_subtract(expr): return None

def p_op_multiply(expr): return None

def p_op_exp(expr): return None

def p_op_fdivide(expr): return None

def p_op_idivide(expr): return None

def p_op_lparen(expr): return None

def p_op_rparen(expr): return None

def p_spaces(expr): return None

def p_space(expr): return None

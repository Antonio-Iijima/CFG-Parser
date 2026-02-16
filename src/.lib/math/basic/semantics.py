def p_add(expr):
    return expr(0) + expr(2)

def p_subtract(expr): 
    return expr(0) - expr(2)

def p_term_2(expr):
    return -expr(1)

def p_multiply(expr): 
    return expr(0) * expr(2)

def p_divide(expr): 
    return expr(0) / expr(2)

def p_modulo(expr):
    return expr(0) % expr(2)

def p_factor_0(expr):
    return expr(1)

def comparison(expr):
    return bool(expr(0))

def p_le(expr):
    return expr(0) < expr(2)
    
def p_leq(expr):
    return expr(0) <= expr(2)
    
def p_ge(expr):
    return expr(0) > expr(2)
    
def p_geq(expr):
    return expr(0) >= expr(2)
    
def p_eq(expr):
    return expr(0) == expr(2)
    
def p_neq(expr):
    return expr(0) != expr(2)

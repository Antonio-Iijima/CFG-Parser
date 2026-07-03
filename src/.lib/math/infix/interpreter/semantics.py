def p_or_0(expr):
    return expr(0) or expr(2)

def p_and_0(expr):
    return expr(0) and expr(2)

def p_not_0(expr):
    return not expr(1)


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


def p_sum_0(expr):
    return expr(0) + expr(2)

def p_sum_1(expr): 
    return expr(0) - expr(2)

def p_term_0(expr): 
    return expr(0) * expr(2)
    
def p_term_1(expr): 
    return expr(0) / expr(2)

def p_factor_0(expr):
    return - expr(1)

def p_power_0(expr):
    return expr(0) ** expr(2)

def p_group_0(expr):
    return expr(1)

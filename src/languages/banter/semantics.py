g_env = {}

 
def lookup(var): return g_env(var)

def p_assignment(expr):
    g_env[expr(1)] = expr(3)

def p_if_then(expr):
    if expr(1): return expr(4)

def p_if_then_else(expr):
    if expr(1):
        return expr(4)
    else: 
        return expr(6)
    
def p_condition(expr):
    return bool(int(expr(0)))
    
def p_statement_list_1(expr):
    return expr

def p_return(expr):
    print(expr(1))
    exit()

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

def p_variable(expr):
    return g_env[expr(0)]

def p_string(expr):
    return expr(1)
g_env = {}
g_markers = {}

 
def lookup(var): return g_env(var)

def p_assignment(expr):
    g_env[expr(1)] = expr(3)

def p_if_then(expr):
    if expr(1): 
        return expr(4)

def p_if_then_else(expr):
    if expr(1):
        return expr(4)
    else: 
        return expr(6)
    
def p_return(expr):
    print(expr(1))
    exit()

def p_string(expr):
    return expr(1)

def p_reference(expr):
    return g_env[expr(0)]

def p_jump(expr):
    return g_markers[expr(2)]()

def p_marker(expr):
    g_markers[expr(1)] = lambda: expr(2)

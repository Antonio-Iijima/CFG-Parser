g_env = {}
g_markers = {}

 
def p_statements_0(expr):
    expr(0)
    
def p_statements_1(expr):
    expr(0)
    expr(1)


def p_assignment(expr):
    g_env[expr(1)] = expr(3)


def p_string(expr):
    return expr(1)


def p_if_then(expr):
    if expr(1): 
        expr(4)

def p_if_then_else(expr):
    if expr(1):
        expr(4)
    else: 
        expr(6)

def p_block(expr):
    return expr(1)

def p_return(expr):
    raise Exception(0, expr(1))


def p_marker(expr):
    g_markers[expr(1)] = lambda: expr(2)
    expr(2)

def p_jump(expr):
    g_markers[expr(2)]()


def p_label(expr):
    try:
        return g_env[expr(0)]
    except KeyError:
        raise Exception(1, f"Error: variable {expr(0)} not declared.")


def p_print(expr):
    print(expr(1))

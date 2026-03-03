g_env = {}
g_markers = {}



def p_statement(expr):
    expr(0)    


def p_statement_list_0(expr):
    expr(0)
    
def p_statement_list_1(expr):
    expr(0)
    expr(2)


def p_assignment(expr):
    g_env[expr(1)] = expr(3)


def p_string(expr):
    return expr(1)


def p_if_then(expr):
    if expr(1): 
        expr(5)

def p_if_then_else(expr):
    if expr(1):
        expr(5)
    else: 
        expr(9)

def p_block(expr):
    return expr(1)


def p_return(expr):
    raise Exception(0, expr(1))


def p_marker(expr):
    mark = expr(1)
    if not mark in g_markers: 
        g_markers[mark] = lambda: expr(3)
    expr(3)

def p_jump(expr):
    g_markers[expr(2)]()


def p_label(expr):
    try:
        return g_env[expr(0)]
    except KeyError:
        raise Exception(1, f"Error: variable {expr(0)} not declared.")


def p_print(expr):
    print(expr(1))

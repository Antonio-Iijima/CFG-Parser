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
        expr(4)

def p_if_then_else(expr):
    if expr(1):
        expr(4)
    else: 
        expr(7)

def p_block(expr):
    return expr(2)


def p_return(expr):
    raise Exception(0, expr(1))


def p_marker(expr):
    mark = f"marker_{expr(1)}"
    jump = True
    while jump:
        try:
            expr(3)
            jump = False
        except Exception as e:
            jump = (mark in e.args[0])
            if not jump: raise e


def p_jump(expr):
    raise Exception(f"marker_{expr(2)}")


def p_label(expr):
    try:
        return g_env[expr(0)]
    except KeyError:
        raise Exception(1, f"Error: variable {expr(0)} not declared.")


def p_print(expr):
    print(expr(1))

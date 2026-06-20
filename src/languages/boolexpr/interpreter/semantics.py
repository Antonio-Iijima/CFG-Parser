g_env = set()



def p_program_1(expr):
    print(expr(0))
    return expr(2)


def p_boolexpr(expr):
    global g_env

    g_env = set(expr(1))

    return expr(3)


def p_expr_0(expr):
    return expr(0) or expr(2)

def p_and_0(expr):
    return expr(0) and expr(2)


def p_not_0(expr):
    return not expr(1)

def p_not_2(expr):
    return expr(0) in g_env


def p_literal(expr):
    return expr(0) == 't'

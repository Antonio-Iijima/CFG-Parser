def p_program(expr):
    print(expr(0))

def p_e_0(expr):
    return expr(0) + expr(2)

def p_e_1(expr):
    return expr(0) - expr(2)

def p_value(expr):
    return int(expr(0))

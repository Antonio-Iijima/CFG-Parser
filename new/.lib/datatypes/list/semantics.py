def p_list_0(expr):
    return []

def p_list_1(expr):
    return list(expr(1))

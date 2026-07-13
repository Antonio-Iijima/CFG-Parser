def p_tuple_0(expr):
    return ()

def p_tuple_1(expr):
    return tuple(expr(1))

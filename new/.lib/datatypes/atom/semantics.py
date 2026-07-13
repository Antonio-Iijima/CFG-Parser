def p_atoms_0(expr):
    return (expr(0), )

def p_atoms_1(expr):
    return (expr(0), *expr(2))

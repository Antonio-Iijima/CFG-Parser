def p_letters_0(expr):
    return str(expr(0))

def p_letters_1(expr):
    return f"{expr(0)}{expr(1)}"

def p_chars_0(expr):
    return str(expr(0))

def p_chars_1(expr):
    return f"{expr(0)}{expr(1)}"

def p_string(expr):
    return str(expr(1))

def p_add(a, b): return a + b
def p_subtract(a, b): return a - b
def p_multiply(a, b): return a * b
def p_idivide(a, b): return a // b
def p_fdivide(a, b): return a / b
def p_factor(a): return (a)
def p_exp(a, b): return a ** b
def p_float(a, b): return float(f"{a}.{b}")
def p_int(a, b): return int(f"{a}{b}")
def p_digit(a): return int(a)


def p_slist(a, b): return a, b
def p_symbolexpr(a): return a

### META-PROCEDURES ###


def applicative(func):
    def wrapper(*args):
        return func(*map(evaluate, args))

    wrapper.__qualname__ = f"{func.__name__.removeprefix("f_")}"
    return wrapper


### PROCEDURES ###


@applicative
def f_add(a, b):
    return a + b

@applicative
def f_sub(a, b):
    return a - b

@applicative
def f_mult(a, b):
    return a * b

@applicative
def f_fdiv(a, b):
    return a / b

@applicative
def f_idiv(a, b):
    return a // b

@applicative
def f_exp(a, b):
    return a ** b

@applicative
def f_mod(a, b):
    return a % b

@applicative
def f_le(a, b):
    return a < b

@applicative
def f_leq(a, b):
    return a <= b

@applicative
def f_ge(a, b):
    return a > b

@applicative
def f_geq(a, b):
    return a >= b

@applicative
def f_eq(a, b):
    return a == b

# is applicative, but handled in lookup
def f_cxr(x: str, output: list) -> any:
    """Tail-recursive evaluation of `cxr` expressions (arbitrary combinations of `car` and `cdr`)."""
    if not x: return output
    elif x.endswith("a"): return f_cxr(x.removesuffix("a"), output[0])
    elif x.endswith("d"): return f_cxr(x.removesuffix("d"), output[1:])

def f_quote(x):
    return x

@applicative
def f_eval(x):
    return evaluate(x)

def f_lambda(params, body):
    
    @applicative
    def λ(*args):
        g_env.append({ param : arg for param, arg in zip(params, args) })
        value = evaluate(body)
        g_env.pop()
        return value
    
    return λ

def f_define(name, body):
    g_env[-1][name] = evaluate(body)

def f_ternary(a, b, c):
    return evaluate(b) if evaluate(a) else evaluate(c)

def f_cond(*options):
    for option in options:
        condition, body = option
        if condition == "else" or evaluate(condition): return evaluate(body)


### ENVIRONMENT & BUILTINS ###


g_aliases = {
    "+" : "add",
    "-" : "sub",
    "*" : "mult",
    "/" : "fdiv",
    "//" : "idiv",
    "**" : "exp",
    "%" : "mod",
    "?" : "ternary",
    "<" : "le",
    "<=" : "leq",
    ">" : "ge",
    ">=" : "geq",
    "==" : "eq",
}

g_env = [
    { name.removeprefix("f_") : procedure for name, procedure in globals().items() if name.startswith("f_") }
]


### OUTPUT ###


def toLisp(s: list|str) -> str:
    return f"({" ".join((toLisp(e) for e in s))})" if isinstance(s, list) else str(s)


### SEMANTICS ###


def p_program_0(expr):
    value = evaluate(expr(0))
    if value is not None: print(toLisp(value))

def p_program_1(expr):
    p_program_0(expr)
    expr(1)


def p_lisp_expr_0(expr):
    return ["quote", expr(1)]


def p_list_0(expr):
    return []

def p_list_1(expr):
    return list(expr(1))


def p_elems_0(expr):
    return (expr(0), )

def p_elems_1(expr):
    return (expr(0), *expr(1))


### INTERPRETER ###


def isatom(expr): return not isinstance(expr, list)

def islist(expr): return isinstance(expr, list)

def isnull(expr): return expr == []

def isliteral(expr): return isinstance(expr, (int, float, bool))

def isprocedure(expr): return isinstance(expr, type(callable))


def lookup(var):
    from re import fullmatch

    # follow operator aliases (e.g. + : "add")
    var = g_aliases.get(var, var)

    # prioritize car/cdr operators
    if fullmatch(r"c[ad]+r", var):
        return lambda expr: f_cxr(var[1:-1], evaluate(expr))

    # try to find declared or builtin values / procedures
    for scope in reversed(g_env):
        val = scope.get(var, LookupError)
        if not (val == LookupError):
            return val

    # otherwise not found
    raise Exception(1, f"variable {var} not found.")


def evaluate(expr):

    if isatom(expr):
        
        # literals evaluate to themselves
        if isliteral(expr): return expr
        
        # lookup everything else in the environment
        return lookup(expr)

    # lists are treated as function applications by default
    elif islist(expr):

        # empty list evaluates to itself
        if isnull(expr): return expr
        
        # Evaluate operators/builtins
        return evaluate(expr[0])(*expr[1:])

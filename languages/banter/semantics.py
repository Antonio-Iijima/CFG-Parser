g_env = {}
g_markers = {}



class Goto(Exception): pass
class ReturnValue(Exception): pass



def find_markers(node, path: list = None) -> None:
    """Find paths to all marker statements in program and store in `g_markers`."""

    if path is None: path = []

    if not isinstance(node, str):
        if (str(node) == "MARKER"):
            g_markers[node(1)] = path
            find_markers(node[3], path + [3])
        else:
            for i, child in enumerate(node):
                find_markers(child, path + [i])


def sequence(node, path) -> list:
    """Build evaluation path of expression from a given marker statement onwards."""

    if (path == []):
        return [node[3]]
    else:
        i = path[0]
        return sequence(node[i], path[1:]) + list(node[i+1:])


def p_program(expr):
    program = expr[0]
    nodes = [program]
    
    find_markers(program)

    while nodes:
        try: out = nodes.pop(0)()

        except ReturnValue as e:
            print(e.args[0])
            quit()
        
        except Goto as e:
            nodes = sequence(program, g_markers[e.args[2]])
        
    return out
    

def p_statements_1(expr):
    expr(0); expr(2)


def p_assignment(expr):
    g_env[expr(1)] = expr(3)


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
    raise ReturnValue(expr(1))


def p_goto(expr):
    raise Goto(expr(2))


def p_marker(expr):
    expr(3)


def p_print_0(expr):
    print(expr(1))

def p_print_1(expr):
    print()


def p_label(expr):
    try:
        return g_env[expr(0)]
    except KeyError:
        raise UnboundLocalError(f"variable {expr(0)} not declared.")

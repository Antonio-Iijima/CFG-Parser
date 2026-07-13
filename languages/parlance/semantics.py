g_env = {}
g_markers = {}
g_program = None



def find_marker(destination) -> any:
    """Finds path to a provided destination marker statement; caches in `g_markers`. Returns the destination."""

    def search(node, path):
        if not isinstance(node, str):
            if (str(node) == "MARKER"):

                try:
                    mark = node(1)
                except Exception as e:
                    if e.args[0] == 1 and e.args[1].endswith("not declared."):
                        mark = None
                    else:
                        raise e
                
                if mark == destination:
                    g_markers[mark] = path
                else:
                    search(node[3], path + [3])
            else:
                for i, child in enumerate(node):
                    search(child, path + [i])

    if not (destination in g_markers): 
        search(g_program, [])
    
    return destination


def sequence(node, path) -> list:
    """Build evaluation path of expression from a given marker statement onwards."""

    if (path == []):
        return [node[3]]    
    else:
        i = path[0]
        return sequence(node[i], path[1:]) + list(node[i+1:])


def p_program(expr):
    global g_program
    
    g_program = expr[0]
    nodes = [g_program]

    while nodes:
        try:
            out = nodes.pop(0)()
        
        except Exception as e:
            if e.args[:2] == (2, "goto"):
                path = g_markers.get(e.args[2])
                if path is None:
                    raise Exception(1, f"marker '{e.args[2]}' not found.")
                nodes = sequence(g_program, path)
            else: raise e
    
    return out
    

def p_statement_list_1(expr):
    expr(0)
    expr(2)


def p_label(expr):
    try:
        return g_env[expr(0)]
    except KeyError:
        raise Exception(1, f"variable {expr(0)} not declared.")

def p_bool(expr):
    return expr(0) == "True"


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
    raise Exception(0, expr(1))

def p_return_1(expr):
    raise Exception(0)


def p_goto(expr):
    raise Exception(2, "goto", find_marker(expr(2)))

def p_marker(expr):
    expr(3)


def p_print_0(expr):
    print(expr(1))

def p_print_1(expr):
    print()


def p_listexpr(expr):
    try:
        return expr(0)[expr(2)]
    except IndexError:
        raise Exception(1, f"index {expr(2)} out of range")


def p_slice_0(expr):
    return expr(0)

def p_slice_1(expr):
    
    a, b = None, None
    
    match len(expr):
        case 2:
            if str(expr[0]) == "INDEX":
                a = expr(0)
            else:
                b = expr(1)
        case 3:
            a, b = expr(0), expr(2)

    return slice(a, b)

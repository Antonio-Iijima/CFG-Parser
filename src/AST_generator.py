from utils import *

from os.path import exists



REQUIREMENTS = set()
DEFAULTS = {
    "alt" : "|",
    "lbrace" : "<",
    "rbrace" : ">",
    "production" : "::="
}



def build_grammar(path: str) -> tuple[list, list]:
    """
Recursively build a complete set of grammar rules from path.

:param str path: Path to a directory containing at least a `syntax.txt` file, and any dependencies.

:return: Returns a tuple containing two lists: the macros and the rules.
    """

    macros, rules = [], []
    dependency_macros, dependency_rules = [], []
    symbols = DEFAULTS.copy()

    if not path in REQUIREMENTS:
        REQUIREMENTS.add(path)

        with open(f"{path}/syntax.txt") as file:
            syntax = preprocess_text(file)

            for line in syntax:

                # Change alternation symbol
                if line.startswith("#set"):
                    _, option, symbol = line.split()

                    symbols[option] = DEFAULTS[option] if symbol == "default" else symbol

                # Expand #require lines into the grammars of their modules
                elif line.startswith("#require"):
                    # Remove #require line and enumerate direct dependencies (i.e. dependencies specified in the #require line) 
                    _, category, *dependencies = line.split()
                    
                    if not category in ("macro", "rule"): raise SyntaxError(f"Invalid #require location.")

                    dependencies = [
                        dependency.removesuffix(",").strip() for dependency in dependencies if dependency.strip()
                    ]
                    
                    # General dependency list will be expanded to include all indirect dependencies (i.e. math from math.infix)
                    for dependency in dependencies:
                        dependency = dependency.split(".")
                        for i, _ in enumerate(dependency):
                            dependency_path = f"{LIB_PATH}/{category}s/{'/'.join(dependency[:i+1])}"

                            m, r = build_grammar(dependency_path)
                            dependency_macros = m + dependency_macros
                            dependency_rules = r + dependency_rules
                
                # Process rules/macros in top-level file            
                else:
                    rule, alternatives = line.split(symbols["production"])
                    rule, alternatives = split_pattern(rule), [split_pattern(pattern) for pattern in alternatives.split(symbols["alt"])]
                    
                    if len(rule) == 2:
                        macros.append([rule, alternatives])
                    else:
                        rules.append([rule, alternatives])

    return (
        macros + dependency_macros,
        rules + dependency_rules
    )


def process_syntax(path: str) -> dict:
    from rich import print
    from main import dFlag

    grammar = {}
    macros = {}
    parameters = {}
    
    prepend, append = build_grammar(path)
    syntax = prepend + append

    if dFlag: print(syntax)

    REQUIREMENTS.remove(path)
    
    for rule, alternatives in syntax:
        

        # Match macro declaration and add params to dict
        if len(rule) == 2:
            rule, params = rule[0][1:-1], rule[1][1:-1].split()
            macros[rule] = alternatives[0]
            parameters[rule] = params
            continue
        
        rule = rule[0][1:-1]
        
        # Prep rule entry; if rule already exists, continue to add alternatives
        grammar[rule] = grammar.get(rule, [])

        for pattern in alternatives:
            expanded_pattern = []

            i = 0
            while i < len(pattern):
                current = pattern[i]
                next = pattern[i+1] if i < len(pattern)-1 else None

                # Match macro application
                if (
                    not (next == None)
                    and current.startswith("<")
                    and current.endswith(">")
                    and next.startswith("[")
                    and next.endswith("]")
                ):
                    operation, args = current[1:-1], next[1:-1].split()

                    # Macro application is a simple pattern replacement of [param] with arg
                    for param, arg in zip(parameters[operation], args):
                        expanded_pattern.extend([arg if e == f"[{param}]" else e for e in macros[operation]])
                        i += 2
                
                # Otherwise match regular token
                else:
                    expanded_pattern.append(current)
                    i += 1

            grammar[rule] = grammar.get(rule) + [expanded_pattern]

    for dependency in sorted(REQUIREMENTS): print(dependency)
    
    from main import dFlag
    if dFlag:
        print()
        print(grammar)
    
    return grammar


def show_grammar(grammar: dict) -> None:
    offset = max(len(p) for p in grammar)

    for p, r in grammar.items(): 
        print(f"<{p}>{" " * (offset - len(p))} ::= {" | ".join("".join(s) for s in r)}")
    
    return offset


def generate_AST(path: str) -> None:
    """
Generates an AST from a context-free grammar.
    
:param str path: Path to a folder containing at least a `syntax.txt` file.
    """

    print("Compiling grammar...")
    print()
    GRAMMAR = process_syntax(path)
    print()
    
    offset = show_grammar(GRAMMAR)

    TERMINALS = set(
        token
                for alternatives in GRAMMAR.values()
            for pattern in alternatives
        for token in pattern if is_terminal(token)
        )

    AST_text = f"""'''!!! THIS FILE IS AUTOMATICALLY GENERATED - PLEASE DO NOT MODIFY !!!'''      



from parser import Rule



##### ABSTRACT SYNTAX TREE #####


"""

    for (rule, alternatives) in GRAMMAR.items():

        docstring = f"\n{" "*(len(rule)+5)}| ".join(" ".join(pattern) for pattern in alternatives)
        AST_text += f"""
class {embed_nonterminal(rule)}(Rule): 
    '''```
<{rule}> ::= {docstring}
    ```'''
"""

    AST_text += f"""

        
##### GRAMMAR #####


    
GRAMMAR = {{
    {",\n    ".join(f'''{embed_nonterminal(rule)}{" " * (offset - len(rule))} : [{
        ",".join(f"[{", ".join(embed_nonterminal(s) if is_nonterminal(s) else f"'{s}'" for s in alternative)}]"
                for alternative in alternatives)}]'''
                    for rule, alternatives in GRAMMAR.items())}
}}



##### USEFUL VARIABLES #####


FIRST = list(GRAMMAR)[0]

K = {max(map(len, (pattern for alternatives in GRAMMAR.values() for pattern in alternatives)))}

EPSILON = "ε"

SIGMA = "ς"

TERMINALS = {TERMINALS}

TOKENS = TERMINALS.union(GRAMMAR.keys())

EXPECTED_TOKENS = {{ token : [] for token in TOKENS }}

EXPECTED_PATTERNS = {{ token : [] for token in TOKENS }}

EPSILA: set = {{EPSILON}}

ACCEPT_NULL = {["ε"] in list(GRAMMAR.values())[0]}



##### HELPER FUNCTIONS #####



def retype(x): return type(x) if isinstance(x, Rule) else x


def expected_patterns(x) -> tuple[Rule, int, list]: return EXPECTED_PATTERNS[retype(x)]


def nullable(x): return retype(x) in EPSILA


def expects(previous: Rule|str, next: str|None) -> bool:
    '''Check if `previous` expects `next` or `previous` is `None`.'''
    return previous == None or retype(next) in EXPECTED_TOKENS.get(retype(previous), [])


def expand_expected(token, x):
    not x in EXPECTED_TOKENS[token] and EXPECTED_TOKENS[token].append(x)

    for alternative in GRAMMAR.get(x, []):
        for y in alternative:
            if not y in EXPECTED_TOKENS[token]:
                expand_expected(token, y)
            if not y in EPSILA: break



##### GRAMMAR POSTPROCESSING / EXPANSION #####



# Collect nullable rules (i.e. rules that can be expanded from EPSILON)
count = 0
while count < len(EPSILA):
    for rule, alternatives in GRAMMAR.items():
        for pattern in alternatives:
            if (
                len(pattern) == 1
                and pattern[0] in EPSILA
                and rule not in EPSILA
            ):
                EPSILA.add(rule)
    count += 1
del count


# Grammar post-processing/expansion
for rule, alternatives in GRAMMAR.items():
    GRAMMAR[rule] = []
    
    for variant, pattern in enumerate(alternatives):

        # Expand nullable patterns
        expanded_null_patterns = [[]]
        for i, token in enumerate(pattern):
            if not token == EPSILON:
                expanded_null_patterns = list(state + [token] for state in expanded_null_patterns)
                if nullable(token):
                    expanded_null_patterns += list(state[:-1] for state in expanded_null_patterns)

        for expanded_null_pattern in expanded_null_patterns:
            if expanded_null_pattern and not (
                expanded_null_pattern in GRAMMAR[rule]
                or len(expanded_null_pattern) == 1 and expanded_null_pattern[0] == rule
            ):
                GRAMMAR[rule].append([variant] + expanded_null_pattern)

# Only construct expected tokens/patterns with the full expansion of the grammar
for rule, alternatives in GRAMMAR.items():                
    for pattern in sorted(alternatives, key=len):
        variant = pattern.pop(0)

        # Expand expected patterns 
        for token in pattern:
            if not (rule, variant, pattern) in EXPECTED_PATTERNS[token]: 
                EXPECTED_PATTERNS[token].append((rule, variant, pattern))

for rule, alternatives in GRAMMAR.items():                
    for pattern in alternatives:
    
        # Expand expected tokens
        for i, token in enumerate(pattern[:-1]):
            expand_expected(token, pattern[i+1])
"""


    with open("AST.py", "w") as file:
        file.write(AST_text)

    print()
    with open("eval.py", "w") as file:
        print("Generating eval...")
        print()
        file.write(generate_eval(path))
    
    print()
    print("Done!")
 


def generate_eval(main_path: str) -> str:
    # AST-bound operations should be prefixed with 'p_'; 
    # global functions and variables (e.g. the environment) with 'g_'

    eval_text = f"""'''!!! THIS FILE IS AUTOMATICALLY GENERATED - PLEASE DO NOT MODIFY !!!'''

    

from parser import Rule
"""
    
    
    for folder in REQUIREMENTS:
        if folder.startswith(f"{LIB_PATH}/macros"): continue
        else:
            path = f"{folder}/semantics.py"
            if not exists(path): print(f"WARNING: semantics not found in dependency {folder}.")
            else:
                with open(path) as file:
                    eval_text += f"""


##### DEPENDENCY: {folder} #####



""" + file.read()
                    

    semantics = main_path + "/semantics.py"
    if not exists(semantics): print(f"WARNING: semantics not found in main {main_path}.")
    else:
        with open(semantics) as file:
            eval_text += f"""


##### MAIN: {main_path} #####



""" + file.read()


    eval_text += f"""


##### EVAL #####



def null(x): return None


def get_function(AST: Rule):
    return (
        globals().get(f"{{AST.fname}}_{{AST.variant}}")
        or globals().get(AST.fname)
        or null
    )


def evaluate(AST: Rule):
    return (
        get_function(AST)(list(map(evaluate, AST.children))) if isinstance(AST, Rule)
        else AST
    )
"""

    return eval_text

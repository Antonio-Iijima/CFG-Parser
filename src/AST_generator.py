from utils import *

from os.path import exists



def process_syntax(syntax: list[str]) -> tuple[dict, set]:
    from rich import print

    grammar = {}
    macros = {}
    parameters = {}
    
    prepend, append = [], []
    requirements = set()

    # Identify any required libraries.
    while syntax and syntax[0].startswith("#require"):

        # Handle comma-separated multiple dependencies and nested dependencies

        # Split declaration of the form: #require (macro|rule) <name>[, <name>]*
        _, category, *dependencies = syntax.pop(0).split()
        dependencies = [dep.removesuffix(",").strip() for dep in dependencies if dep.strip()]
        
        # Add parents of nested modules, e.g. #require rule math.infix
        for i, dependency in enumerate(dependencies):
            if "." in dependency:

                # Lowest level folder; modify in-place
                dependency = dependency.split(".")
                dependencies[i] = "/".join(dependency)

                # Also require all higher level folders to be processed later
                for j, _ in enumerate(dependency):
                    submodule = "/".join(dependency[:j+1])
                    if f"#require {category} {submodule}" not in requirements: 
                        syntax.insert(0, f"#require {category} {submodule}")

            folder = dependencies[i]

            declaration = f"#require {category} {folder}"

            # Skip dependency if already met
            if declaration in requirements: continue

            requirements.add(declaration)
            
            # Iterate through dependencies: math, spacing, &c.
            with open(f".lib/{category}s/{folder}/syntax.txt") as file:
                lines = preprocess_text(file.read().splitlines())

                while lines and lines[0].startswith("#require"):

                    # Again, skip dependency if already met
                    if lines[0] in requirements: lines.pop(0); continue

                    # Otherwise we want to process as another dependency
                    syntax.insert(0, lines.pop(0))

                # Prepend macros, append rules
                match category:
                    case "macro": prepend += lines
                    case "rule": append += lines
                    case _: raise SyntaxError(f"Invalid #require location.")
        
    syntax = prepend + syntax + append

    for line in syntax:
        rule, alternatives = line.split("::=")
        rule, alternatives = split_pattern(rule), [split_pattern(pattern) for pattern in alternatives.split("|")]
        

        # Add params to dict
        if len(rule) == 2:
            rule, params = rule[0][1:-1], rule[1][1:-1].split()
            macros[rule] = alternatives[0]
            parameters[rule] = params
            continue
        
        rule = rule[0][1:-1]
        
        # Prep rule entry
        grammar[rule] = []

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

    for dependency in sorted(requirements): print(dependency)
    
    from main import dFlag
    if dFlag:
        print()
        print(grammar)
    
    return grammar, requirements


def process_semantics(semantics: str) -> str:
    """Current implementation does nothing."""
    return semantics


def show_grammar(grammar: dict) -> None:
    offset = max(len(p) for p in grammar)

    for p, r in grammar.items(): 
        print(f"{p}{" " * (offset - len(p))} ::= {" | ".join("".join(s) for s in r)}")
    
    return offset


def generate_AST(syntax: list[str], semantics, debug: bool = False) -> set:
    """Generates an AST from an EBNF grammar (BNF with `|` for convenience) for context-free languages."""

    print("Compiling grammar...")
    print()
    GRAMMAR, REQUIREMENTS = process_syntax(syntax)
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



##### CONSTANTS #####



K = {max(map(len, (pattern for alternatives in GRAMMAR.values() for pattern in alternatives)))}

EPSILON = "ε"

SIGMA = "ς"

SPECIAL = {{EPSILON, SIGMA}}

TERMINALS = {TERMINALS}

TOKENS = TERMINALS.union(GRAMMAR.keys())

OPERATORS = {{{", ".join(embed_nonterminal(t) if is_nonterminal(t) else f"'{t}'" for t in set(
        token 
                for alternatives in GRAMMAR.values()
            for pattern in alternatives
        for token in pattern if (
            len(pattern) > 1
            and is_terminal(token)
            and (not token == pattern[-1])
            and any(is_nonterminal(x) for x in pattern)
        )))}}}

EXPECTED_TOKENS = {{ token : [] for token in TOKENS }}

EXPECTED_PATTERNS = {{ token : [] for token in TOKENS }}

EPSILA = {{EPSILON}}



##### HELPER FUNCTIONS #####



def retype(x): return type(x) if isinstance(x, Rule) else x


def expected_patterns(x): return EXPECTED_PATTERNS[retype(x)]


def nullable(x): return retype(x) in EPSILA


def is_expected(e, x: Rule|str) -> bool:
    '''Check if `e` is expected by `x` or `e` is `EPSILON` and x expects a nullable.'''
 
    expected = EXPECTED_TOKENS.get(retype(x), [])
    return expected and retype(e) in expected or (e == EPSILON and any(nullable(c) for c in expected))


def expand_expected(token, x):
    EXPECTED_TOKENS[token].append(x)

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
    for pattern in alternatives:

        # 1) Expand expected tokens
        for i, token in enumerate(pattern[:-1]):
            expand_expected(token, pattern[i+1])

        # 2) Expand nullable patterns
        null = list(map(lambda x: EPSILON if nullable(x) else x, pattern))
        if not null == pattern:
            GRAMMAR[rule].append(null)

        # 3) Expand expected patterns 
        for token in pattern:
            if not (rule, pattern) in EXPECTED_PATTERNS[token]: 
                EXPECTED_PATTERNS[token].append((rule, pattern))
"""


    with open("AST.py", "w") as file:
        file.write(AST_text)

    print()
    with open("eval.py", "w") as file:
        print("Generating eval...")
        print()
        file.write(generate_eval(semantics, REQUIREMENTS))
    
    print()
    print("Done!")
 


def generate_eval(semantics: str, requirements: set[str]) -> str:
    # AST-bound operations should be prefixed with 'p_'; 
    # global functions and variables (e.g. the environment) with 'g_'

    eval_text = f"""'''!!! THIS FILE IS AUTOMATICALLY GENERATED - PLEASE DO NOT MODIFY !!!'''

    

from parser import Rule
"""
    
    
    for requirement in requirements:
        _, category, *dependencies = requirement.split()

        if category == "macro": continue
        for filename in dependencies:
            folder = f"{LIB_PATH}/{category}s/{filename}"
            path = f"{folder}/semantics.py"
            if not exists(path): print(f"WARNING: dependency semantics {folder} not found.")
            else:
                with open(path) as file:
                    eval_text += f"""


##### DEPENDENCY: {folder} #####



""" + file.read()
                    

    if not exists(semantics): print(f"WARNING: main semantics {semantics} not found.")
    else:
        with open(semantics) as file:
            eval_text += f"""


##### MAIN: {semantics.removesuffix("/semantics.py")} #####



""" + file.read()


    eval_text += f"""


##### EVAL #####



def evaluate(AST):    
    return (
        globals().get(AST.fname, lambda x: None)(list(map(evaluate, AST.children))) if isinstance(AST, Rule)
        else "" if AST == None 
        else AST
    )
"""

    return eval_text

from utils import *
from rich import print



class Rule:
    def __init__(self, children):
        self.children = children

        
    def __hash__(self):
        return self.name.__hash__()

        
    def __repr__(self):
        return f"{self.name[1:-1]}"
            
                
    def __str__(self):
        return "".join(map(str, self.children))



def parse(expr: str) -> Rule:
    from AST import GRAMMAR, is_expected, retype, OPERATORS
    from main import dFlag

    expr = tokenize(expr)

    # A list of states organized by step (i.e. number of processed tokens).
    # For each step, there is a list of states (which is a list of tokens or nodes).
    current_states = [[]]
    future_states = []

    if dFlag:
        from AST import EXPECTED_TOKENS
        print(EXPECTED_TOKENS)
    
    # For each token, advance a step and begin processing states
    for token in expr:

        # For each state at the previous step, 
        # add to the current step with the newest token
        current_states = list(map(lambda x: x + [token], current_states))
        if token in OPERATORS: continue

        to_be_reduced = list(current_states)

        if dFlag: print("Current states", current_states)

        # We need to reduce all the new states at the current step

        # Select a state from the current set for reducible states,
        # and add the reduction to both the set of states at this step, and
        # the set of further reducible states.
        while to_be_reduced:
            state = to_be_reduced.pop()

            for rule, alternatives in GRAMMAR.items():
                for pattern in alternatives:
                    idx = -len(pattern)

                    # Reduce only states that can produce a valid parse
                    if (
                        retype(state[-1]) in pattern
                        and -idx == len(state[idx:]) 
                        and compare(state[idx:], pattern)
                    ):
                        reduced = state[:idx] + [rule(state[idx:])]
                        
                        to_be_reduced.append(reduced)

                        # Proceed with only states that can produce a valid parse
                        if (
                            (
                                len(reduced) == 1
                                and isinstance(reduced[0], Rule)
                            )
                            or (
                                len(reduced) == 2 
                                and is_expected(reduced[-1], reduced[-2])
                            )
                            or (len(reduced) > 2 
                                and is_expected(reduced[-1], reduced[-2])
                                and is_expected(reduced[-2], reduced[-3])
                            )
                        ):
                            future_states.append(reduced)

        current_states, future_states = future_states or current_states, []

        if dFlag: 
            print("Future states", current_states)
            print()

    # Filter for accepting state; if not found return None explicitly
    for state in current_states:
        if len(state) == 1 and isinstance(state[0], list(GRAMMAR.keys())[0]):
            return state[0]
    return None



def validate(expr: str) -> str:
    parsed = parse(expr)
    return f"{{expr}} is not a valid expression." if (parsed == None) else f"{{parsed}} is a valid {{parsed.name}} expression."



def tokenize(string: str) -> list:
    from AST import TERMINALS

    tokens = []
    while string:
        for terminal in TERMINALS:
            if string.startswith(terminal) and not terminal == "":
                tokens.append(terminal)
                string = string.removeprefix(terminal)
                break
        else: raise SyntaxError(f"unrecognized token in input '{string}'")

    return tokens

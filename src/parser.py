from utils import *
from rich import print



class Rule:
    def __init__(self, children):
        from AST import EPSILON, SIGMA

        self.__name__ = type(self).__name__
        self.fname = f"p_{self.__name__.lower()}"
        self.children = [{EPSILON : "", SIGMA : " "}.get(c, c) for c in children]

        
    def __hash__(self):
        return self.__name__.__hash__()

        
    def __repr__(self):
        return f"{self.__name__}"
            
                
    def __str__(self):
        return "".join(map(str, self.children))



def parse(expr: str) -> Rule:
    from AST import (
        is_expected, expected_patterns,
        GRAMMAR, K, EPSILON, EXPECTED_TOKENS, EXPECTED_PATTERNS
    )
    from main import dFlag

    tokens = tokenize(expr)

    # A list of states organized by step (i.e. number of processed tokens).
    # For each step, there is a list of states (which is a list of tokens or nodes).
    current_states = [[]]
    future_states = []

    if dFlag:
        print("EXPECTED TOKENS:")
        for key in sorted(EXPECTED_TOKENS.keys(), key=comparative):
            print(f"{key} :: {EXPECTED_TOKENS[key]}")
            print()
        
        print()
        
        print("EXPECTED PATTERNS:")
        for key in sorted(EXPECTED_PATTERNS.keys(), key=comparative):
            print(f"{key} :: {EXPECTED_PATTERNS[key]}")
            print()

    # For each token, advance a step and begin processing states
    for i, token in enumerate(tokens):
        lookahead = tokens[i+1:K+i+1]

        # For each state at the previous step, 
        # add to the current step with the newest token
        current_states = list(map(lambda x: x + [token], current_states))
        
        reducible_states = list(current_states)

        if dFlag: print("Current states", current_states)

        # We need to iteratively reduce all states as far as possible,
        # adding valid future states to the list as appropriate 
        while reducible_states:

            state = reducible_states.pop()
            
            if dFlag: print("State", state)

            for (rule, pattern) in expected_patterns(state[-1]):

                # We want to ignore epsilons in the pattern since epsilon is not a readable token.
                idx = len(state) - sum(1 for e in pattern if not e == EPSILON)

                reducible = state[idx:] # Will be an empty list if pattern == [EPSILON].

                # Reduce only if pattern matches the reducible part of the state (excluding epsilon)
                if compare(reducible, pattern):
                    reduced = state[:idx] + [rule(reducible)]

                    if dFlag: print("Reduced", reduced)

                    reducible_states.append(reduced)
                    
                    # Accept as future state if any of the following:
                    # 1) EOI
                    # 2) Correct expected next token
                    # Whole sequence must also be valid. 
                    if (
                        (
                            (not lookahead)
                            or is_expected(lookahead[0], reduced[-1])
                        ) and (
                            all(idx == k or is_expected(reduced[idx-k], reduced[idx-k-1]) 
                                for k in range(min(K, len(reduced))))
                        )
                    ):
                        if dFlag: print("Future", reduced)
                        future_states.append(reduced)
                
                # If the current pattern does not match, but could match if more tokens
                elif state[-1] in pattern: future_states.append(state)
                        
        current_states, future_states = future_states or current_states, []

        if dFlag: 
            print("Future states", current_states)
            print()
            
    # Filter for accepting states; if not found return None explicitly.
    acceptable_states = [ 
        state[0] for state in current_states if (
            len(state) == 1 
            and isinstance(state[0], list(GRAMMAR.keys())[0])
        )
    ]

    if dFlag:
        print()
        print(list(map(str, acceptable_states)))

    return acceptable_states[0] if acceptable_states else None
    

def tokenize(string: str) -> list:
    from AST import TERMINALS, SIGMA

    terminals = sorted(TERMINALS, reverse=True)
    tokens = []
    while string:
        for terminal in terminals:
            
            if string.startswith(" "):
                tokens.append(SIGMA)
                string = string.removeprefix(" ")
                break

            if string.startswith(terminal) and not terminal == "":
                tokens.append(terminal)
                string = string.removeprefix(terminal)
                break

        else: raise SyntaxError(f"unrecognized token in input '{string}'")

    return tokens

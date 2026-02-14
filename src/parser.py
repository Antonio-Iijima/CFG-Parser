from utils import *
from datatypes import *

from rich import print



def parse(expr: str) -> tuple[Rule, int]:
    from AST import (
        expects, expected_patterns,
        FIRST, K, 
        EXPECTED_TOKENS,
        EXPECTED_PATTERNS, 
        ACCEPT_NULL
    )
    from main import dFlag

    tokens = tokenize(expr)
    
    # Accept empty strings immediately only if permitted by the grammar.
    if tokens == [] and ACCEPT_NULL: return (FIRST(0, []), 0)

    # Everything is a dict now, because they are
    # a) fast
    # b) ordered 
    current_states = OrderedSet((State(),))
    future_states = OrderedSet()

    # Memoize everything; to be implemented
    memoized: dict[str, list] = {}

    if dFlag:
        print("EXPECTED TOKENS:")
        for key, expected in EXPECTED_TOKENS.items():
            print(key, end=" :: ")
            print(expected)
            print()

        print()
        
        print("EXPECTED PATTERNS:")
        for key, expected in EXPECTED_PATTERNS.items():
            print(key, end=" :: ")
            print(expected)
            print()

        print()

    max_states = 0

    # For each token, advance a step and begin processing states
    for i, token in enumerate(tokens):
        max_states = max(max_states, len(current_states))
        if max_states > 2**10: raise RuntimeError(f"Too many states to consider: {max_states}")
        
        next_token = tokens[i+1] if i+1 < len(tokens) else None

        # For each state at the previous step, 
        # add to the current step with the newest token
        for state in current_states: state.append(token)
        
        reducible_states = current_states.copy()

        if dFlag: print("Current states", current_states)

        # We need to iteratively reduce all states as far as possible,
        # adding valid future states to the list as appropriate 
        while reducible_states:

            state = reducible_states.remove()
            
            if dFlag: print("State", state)

            for (rule, variant, pattern) in expected_patterns(state[-1]):
                
                idx = len(state) - len(pattern)
                reducible = state[idx:]

                # Reduce only if pattern matches the reducible part of the state.
                if compare(reducible, pattern):

                    reduced = State(state[:idx] + [rule(variant, reducible)])

                    if dFlag: print("Reduced", reduced)

                    reducible_states.add(reduced)
                    
                    # Accept as future state if the following:
                    # 1) EOI (no next token) or next token is expected
                    # 2) Each token correctly expects the next token
                    if (
                        (
                            next_token == None
                            or expects(reduced[-1], next_token)
                        ) and (
                            all(idx == k or expects(reduced[idx-k-1], reduced[idx-k]) 
                                for k in range(min(K, len(reduced))))
                        )
                    ):
                        if dFlag: print("Future", reduced)
                        future_states.add(reduced)

                # If the current pattern does not match, but could match if given more tokens.
                elif state[-1] in pattern: future_states.add(state)
                        
        current_states, future_states = future_states or current_states, OrderedSet()

        if dFlag: 
            print("Future states", current_states)
            print()
            
    # Filter for accepting states; if not found return None explicitly.
    acceptable_states: set = {
        state[0] for state in current_states if (
            len(state) == 1
            and isinstance(state[0], FIRST)
        )
    }
    
    if dFlag:
        print()
        print(list(str(state) for state in acceptable_states))

    return (acceptable_states.pop(), max_states) if acceptable_states else (None, None)
    

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

from utils import *
from datatypes import *

from rich import print



def parse(expr: str, state_limit: int = 2**10, dFlag: bool = False) -> Parsed:
    from AST import (
        expects, expected_patterns,
        FIRST, K, 
        EXPECTED_TOKENS,
        EXPECTED_PATTERNS, 
        ACCEPT_NULL
    )

    remaining_tokens = tokenize(expr)
    tokens = []

    # Accept empty strings immediately only if permitted by the grammar.
    if not remaining_tokens and ACCEPT_NULL: return Parsed(expr, FIRST(0, []), 0)

    # Everything is a dict now, because they are
    # a) fast
    # b) ordered 
    # c) unique
    current_states = OrderedSet((State(),))
    future_states = OrderedSet()

    if dFlag:
        print("EXPECTED TOKENS:")
        for key, expected in (EXPECTED_TOKENS.items()):
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

    # Track number of tokens since last space read.
    tokensSinceLastSpace = 0

    # Process tokens sequentially, pursuing all valid shift/reduce paths in parallel.
    while remaining_tokens:
        token = remaining_tokens.pop(0)

        if token == " ": 
            tokensSinceLastSpace = 0
            continue
        else: 
            tokensSinceLastSpace += 1

        # Otherwise set up to process states at this token
        tokens.append(token)

        for t in remaining_tokens:
            if not t == " ":
                next_token = t
                break
        else: next_token = None

        for state in current_states: state.append(token)
        
        reducible_states = current_states.copy()

        if dFlag: print("Current states", current_states)

        # We need to iteratively reduce all states as far as possible,
        # adding valid future states to the list as appropriate.
        while reducible_states:

            state = reducible_states.remove()
            
            if dFlag: print("State", state)

            for (rule, variant, pattern) in expected_patterns(state[-1]):

                # Strict rules cannot include spaces
                if issubclass(rule, StrictRule) and tokensSinceLastSpace < len(pattern): continue
                
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
        
        max_states = max(max_states, len(future_states))
        if max_states > state_limit: raise RuntimeError(f"Too many states to consider: {max_states}")
        
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
    
    return Parsed(expr, acceptable_states.pop(), max_states) if acceptable_states else Parsed("ERROR: Parser terminated without any accepting states.")


def tokenize(string: str) -> list:
    from AST import TERMINALS, INDENT_SENSITIVE
    INDENT = "   "
    prev_indent = 0
    curr_indent = 0

    # Remove commented lines
    lines = [line for line in string.splitlines() if not line.startswith("#")]
    
    if INDENT_SENSITIVE:
        indented = [""]*len(lines)

        for i, line in enumerate(lines):
            while line.startswith(INDENT):
                line = line.removeprefix(INDENT)
                curr_indent += 1

            diff = curr_indent - prev_indent
            while diff > 0:
                indented[i] += "INDENT"
                diff -= 1
            
            while diff < 0:
                indented[i] += "DEDENT"
                diff += 1

            indented[i] += line
            prev_indent, curr_indent = curr_indent, 0
        
        lines = indented

    original = string = "".join(lines).strip()

    terminals = sorted(TERMINALS.difference({""}), reverse=True)
    tokens = []
    comment = False

    while string:        
        comment = (comment or string.startswith("#")) and not (string.startswith("\n"))
        
        if comment: 
            string = string[1:]
            continue
        
        if string.startswith(" "):
            tokens.append(" ")
            string = string.removeprefix(" ")
            continue

        for terminal in terminals:
            if string.startswith(terminal):
                tokens.append(terminal)
                string = string.removeprefix(terminal)
                break

        else: 
            raise SyntaxError(f"index {len(original)-len(string)}: unrecognized token '{string[0]}' in input '{original}'")

    return tokens


def validate(parsed: Parsed, solution: any) -> str:
    from eval import evaluate
    
    if str(parsed) == solution: return solution
    
    result = evaluate(parsed.AST)
    
    if result == solution: return solution
    raise ValueError(f"value of {parsed} should be {solution}, but received {result or "False|None"}")

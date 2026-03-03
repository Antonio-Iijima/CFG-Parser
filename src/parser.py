from utils import *
from datatypes import *



def parse(expr: str, state_limit: int = 2**100, dFlag: bool = False) -> Parsed:
    from AST import (
        expects, expected_patterns,
        FIRST, K, 
        EXPECTED_TOKENS,
        EXPECTED_PATTERNS,
        NEWLINE_SENSITIVE
    )

    remaining_tokens = tokenize(expr)
    tokens = []

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

        if token in (" ", "\n"):
            tokensSinceLastSpace = 0
            if not (NEWLINE_SENSITIVE and token == "\n"):
                continue
        else: 
            tokensSinceLastSpace += 1

        # Otherwise set up to process states at this token
        tokens.append(token)

        next_token = get_next_token(remaining_tokens)

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
    
    if not acceptable_states: 
        raise SyntaxError("parser terminated without any accepting states.")
    
    return Parsed(expr, acceptable_states.pop(), max_states, showTree=dFlag)



def tokenize(string: str) -> list:
    from AST import TERMINALS, INDENT_SENSITIVE, INDENT
    
    lines = preprocess_input(string, INDENT_SENSITIVE, INDENT)
    
    original = string = "\n".join((line for line in lines if line.strip())).strip()

    terminals = sorted(TERMINALS, reverse=True)
    tokens = []

    while string:
        for terminal in terminals:
            if string.startswith(terminal):
                tokens.append(terminal)
                string = string.removeprefix(terminal)
                break
        else: raise SyntaxError(f"index {len(original)-len(string)}: unrecognized token '{string[0]}' in input '{original}'")
    
    # print(tokens)
    return tokens
 

def indent(INDENT: str, lines: list) -> list:
    indented = []
    curr_indent = prev_indent = 0

    for i, line in enumerate(lines):
        
        # Remove commented and empty lines
        if (not line.strip()) or line.strip().startswith("#"): 
            continue

        while line.startswith(INDENT):
            line = line.removeprefix(INDENT)
            curr_indent += 1

        if line.startswith(" "): 
            count = line.count(" ", 0, 2)
            raise IndentationError(f"invalid indent in line {i+1}: {count} extra space{"" if count == 1 else "s"}.")

        diff = curr_indent - prev_indent

        while diff < 0:
            indented[-1] += "DEDENT"
            diff += 1

        # Newline will come after DEDENTs but before INDENTS
        indented.append("")
        
        while diff > 0:
            indented[-1] += "INDENT"
            diff -= 1
            
        indented[-1] += line
        prev_indent, curr_indent = curr_indent, 0

    # Handle any final DEDENTs
    while prev_indent > 0:
        indented[-1] += "DEDENT"
        prev_indent -= 1

    return indented


def preprocess_input(string: str, indentSensitive: bool, indentation: str = "   "):
    lines = string.splitlines()

    for i, line in enumerate(lines):
        if "#" in line:
            lines[i] = line[:line.index("#")]

    return indent(indentation, lines) if indentSensitive else lines


def get_next_token(remaining: list) -> str|None:
    for t in remaining:
        if not t == " ":
            return t
    return None

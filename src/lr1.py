from AST import *
from rich import print
from rich.table import Table



class LALR_Parser:
    def __init__(self, debug: bool = False):
        self.rules = list(e for opts in GRAMMAR.values() for e in opts)
        self.nulls: set = set()
        self.automaton: dict[int, dict[Item, set]] = {}
        self.table: dict[int, dict[str|ProductionData, int]] = {}
        self.kernels: dict[Item, int] = {}
        self.first: dict[Rule] = {}

        self.debug = debug

        # for rule in GRAMMAR: self.first[rule] = self.compute_first(rule)

        self.construct_automaton({
            Item(0, ProductionData(START, "MAIN", 0, [ PROGRAM ])) : { EOI }
            })
        self.construct_table()
        
        if self.debug:
            
            print()

            print("AUTOMATON")
            print(self.automaton)
            
            print()
            
            self.show_tables()


    def isNullable(self, rule: Rule|str) -> bool:
        if isinstance(rule, Rule):
        
            if rule in self.nulls:
                return True
            
            else:
                for productionData in GRAMMAR[rule]:
                    if (
                        (productionData.pattern == []) 
                        or all(self.isNullable(token) for token in productionData.pattern if not (token == rule))
                    ): 
                        self.nulls.add(productionData.rule)
                        return True
                    
        return False


    def construct_automaton(self, kernel: dict[Item, set]) -> None:
        """Constructs the LALR automaton."""

        def merge(a: dict[Item, set], b: dict[Item, set]) -> bool:
            if a.keys() == b.keys():
                for item, lookahead in b.items():
                    a[item].update(lookahead)
                return True
            return False
            
        state = len(self.automaton)
        self.automaton[state] = self.closure(kernel)
        transitions: dict[str|type, dict[Item, set]] = {}

        for item, lookahead in self.automaton[state].items():
            if item.isReduction: continue

            if not item.current in transitions: transitions[item.current] = {}

            transitions[item.current].update({item : lookahead})

        for token in transitions:

            nextKernel = {
                Item(item.dot+1, item.production) : lookahead
                for item, lookahead in transitions[token].items()
            }

            for closure in self.automaton.values():
                if merge(closure, self.closure(nextKernel)): break
            else: 
                self.construct_automaton(nextKernel)


    def construct_table(self) -> None:
        """Constructs the LALR table."""

        for state, fromClosure in self.automaton.items():
            self.table[state] = {}

            for item, lookahead in fromClosure.items():
                if item.isReduction:

                    for token in lookahead:
                        self.table[state][token] = self.table[state].get(token, set()).union({
                            ("A", True) if (item.production.rule, token) == (START, EOI) 
                            else ("R", self.rules.index(item.production))
                        })

                else:
                    nextItem = Item(item.dot+1, item.production)
                    action = ("S" if isinstance(item.current, str) else "G")
                    
                    self.table[state][item.current] = self.table[state].get(item.current, set()).union({ 
                            (action, toState) for toState, toClosure in self.automaton.items() if nextItem in toClosure
                        })

            self.table[state] = { token : list(actions) for token, actions in self.table[state].items() }
                            
        for state, transitions in self.table.items():
            for token, actions in transitions.items():
                if len(actions) > 1:
                    actions = self.table[state][token] = sorted(actions, key=lambda tup: tup[0] == "R")
                    # print(f"CONFLICT: {len(actions)} actions in state {state} on token {token}")
                    print(f"{"/".join(action[0] for action in actions)} conflict in state {state} on token {token}")



    def closure(self, kernel: dict[Item, set]) -> dict[Item, set]:
        """Computes the closure of a given configuration."""

        items: dict[Item, set] = {}
        expansions: dict[Item, set] = {}

        for initialItem, initialLookahead in kernel.items():

            expansions[initialItem] = initialLookahead

            while expansions:

                # add the most recent rule to the expansion
                item, lookahead = expansions.popitem()

                if item.isEpsilon: continue

                items[item] = lookahead

                # if the current token is a nonterminal, we must add further expansions
                if not (item.isReduction or isinstance(item.current, str)):
                    # compute the lookahead; if no following tokens, we have A -> .B, where lookahead is a subset of follow(A)
                    lookahead = self.FIRST(item.next, initialLookahead)

                    # add new configuration;
                    # dot will always be at the beginning for a new nonterminal configuration
                    for productionData in GRAMMAR[item.current]:
                        newItem = Item(0, productionData)
                        if newItem in items:
                            items[newItem].update(lookahead)
                        else:
                            expansions[newItem] = expansions.get(newItem, set()).union(lookahead)
                            # if newItem in expansions:
                            #     expansions[newItem].update(lookahead)
                            # else:
                            #     expansions[newItem] = lookahead
                
        return items


    def FIRST(self, rules: list[Rule|str], lookahead: set = None) -> set[str]:
        def compute_first(rule: Rule, exclude: list = None) -> set:
            if rule in self.first: return self.first[rule]

            exclude = exclude or set()
            first = set()

            for productionData in GRAMMAR[rule]:
                for token in productionData.pattern:
                    if isinstance(token, str):
                        first.add(token)
                        break

                    elif token not in exclude:
                        if token not in self.first:
                            self.first[token] = compute_first(token, exclude.union({token}))
                        first.update(self.first[token])
                        if self.isNullable(token):
                            first.add(EPSILON)
                        else:
                            break

            return first


        out = set()

        for rule in rules:
            if isinstance(rule, str):
                out.add(rule)
            else:
                if rule not in self.first:
                    self.first[rule] = compute_first(rule)
                out.update(self.first[rule])

            if self.isNullable(rule): out.add(EPSILON) # add epsilon and continue processing rules
            else: break # otherwise done

        # if all rules are nullable
        else: out.update(lookahead)

        return out

            
    def parse(self, input: list[Token], symbols: list = None, state: list = None) -> Rule:
        if symbols is None: symbols = []
        if state is None: state = [0]

        if self.debug:

            print()
            
            print("FIRST")
            print(self.first)
            
            print()

            parserOutput = table(
                title="Parser Output",
                headers={
                    "Step" : {"justify" : "center"},
                    "State" : {},
                    "Symbols" : {},
                    "Input" : {"justify" : "right"},
                    "Action" : {"justify" : "center"}
                }
            )
        
        step = -1
        while input:
            step += 1

            action, data = self.table[state[-1]].get(input[0].regex, [("E", False)])[0]
            
            if self.debug:
                parserOutput.add_row(
                    str(step), 
                    " ".join(tostr(state)), 
                    " ".join(tostr(symbols)), 
                    " ".join(tostr(input)), 
                    { "A" : "ACC", "E" : "ERR" }.get(action, f"{action} {data}")
                )
 
            match action:
                
                case "S":
                    symbols.append(input.pop(0))
                    state.append(data)

                case "R":
                    production: ProductionData = self.rules[data]
                    reduction = []

                    for _ in production.pattern:
                        reduction.append(symbols.pop())
                        state.pop()
                    
                    symbols.append(production.rule(reversed(reduction), production.module, production.variant))
                    
                    # Handle goto as part of reduce action
                    action, data = self.table[state[-1]][production.rule][0]
                    if action == "G": state.append(data)
                    else: raise ParseError(f"expected goto on token {state[-1]}")

                case "A":
                    if len(symbols) == 1 and isinstance(symbols[0], PROGRAM):
                        if self.debug: print(parserOutput)
                        return symbols.pop()
                    raise ParseError("could not parse expression")
                
                case "E": 
                    expected = set({None : "EOI"}.get(item.current, item.current) for item in self.automaton[state[-1]])
                    
                    if self.debug: print(parserOutput)
                    
                    msg = f"unexpected input" \
                        + (f" {input[0].info}" if isinstance(input[0], Token) else f" {input[0]}") \
                        + f" (expected {expected})"
                    
                    raise ParseError(msg)

    
    def show_tables(self) -> None:

        categories = list(sorted(TERMINALS)) + [EOI] + list(rule for rule in GRAMMAR.keys() if not rule == START)

        self.display_table = Table(title="LALR(1) Parsing Table")
        self.display_table.add_column("State", justify="center")
        for category in categories:
            self.display_table.add_column(category if isinstance(category, str) else category.__name__, justify="center")
        for state, edges in self.table.items():
            self.display_table.add_row(str(state), *(" ".join(map(str, edges.get(edge, ("",)))) for edge in categories))

        self.display_rules = Table.grid()
        self.display_rules.title = "Rules"
        self.display_rules.add_column(style="bright_cyan")
        for i, production in enumerate(self.rules):
            rule, pattern = str(production).split("::=")
            self.display_rules.add_row(f"{i} ", rule, "::=", pattern)

        print()
        print(self.display_table)
        print()
        print(self.display_rules)
        print()

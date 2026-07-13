"""Contains datatypes used throughout the project."""



class Default:
    """Base class which handles `__eq__` if `__hash__` has been defined by the subclass."""
    def __eq__(self, other): return isinstance(other, type(self)) and self.__hash__() == other.__hash__()



class Terminal(Default):
    def __init__(self, regex: str):
        self.regex = regex

    def __hash__(self):
        return hash(self.regex)

    def __str__(self):
        return f"\"{self.regex}\""

    def __repr__(self):
        return f"r\"{self.regex}\""



class Nonterminal(Default):
    def __init__(self, rule: str):
        self.rule = rule.upper()

    def __hash__(self):
        return hash(self.rule)
    
    def __len__(self):
        return len(self.rule)

    def __str__(self):
        return self.rule

    def __repr__(self):
        return self.rule



class Production(Default):
    def __init__(self, rule: Nonterminal, module: str, variant: int, pattern: list):
        self.rule = rule
        self.module = module
        self.variant = variant
        self.pattern = pattern
        
    def __hash__(self):
        return hash((self.rule, self.module, self.variant))
    
    def __str__(self):
        return f"{self.rule} -> {" ".join(map(str, self.pattern))}"
    
    def __repr__(self):
        return f"({self.rule}, {self.module.__repr__()}, {self.variant}, {len(self.pattern)})"



class Item(Default):
    def __init__(self, dot: int, production: Production):
        self.dot = dot
        self.production = production
        self.isReduction = (dot == len(production.pattern))
        self.current = (None if self.isReduction else production.pattern[dot])
        self.next = production.pattern[dot+1:]

    def __hash__(self):
        return hash((self.dot, self.production.rule, tuple(self.production.pattern)))
    
    def __repr__(self):
        pattern = self.production.pattern[:]
        pattern.insert(self.dot, "∙")
        return f"{self.production.rule} -> {" ".join(map(str, pattern))}"



class EPSILON: pass



class START(Nonterminal):
    def __init__(self):
        super().__init__("START")



class EOI(Terminal):
    def __init__(self): 
        super().__init__(str(hash("EOI")))
        self.regex = EOI
    
    def __repr__(self): return "EOI"
    

    
class Token:
    def __init__(self, tok: str, regex: str, lineno: int, col: int):
        self.tok = tok
        self.regex = regex
        self.lineno = lineno
        self.col = col

    
    @property
    def info(self) -> str:
        return f"{self.tok.__repr__()} at line {self.lineno}, col {self.col}"


    def __str__(self):
        return self.tok
    

    def __repr__(self):
        return f"Token{self.tok, self.regex, self.lineno, self.col}"



class Rule(Default):
    def __init__(self, children: list, modulename: str = None, variant: int = 0):
        self.__name__ = type(self).__name__
        self.fname = f"p_{modulename}_{self.__name__.lower()}"
        self.variant = variant
        self.children = tuple(children)
        self.modulename = modulename


    def __eq__(self, other: 'Rule'):
        return isinstance(other, Rule) and self.__hash__() == other.__hash__()


    def __hash__(self):
        return hash((self.__name__, tuple(self.children)))


    def __repr__(self, i=0):
        return \
            "\n" + "   " * i \
            + f"{self.__name__}([{", ".join(child.__repr__() if isinstance(child, Token) else child.__repr__(i+1) for child in self.children)}]," \
            + "\n" + "   " * i \
            +  f"{self.modulename.__repr__()}, {self.variant})"
            
                
    def __str__(self):
        return self.__name__



### Custom Errors and Exceptions ###



class TableGenerationError(Exception): pass
class ValidationError(Exception): pass
class ParseError(Exception): pass

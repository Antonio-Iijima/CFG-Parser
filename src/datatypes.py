"""Contains datatypes used throughout the project."""



from utils import *



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
        self.rule = rule
        if "_" in rule: self.module, self.name = rule.rsplit("_", 1)

    def __hash__(self):
        return hash(self.rule)
    
    def __len__(self):
        return len(self.name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name



class Production(Default):
    def __init__(self, rule: Nonterminal, module: str, variant: int, pattern: list):
        self.rule = rule
        self.module = module
        self.variant = variant
        self.pattern = list(token for token in pattern if not isinstance(token, EPSILON))
        
    def __hash__(self):
        return hash((self.rule, self.module, self.variant))
    
    def __str__(self):
        return f"{self.rule} -> {lstToStr(self.pattern) if self.pattern else "\"\""}"
    
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
        return f"{self.production.rule} -> {lstToStr(pattern)}"



class SpecialTerminal(Terminal):
    def __init__(self): 
        self.__name__ = type(self).__name__
        self.regex = type(self)
    
    def __hash__(self):
        return hash(self.regex)

    def __repr__(self):
        return type(self).__name__



class EOI(SpecialTerminal):
    def __str__(self): return "$"



class EPSILON(SpecialTerminal):
    def __str__(self): return "\"\""



class START(Nonterminal):
    def __init__(self): super().__init__("MAIN_START")



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
        self.children = tuple(children)
        self.modulename = modulename
        self.variant = variant

        self.__name__ = type(self).__name__
        self.fname = f"p_{modulename}_{self.__name__}".lower()
        self.fname_var = f"{self.fname}_{self.variant}"


    def __hash__(self):
        return hash((self.__name__, self.children))


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

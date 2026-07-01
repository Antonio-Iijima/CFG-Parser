from utils import pathToFunc



class Rule:
    def __init__(self, children: list, modulename: str = None, variant: int = 0):
        self.__name__ = type(self).__name__
        self.fname = pathToFunc(modulename) + self.__name__.lower()
        self.variant = variant
        self.children = tuple(children)
        self.modulename = modulename
        self._hash = self.__name__.__hash__() + sum(child.__hash__() for child in children)
        self.depth = (1 + max((child.depth for child in self.children), default=0))


    def __eq__(self, other: 'Rule'):
        return isinstance(other, Rule) and self.__hash__() == other.__hash__()


    def __hash__(self):
        return self._hash


    def __repr__(self, i=0):
        return \
            "\n" + "   " * i \
            + f"{self.__name__}([{", ".join(child.__repr__() if isinstance(child, Token) else child.__repr__(i+1) for child in self.children)}]," \
            + "\n" + "   " * i \
            +  f"{self.modulename.__repr__()}, {self.variant})"
            
                
    def __str__(self):
        return self.__name__



class ProductionData:
    def __init__(self, rule: Rule, module: str, variant: int, pattern: list):
        self.rule = rule
        self.module = module
        self.variant = variant
        self.pattern = list(t for t in pattern if not t == EPSILON)
        self.isNull = (self.pattern == [])
        

    def __hash__(self):
        return hash((self.rule, self.module, self.variant))


    def __str__(self):
        return f"<{self.rule.__name__}> ::= {(" ".join(s if isinstance(s, str) else f'<{s.__name__}>' for s in self.pattern) if self.pattern else "ε")}"


    def __repr__(self):
        return f"""ProductionData( # {str(self)}
            {self.rule.__name__}, '{self.module}', {self.variant}, [{
                ", ".join(f"r'{token}'" if isinstance(token, str) 
                else token.__name__ for token in self.pattern)
                }])"""



class OrderedSet(dict):
    """Implements an ordered set using a `dict`. 
    `add()` and `remove()` methods provide `append()` and `pop()` functionality."""

    def __init__(self, iterable = None):
        super().__init__(dict.fromkeys(iterable) if iterable else {})


    def add(self, item: any) -> None:
        self[item] = None


    def pop(self):
        """Removes and returns the last value from the `OrderedSet`."""
        return self.popitem()[0]


    def copy(self):
        return OrderedSet(self.keys())
    

    def extend(self, iterable) -> 'OrderedSet':
        for item in iterable:
            self.add(item)

        return self
    
    
    def show(self):
        for item in self:
            print(item)


    def __repr__(self):
        return self.__str__()
    

    def __str__(self) -> str:
        return "{\n" + ",\n".join(f"   {e}" for e in self) + "\n}"
    

    def compile(self):
        return "{\n" + ",\n".join(f"   r'{e}'" for e in sorted(self, key=len, reverse=True)) + "\n}"



class Parsed:
    def __init__(self, sentence: str, AST: Rule, max_states: int):
        self.sentence = sentence
        self.AST = AST
        self.max_states = max_states


    def __str__(self):
        return self.sentence



class Token:
    def __init__(self, tok: str, regex: str, lineno: int, i: int):
        self.tok = tok
        self.regex = regex
        self.lineno = lineno
        self.i = i

        self.info = f"'{tok}' at line {lineno}, col {self.i}"
        self.depth = 1


    def __str__(self):
        return f"{self.tok}"
    

    def __repr__(self):
        return f"Token{self.tok, self.regex, self.lineno, self.i}"


class Item:
    def __init__(self, dot: int, production: ProductionData):
        self.dot = dot
        self.production = production
        self.isReduction = (dot == len(production.pattern))
        self.isEpsilon = (production.pattern == [])
        self.current = (None if self.isReduction else production.pattern[dot])
        self.next = production.pattern[dot+1:]


    def __hash__(self):
        return hash((self.dot, self.production))
    

    def __eq__(self, value):
        return isinstance(value, Item) and self.__hash__() == value.__hash__()
    

    def __repr__(self):
        out = self.production.pattern[:]
        out.insert(self.dot, "∙")
        return f"{self.production.rule.__name__} ::= {" ".join(e if isinstance(e, str) else e.__name__ for e in out)}"


 
class EOI: 
    def __init__(self): self.regex = EOI
    def __str__(self): return "$"
    def __repr__(self): return "EOI()"
    


class START: pass
class EPSILON: pass

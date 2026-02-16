class Rule:
    def __init__(self, variant: int, children: list):
        self.__name__ = type(self).__name__
        self.fname = f"p_{self.__name__.lower()}"
        self.variant = variant
        self._str = " ".join(map(str, children))
        self.children = tuple(c for c in children if c)
        self._hash = self.__name__.__hash__() + sum(child.__hash__() for child in children)
        

    def __eq__(self, other: 'Rule'):
        return isinstance(other, Rule) and self.__hash__() == other.__hash__()
        

    def __hash__(self):
        return self._hash


    def __repr__(self):
        return self.__name__
            
                
    def __str__(self):
        return self._str
    


class StrictRule(Rule): pass



class State(list):    
    def __init__(self, iterable = None):
        iterable = iterable or []
        super().__init__(iterable)
        self._hash = sum(token.__hash__() for token in iterable)


    def __hash__(self) -> int:
        return self._hash
    


class OrderedSet(dict):
    """Implements an ordered set using a `dict`. 
    `add()` and `remove()` methods provide `append()` and `pop()` functionality."""

    def __init__(self, iterable = None):
        super().__init__(dict.fromkeys(iterable) if iterable else {})


    def add(self, item):
        self.pop(item, None)
        self[item] = None


    def remove(self) -> State:
        return self.popitem()[0]


    def copy(self):
        return OrderedSet(self.keys())


class Parsed:
    def __init__(self, sentence: str, AST: Rule = None, max_states: int = None):
        self.sentence = sentence
        self.AST = AST
        self.max_states = max_states


    def get(self):
        return self.AST


    def __str__(self):
        return self.sentence

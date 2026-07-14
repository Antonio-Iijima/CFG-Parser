import json
import os



class DotDict(dict):
    __getattr__ = dict.__getitem__
    __delattr__ = dict.__delitem__


    def __init__(self, iterable):
        super().__init__(iterable)
        for k, v in self.items():
            if isinstance(v, dict):
                self[k] = DotDict(v)


    def __setattr__(self, key, value):
        return dict.__setitem__(self, key, DotDict(value) if isinstance(value, dict) else value)



class Config(DotDict):
    def __init__(self, filename: str = "config.json", indent: int = 3):        
        root = os.path.dirname(__file__)
        config = os.path.join(root, filename)
        
        with open(config) as file:
            super().__init__(json.load(file))

        self.paths.root = root
        self.paths.config = config
        self.indent = indent


    def save(self):
        self.flags = dict.fromkeys(self.flags.keys(), False)
        with open(self.paths.config, "w") as file:
            json.dump(self, file, indent=self.indent)


    @property
    def isModified(self):
        with open(self.paths.config) as file:
            old = DotDict(json.load(file))
        return any(
            self[category] != old.get(category, KeyError)
            for category in self.keys() if category not in old.ignore.categories
        )



CONFIG = Config()

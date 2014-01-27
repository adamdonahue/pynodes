import importlib

registry = [
        # ('ClassName', 'ModuleName')
        ]

class Types(object):
    def __init__(self):
        self.typeMap = {}
        for c, m in registry:
            if c in self.typeMap:
                raise RuntimeError("Type %s is defined more than once." % c)
            self.typeMap[c] = m

    def __getattr__(self, k):
        return getattr(importlib.import_module(self.typeMap[k]), k)

types = Types()

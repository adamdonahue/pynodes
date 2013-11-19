import imp
import json
import os
import requests
import sys

class AutoImporter(object):

    rev = "master"
    uri = 'http:///{host}/{rev}/{module}'
    modules = [
        ]

    def __init__(self, rev="master"):
        self.rev = rev
        self.requests = requests

    def find_module(self, name, path):
        """Return True only if the path is to a module
        we can load.

        """
        if name in self.modules:
            return self
        if name.split('.', 1)[0] not in self.modules:
            return None
        response = requests.head(self.uri.format(rev=self.rev, module=name))
        if response.status_code != 200:
            return None
        return self

    def load_module(self, name):
        if name in sys.modules:
            return sys.modules[name]
        response = requests.get(self.uri.format(rev=self.rev, module=name))
        if response.status_code != 200:
            raise ImportError(response.content)
        source = json.loads(response.content)
        if source['name'] in sys.modules:
            return sys.modules[source['name']]
        module = imp.new_module(name)
        if source['path']:
            module.__path__ = str(source['path'])
        module.__file__ = str(source['file'])
        module.__loader__ = self
        # TODO: Set module.__package__ appropriately.

        sys.modules[source['name']] = module

        exec(source['source'], module.__dict__)

        return module

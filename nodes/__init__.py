__author__ = "Adam M. Donahue (adam.donahue@gmail.com)"
__copyright__ = "Copyright 2013, Adam M. Donahue"
__version__ = "0.0.1"
__maintainer__ = "Adam Donahue"
__contact__ = "adam.donahue@gmail.com"
__status__ = "Alpha"

import functools
import inspect
import types

from graph import *

ReadOnly     = NodeDescriptor.READONLY
Settable     = NodeDescriptor.SETTABLE
Serializable = NodeDescriptor.SERIALIZABLE
Stored       = NodeDescriptor.STORED

class GraphEnabledType(type):
    def __init__(cls, className, baseClasses, attrs):
        if className != 'GraphEnabled' and '__init__' in attrs:
            raise RuntimeError("Subclasses of GraphEnabledType are not allowed to redefine __init__.")

        for k,v in attrs.iteritems():
            if isinstance(v, GraphMethodDescriptor) and v.name != k:
                v_ = copy.copy(v)
                v_.name = k
                v_.flags = v.flags
                setattr(cls, k, v_)

        type.__init__(cls, className, baseClasses, attrs)

        graphMethodDescriptors = []
        for k in dir(cls):
            v = getattr(cls, k)
            if isinstance(v, GraphMethodDescriptor):
                graphMethodDescriptors.append(v)
            cls._graphMethodDescriptors = graphMethodDescriptors
            cls._storedGraphMethodDescriptors = [v for v in graphMethodDescriptors if v.stored]

# TODO: Not sure inheritance is the right pattern.  Perhaps
#       these next two should be uses relationships.
class GraphMethodDescriptor(NodeDescriptor):

    @property
    def name(self):
        return self.function.__name__

class GraphMethod(NodeDescriptorBound):

    @property
    def name(self):
        return self.function.__name__

class GraphEnabled(object):
    __metaclass__ = GraphEnabledType

    def __init__(self, **kwargs):
        for k in dir(self):
            v = getattr(self, k)
            if isinstance(v, GraphMethodDescriptor):
                super(GraphEnabled, self).__setattr__(k, GraphMethod(self, v))
        for k,v in kwargs.iteritems():
            c = getattr(self, k)
            if not isinstance(c, GraphMethod):
                raise RuntimeError("%s is not a graph-enabled method and cannot be set in __init__.")
            self.__setattr__(c.name, v)

    def __setattr__(self, n, v):
        c = getattr(self, n)
        if isinstance(c, GraphMethod):
            c.setValue(v)
            return
        super(GraphEnabled, self).__setattr__(n, v)

def graphMethod(f=0, flags=ReadOnly, *args, **kwargs):
    """Declares a on-graph method, potentially persisted
    to an underlying datastore.

    """
    if not isinstance(f, types.FunctionType):
        def wrapper(g):
            return graphMethod(g, f, *args, **kwargs)
        return wrapper
    return GraphMethodDescriptor(f, flags=flags)

def scenario(parentScenario=None):
    """Creates a new scenario, collecting values to overlay
    when the scenario is applied.

    """
    raise NotImplementedError("Scenarios are not yet supported.")

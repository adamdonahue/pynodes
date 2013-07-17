import functools
import inspect

class NodeBase(object):
    """All nodes belong to a single graph, and have one or more
    edges to other nodes in the same graph.

    Subclasses can add additional attributes, etc., but
    in general flags should be set to indicate the state
    and/or options set on a node as well.

    Each node must have a key that differentiates it
    from other nodes of the same class.

    It is up to the user to ensure the key is unique
    for every node in the graph.

    """
    DEFAULT = 0x0000
    SETTABLE = 0x0001

    def __init__(self, graph, key, flags=DEFAULT):
        self._graph = graph
        self._key = key
        self._flags = flags
        self._inputNodes = set()
        self._outputNodes = set()

    @property
    def graph(self):
        return self._graph

    @property
    def key(self):
        return self._key

    @property
    def flags(self):
        return self._flags

    @property
    def settable(self):
        return bool(self.flags & self.SETTABLE)

    def value(self):
        raise NotImplementedError()

class Node(NodeBase):
    """All graph nodes are built around the notion of a core
    computation, which can be bypassed by a setting a node
    value specifically (where the node has that option).

    A computation is a Python GraphEnabledFunction or
    GraphEnabledObject along with zero or more arguments.

    """

    def __init__(self, graph, key, graphEnabledFunction=None, args=(), flags=NodeBase.DEFAULT):
        super(Node, self).__init__(graph, key, flags=flags)
        self._graphEnabledFunction = graphEnabledFunction
        self._args = args

    @property
    def graphEnabledFunction(self):
        return self._graphEnabledFunction

    @property
    def function(self):
        return self.graphEnabledFunction.function

    @property
    def args(self):
        return self._args

    def data(self):
        return self.graph.nodeData(self)

    def value(self):
        return self.graph.nodeValue(self)

    def compute(self):
        return self.graphEnabledFunction.function(*self.args)

    def fixed(self):
        return self.data().fixed

    def valid(self):
        return self.data().valid

class NodeDataBase(object):
    INVALID = 0x0000
    VALID = 0x0001
    FIXED = 0x0002

class NodeData(NodeDataBase):
    def __init__(self, node, dataStore):
        self._node = node
        self._dataStore = dataStore
        self._flags = NodeDataBase.INVALID

    @property
    def node(self):
        return self._node

    @property
    def dataStore(self):
        return self._dataStore

    @property
    def value(self):
        if not self.valid:
            raise RuntimeError("The node is invalid and must be recomputed in order to get its value.")
        return self._value

    @property
    def flags(self):
        return self._flags

    @property
    def fixed(self):
        return bool(self.flags & self.FIXED)

    @property
    def valid(self):
        return bool(self.flags & self.VALID)

class GraphState(object):
    """Collects run-time state for a graph.  At the moment
    this means keeping track of which node is being
    computed so that we can built a dynamic dependency
    tree.

    """
    def __init__(self, graph):
        self._graph = graph
        self._activeParentNode = None
        self._activeDataStore = None

class Graph(object):

    def __init__(self, dataStoreClass=None, stateClass=None):
        self._dataStoreClass = dataStoreClass or GraphDataStore
        self._rootDataStore = self._dataStoreClass(self)
        self._stateClass = stateClass or GraphState
        self._state = self._stateClass(self)
        self._state._activeDataStore = self._rootDataStore
        self._nodesByKey = {}

    @property
    def dataStore(self):
        return self._state._activeDataStore

    def nodeKey(self, graphEnabledFunction, args=()):
        """Returns a key for the node given its underlying computation.

        At the moment this computation is what distinctly identifies
        a node in the graph.

        """
        key = (graphEnabledFunction,) + args
        return key

    def nodeResolve(self, graphEnabledFunction, args=(), createIfMissing=True):
        """Given a computation, attempts to find the node in
        the graph.

        If it doesn't exist and addIfMissing is set to True,
        a new node is created and added to the graph.

        """
        key = self.nodeKey(graphEnabledFunction, args=args)
        node = self._nodesByKey.get(key)
        if not node and createIfMissing:
            node = self.nodeCreate(key, graphEnabledFunction=graphEnabledFunction, args=args)
        return node

    def nodeCreate(self, key, graphEnabledFunction=None, args=()):
        """Creates a new node, identified by key, based on the
        specified computation, and adds it to the graph.

        If the node already exists, a RuntimeError is raised.

        Returns the new node.

        """
        if key in self._nodesByKey:
            raise RuntimeError("The node with key %s already exists in this graph.")
        node = self._nodesByKey[key] = Node(self, key, graphEnabledFunction=graphEnabledFunction, args=args)
        return node

    def nodeDelete(self, node):
        """Removes the node from the graph, if it exists
        and if and only if the node has no inputs or outputs.

        """
        raise NotImplementedError("Not yet implemented, nor clear that we should.")

    def nodeCompute(self, node):
        return node.compute()

    def nodeData(self, node, createIfMissing=True):
        """Returns any node data for the object, if it exists.

        If it doesn't exist and createIfMissing is True,
        a new NodeData object for the node is created in the
        data store and then returned.

        """
        return self.dataStore.nodeData(node, createIfMissing=createIfMissing)

    def nodeAddDependency(self, node, dependency):
        """Adds the dependency as an input to the node, and the node
        as an output of the dependency.

        """
        node._inputNodes.add(dependency)
        dependency._outputNodes.add(node)

    def nodeValue(self, node, computeInvalid=True):
        """Returns a value for the given node, recomputing if necessary.

        If the final value returned is not valid, we raise an exception.

        """
        #
        #   Track the dependencies, even if the node data
        #   is valid.  We may have picked up a new output.
        #
        if self._state._activeParentNode:
            self.nodeAddDependency(self._state._activeParentNode, node)

        nodeData = self.nodeData(node)
        if nodeData.valid:
            return nodeData.value
        if not nodeData.valid and not computeInvalid:
            raise RuntimeError("Node is invalid and computeInvalid is False.")
        try:
            savedParentNode = self._state._activeParentNode
            self._state._activeParentNode = node
            nodeData._value = self.nodeCompute(node)
            nodeData._flags |= nodeData.VALID
        finally:
            self._state._activeParentNode = savedParentNode
        return nodeData.value

    def nodeSetValue(self, node, value):
        nodeData = self.nodeData(node)
        if nodeData.fixed and nodeData.value == value:
            return
        nodeData._value = value
        nodeData._flags |= (nodeData.FIXED|nodeData.VALID)
        self.nodeInvalidateOutputs(node)

    def nodeUnsetValue(self, node):
        nodeData = self.nodeData(node)
        if not nodeData.fixed:
            raise RuntimeError("You cannot unset a value that hasn't been set.")
        del nodeData._value
        nodeData._flags &= ~(nodeData.FIXED|nodeData.VALID)
        self.nodeInvalidateOutputs(node)

    def nodeInvalidateOutputs(self, node):
        outputs = list(node._outputNodes)
        while outputs:
            output = outputs.pop()
            outputData = self.nodeData(output)
            if outputData.fixed:
                continue
            outputData._flags &= ~NodeData.VALID
            del outputData._value
            outputs.extend(list(output._outputNodes))
        return

    def nodeCalced(self, node):
        return node.calced()

    def nodeFixed(self, node):
        return node.fixed()

    def nodeValid(self, node):
        return node.valid()

class GraphDataStore(object):
    def __init__(self, graph):
        self._graph = graph
        self._nodeDataByNodeKey = {}

    @property
    def graph(self):
        return self._graph

    def nodeData(self, node, createIfMissing=True):
        """Returns a NodeData object from this data store
        or any of its parents.

        """
        if node.key not in self._nodeDataByNodeKey and createIfMissing:
            self._nodeDataByNodeKey[node.key] = NodeData(node, self)
        return self._nodeDataByNodeKey.get(node.key)

class GraphLayeredDataStore(GraphDataStore):
    """A data store that can exist as part of a tree of
    other data stores.

    """
    def __init__(self, graph, parentDataStore=None):
        super(GraphLayeredDataStore, self).__init__(graph)
        self._parentDataStore = parentDataStore

    @property
    def parentDataStore(self):
        return self._parentDataStore

    def __enter__(self):
        """Activates the data store.

        """
        raise NotImplementedError()


    def __exit__(self, *err):
        """Deactivates the data store.

        """
        raise NotImplementedError()

def dataStore(parentDataStore=None):
    """Creates a new data store and returns it.

    """
    parentDataStore = parentDataStore or _graph.dataStore
    return GraphLayeredDataStore(_graph, parentDataStore)

class GraphEnabledType(type):
    """Used to reserve __init__ on graph objects so that we
    can do additional parsing, set defaults, etc., from a single
    place.

    """
    def __init__(cls, className, baseClasses, attrs):
        if className != 'GraphEnabled' and '__init__' in attrs:
            raise RuntimeError("Subclasses of GraphEnabled are not allowed to redefine __init__.")
        type.__init__(cls, className, baseClasses, attrs)

class GraphEnabled(object):
    """All classes that provide node-enabled methods should
    inherit, directly or indirectly, from this class.  Such
    inheritance may become a requirement in a future version,
    but for now this enables some helpful features such as
    the ability to directly set a node on the object without
    having to call setValue.

    """
    __metaclass__ = GraphEnabledType

    def __init__(self, **kwargs):
        for k in dir(self):
            v = getattr(self, k)
            if isinstance(v, GraphEnabledFunction):
                super(GraphEnabled, self).__setattr__(k, GraphEnabledMethod(v, self))
        for k,v in kwargs.iteritems():
            c = getattr(self, k)
            if not isinstance(c, GraphEnabledMethod):
                raise RuntimeError("%s is not graph-enabled and cannot be set in __init__.")
            self.__setattr__(c.methodName, v)

    def __setattr__(self, n, v):
        c = getattr(self, n)
        if isinstance(c, GraphEnabledMethod):
            c.setValue(v)
            return
        super(GraphEnabled, self).__setattr__(n, v)

class GraphEnabledFunction(object):
    """A function that has been lifted to exist on the graph.

    """
    def __init__(self, function, flags=Node.DEFAULT):
        self.function = function
        self.flags = flags
        self.argspec = inspect.getargspec(function)

    @property
    def name(self):
        return self.function.__name__

    @property
    def settable(self):
        return bool(self.flags & Node.SETTABLE)

    def isConsistent(self, *args):
        if self.argspec.varargs:
            return len(args) >= self.function.func_code.co_argcount
        else:
            return len(args) == self.function.func_code.co_argcount

    def resolve(self, *args):
        return _graph.nodeResolve(self, args=args)

    def setValue(self, value, *args):
        if not self.settable:
            raise RuntimeError("This node cannot be set.")
        node = self.resolve(*args)
        _graph.nodeSetValue(node, value)

    def unsetValue(self, *args):
        if not self.settable:
            raise RuntimeError("This node cannot be unset.")
        node = self.resolve(*args)
        _graph.nodeUnsetValue(node)

    def getValue(self, *args):
        node = self.resolve(*args)
        return _graph.nodeValue(node)

    def __call__(self, *args):
        return self.getValue(*args)

class GraphEnabledMethod(object):

    def __init__(self, graphEnabledFunction, graphEnabledObject):
        self._graphEnabledFunction = graphEnabledFunction
        self._graphEnabledObject = graphEnabledObject

    @property
    def function(self):
        return self.graphEnabledFunction.function

    @property
    def graphEnabledFunction(self):
        return self._graphEnabledFunction

    @property
    def graphEnabledObject(self):
        return self._graphEnabledObject

    @property
    def methodName(self):
        return self._graphEnabledFunction.name

    # Refactor the below, too much duplicated code.
    #
    def args(self, *args):
        return (self._graphEnabledObject,) + args

    def resolve(self, *args):
        return self.graphEnabledFunction.resolve(*self.args(*args))

    def __call__(self, *args):
        return self.getValue(*args)

    def getValue(self, *args):
        return self._graphEnabledFunction(*self.args(*args))

    def setValue(self, value, *args):
        return self._graphEnabledFunction.setValue(value, *self.args(*args))

    def unsetValue(self, *args):
        return self._graphEnabledFunction.unsetValue(*self.args(*args))

DEFAULT = Node.DEFAULT
SETTABLE = Node.SETTABLE

def graphEnabled(f=None, flags=DEFAULT, *args, **kwargs):
    """Places a function on the graph.

    A graph-enabled function is resolved to a node on the
    graph when the computation is called.

    Users can decorate functions in two ways:
        @graphEnabled(*args, **kwargs)      Allowing for decorator options.
        @graphEnabled                       Shortcut for @graphEnabled()

    Any regular function can be enabled.  If a function is
    a member of a class, that class must inherit from the GraphEnabled
    class; when an object of that class is instantiated, the graph-enabled
    function is bound to the object as a graph-enabled method.

    """
    if not callable(f):
        def wrapper(g):
            return graphEnabled(g, f)
        return wrapper
    return GraphEnabledFunction(f, flags=flags)

_graph = Graph()        # We need somewhere to start.

import functools

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
    SETTABLE  = 0x0001

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
        return self.flags & self.SETTABLE

    @property
    def dataStore(self):
        return self.graph.dataStore

    def value(self, dataStore=None):
        raise NotImplementedError()

class Node(NodeBase):
    """All graph nodes are built around the notion of a core
    computation, which can be bypassed by a setting a node
    value specifically (where the node has that option).

    A computation is a Python callable that accepts no
    arguments.  (This doesn't mean you can't compute
    a function with arguments; it just means you need to
    bind the arguments first, using, say, functools.partial,
    before you initialize the node.)

    """

    def __init__(self, graph, key=None, computation=None, flags=NodeBase.DEFAULT):
        super(Node, self).__init__(graph, key, flags=flags)
        self._computation = computation

    @property
    def computation(self):
        return self._computation

    def data(self, dataStore=None):
        return self.graph.nodeData(self, dataStore=dataStore)

    def value(self, dataStore=None):
        return self.graph.nodeValue(self, dataStore=dataStore)

    def compute(self, dataStore=None):
        return self.graph.nodeCompute(self, dataStore=dataStore)

    def calced(self, dataStore=None):
        return self.data(dataStore).calced

    def fixed(self, dataStore=None):
        return self.data(dataStored).fixed

    def valid(self, dataStore=None):
        return self.data(dataStored).valid 

class NodeDataBase(object):
    INVALID = 0x0000
    CALCED  = 0x0001
    FIXED   = 0x0002

class NodeData(NodeDataBase):
    def __init__(self, node, dataStore, value=None, status=NodeDataBase.INVALID):
        self._node = node
        self._dataStore = dataStore
        self._value = value
        self._status = status

    @property
    def node(self):
        return self._node

    @property
    def dataStore(self):
        return self._dataStore

    @property
    def status(self):
        return self._status

    @property
    def calced(self):
        return self.status & self.CALCED

    @property
    def fixed(self):
        return self.status & self.FIXED

    @property
    def valid(self):
        return self.calced | self.fixed

    @property
    def dataStore(self):
        return self._dataStore

class GraphState(object):
    """Collects run-time state for a graph.  At the moment
    this means keeping track of which node is being
    computed so that we can built a dynamic dependency
    tree.

    """
    def __init__(self, graph):
        self._graph = graph
        self._activeNode = None

class Graph(object):

    def __init__(self, dataStoreClass=None, stateClass=None):
        self._dataStoreClass = dataStoreClass or GraphDataStore
        self._dataStore = self._dataStoreClass(self)
        self._stateClass = stateClass or GraphState
        self._state = self._stateClass(self)
        self._nodesByKey = {}

    @property
    def dataStore(self):
        return self._dataStore

    def nodeKey(self, computation):
        """Returns a key for the node given its underlying computation.

        At the moment this computation is what distinctly identifies
        a node in the graph.

        """
        return hash(computation)

    def nodeResolve(self, computation, createIfMissing=False):
        """Given a computation, attempts to find the node in
        the graph.

        If it doesn't exist and addIfMissing is set to True,
        a new node is created and added to the graph.

        """
        key = self.nodeKey(computation)
        node = self._nodesByKey.get(key)
        if not node and createIfMissing:
            node = self.nodeCreate(key, computation)
        return node

    def nodeCreate(self, key, computation):
        """Creates a new node, identified by key, based on the
        specified computation, and adds it to the graph.

        If the node already exists, a RuntimeError is raised.

        Returns the new node.

        """
        if key in self._nodesByKey:
            raise RuntimeError("The node with key %s already exists in this graph.")
        node = self._nodesByKey[key] = Node(self, key, computation)
        return node

    def nodeDelete(self, node):
        """Removes the node from the graph, if it exists
        and if and only if the node has no inputs or outputs.

        """
        raise NotImplementedError("Not yet implemented, nor clear that we should.")

    def nodeData(self, node, createIfMissing=False):
        """Returns any node data for the object, if it exists.

        If it doesn't exist and createIfMissing is a false,
        a new NodeData object is created in the data store
        and then returned.

        """
        return self.dataStore.nodeData(node, createIfMissing=createIfMissing)

    def nodeValue(self, node, computeInvalid=True):
        """Returns a value for the given node, recomputing if necessary.

        If the final value returned is not valid, we raise an exception.

        """
        nodeData = self.dataStore.nodeData(node, createIfMissing=True)
        if nodeData.valid:
            return nodeData.value
        return self.nodeComputeValue(node)
        # TODO: Compute if necessary.
        raise NotImplementedError()

    def nodeComputeValue(self, node, force=False):
        # FIXME: Not working, just testing.
        if self._state._activeNode:
            self._state._activeNode._inputNodes.add(node)
            node._outputNodes.add(self._state._activeNode)
        try:
            self.previousNode = self._state._activeNode
            self._state._activeNode = node
            value = node.computation()
        finally:
            self._state._activeNode = self.previousNode
        return value 

    def nodeSetValue(self, node, value):
        # TODO: Set the node's value, if it's settable.
        #       Any old set values will be overwritten.
        raise NotImplementedError()

    def nodeUnsetValue(self, node):
        # TODO: Unset the node's value if it's set, reverting to the
        #       default computation.  If the value is not set, raises
        #       an error.
        raise NotImplementedError()

    def nodeCalced(self, node):
        return node.calced(self.dataStore)

    def nodeFixed(self, node):
        return node.fixed(self.dataStore)

    def nodeValid(self, node):
        return node.valid(self.dataStore)

class GraphDataStore(object):
    def __init__(self, graph):
        self._graph = graph
        self._nodeDataByNodeKey = {}

    @property
    def graph(self):
        return self._graph

    def nodeData(self, node, createIfMissing=False):
        """Returns a NodeData object from this data store
        or any of its parents.

        """
        nodeData = self._nodeDataByNodeKey.get(node.key)
        if not nodeData and createIfMissing:
            nodeData = self._nodeDataByNodeKey[node.key] = NodeData(node, self)
        return nodeData

    def nodeValue(self, node):
        nodeData = self.nodeData(node)
        if nodeData and nodeData.valid:
            return nodeData.value
        raise Exception("No node data, or node data invalid.")

class DeferredNode(object):
    """A deferred node allows one to wrap callables for later resolution
    to a node when the full details needed for the resolution are not
    available until runtime.

    """
    def __init__(self, method, **kwargs):
        self.method = method
        self.instance = None

    def isBound(self):
        return bool(self.instance)

    def computation(self, *args):
        return functools.partial(self.method, self.instance, *args)

    def resolve(self, createIfMissing=True, *args):
        return _graph.nodeResolve(self.computation(*args), createIfMissing=createIfMissing)

    def __get__(self, instance, *args):
        self.instance = instance
        return self

    def __call__(self, *args):
        if not self.isBound():
            raise RuntimeError("You cannot call an unbound node-enabled method.")
        node = self.resolve(*args)
        return _graph.nodeValue(node)

def deferredNode(f=None, options=None, *args, **kwargs):
    """Marks a function as a (as yet unbound) deferred node for
    the graph.

    A deferred node becomes a real node when the underlying
    computation (the decorated function) is called with a
    particular set of argument values.

    Users can decorate functions in two ways:
        @node(*args, **kwargs)      Allowing for decorator options.
        @node                       Shortcut for @node()

    """
    if not callable(f):
        def wrapper(g):
            return deferredNode(g, f)
        return wrapper
    return DeferredNode(f, options=options)

_graph = Graph()        # We need somewhere to start!

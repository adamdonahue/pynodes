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

    def data(self):
        return self.graph.nodeData(self)

    def value(self):
        return self.graph.nodeValue(self)

    def compute(self):
        return self.graph.nodeCompute(self)

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

    def nodeResolve(self, computation, createIfMissing=True):
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

    def nodeData(self, node, createIfMissing=True):
        """Returns any node data for the object, if it exists.

        If it doesn't exist and createIfMissing is True,
        a new NodeData object for the node is created in the
        data store and then returned.

        """
        return self.dataStore.nodeData(node, createIfMissing=createIfMissing)

    def nodeAddDependency(self, node, dependency):
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
        if not nodeData.valid and not computeInvalid:
            raise RuntimeError("Node is invalid and computeInvalid is False.")
        if nodeData.fixed:
            return nodeData.value
        try:
            savedParentNode = self._state._activeParentNode
            self._state._activeParentNode = node
            nodeData._value = node.computation()
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
            raise RuntimeError("You cannot unset a node that is not set to a value.")
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

# FIXME: We want the key before the computation is created,
#        because the code here means we create a new object every
#        time we get a deferred node's value, even if a node
#        for that computation has already been created.
#
class Computation(functools.partial):
    """Represents a node computation.

    This is essentially a functools.partial with an overriden
    __hash__ function so that a given function and set of
    arguments returns the same hash value.

    """
    def __init__(self, func, *args, **kwargs):
        if kwargs:
            raise RuntimeError("The graph does not yet support keyword arguments.")
        super(Computation, self).__init__(self, *args)

    def __hash__(self):
        return hash((self.func, self.args))

class GraphObject(object):
    """All classes that provide node-enabled methods should
    inherit, directly or indirectly, from this class.  Such
    inheritance may become a requirement in a future version,
    but for now this enables some helpful features such as
    the ability to directly set a node on the object without
    having to call setValue.

    """
    def __setattr__(self, n, v):
        obj = self.__getattribute__(n)
        if isinstance(obj, DeferredNode):
            obj.setValue(v)
            return
        super(GraphEnabled, self).__setattr__(n, v)

class DeferredNode(object):
    """A deferred node allows one to wrap callables for later resolution
    to a node when the full details needed for the resolution are not
    available until runtime.

    """
    def __init__(self, func, flags=Node.DEFAULT):
        self.func = func
        self.argspec = inspect.getargspec(func)
        self.flags = flags
        self.obj = None    # Set if the function is later bound to an object.

    def isBound(self):
        return bool(self.obj)

    def isConsistent(self, *args):
        if self.argspec.varargs:
            return len(args) >= self.func.func_code.co_argcount
        else:
            return len(args) == self.func.func_code.co_argcount

    def computation(self, *args):
        if self.isBound():
            args = (self.obj,) + args
        if not self.isConsistent(*args):
            raise RuntimeError("Missing or too many arguments.")
        return Computation(self.func, *args)

    def resolve(self, *args):
        return _graph.nodeResolve(self.computation(*args))

    @property
    def settable(self):
        return bool(self.flags & Node.SETTABLE)

    def setValue(self, value, *args):
        if not self.settable:
            raise RuntimeError("This node cannot be set.")
        _graph.nodeSetValue(self.resolve(*args), value)

    def unsetValue(self, *args):
        if not self.settable:
            raise RuntimeError("This node cannot be unset.")
        _graph.nodeUnsetValue(self.resolve(*args))

    def __get__(self, obj, *args):
        self.obj = obj
        return self

    def __call__(self, *args):
        return _graph.nodeValue(self.resolve(*args))

DEFAULT = Node.DEFAULT
SETTABLE = Node.SETTABLE

def deferredNode(f=None, flags=DEFAULT, *args, **kwargs):
    """Marks a function as a (as yet unbound) deferred node for
    the graph.

    A deferred node becomes a real node when the underlying
    computation (the decorated function) is called with a
    particular set of argument values.

    Users can decorate functions in two ways:
        @node(*args, **kwargs)      Allowing for decorator options.
        @node                       Shortcut for @node()

    deferredNode can be applied to stand-alone functions or
    those that will be later bound to an instance, and gracefully
    handles both cases.

    """
    if not callable(f):
        def wrapper(g):
            return deferredNode(g, f)
        return wrapper
    return DeferredNode(f, flags=flags)

_graph = Graph()        # We need somewhere to start!

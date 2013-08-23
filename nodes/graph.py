import functools
import inspect

class NodeDescriptor(object):
    # TODO: Get rid of object, do this elsewhere.

    READONLY     = 0x0000
    OVERLAYABLE  = 0x0001
    SETTABLE     = 0x0003
    SERIALIZABLE = 0x0004
    STORED       = SETTABLE|SERIALIZABLE

    def __init__(self, function, flags=READONLY):
        self._function = function
        self._flags = flags

    @property
    def function(self):
        return self._function

    @property
    def name(self):
        return self._name

    @property
    def flags(self):
        return self._flags

    @property
    def overlayable(self):
        return self.flags & self.OVERLAYABLE == self.OVERLAYABLE

    @property
    def settable(self):
        return self.flags & self.SETTABLE == self.SETTABLE

    @property
    def serializable(self):
        return self.flags & self.SERIALIZABLE == self.SERIALIZABLE

    @property
    def stored(self):
        return self.flags & self.STORED == self.STORED

class NodeDescriptorBound(object):

    def __init__(self, obj, descriptor):
        self._obj = obj
        self._descriptor = descriptor

    @property
    def obj(self):
        return self._obj

    @property
    def descriptor(self):
        return self._descriptor

    @property
    def flags(self):
        return self.descriptor.flags

    @property
    def settable(self):
        return self.descriptor.settable

    @property
    def serializable(self):
        return self.descriptor.serializable

    @property
    def stored(self):
        return self.descriptor.stored

    @property
    def function(self):
        return self.descriptor.function

    @property
    def method(self):
        return self.descriptor.function

    def key(self, args=()):
        return (self.obj, self.method) + args

    def node(self, args=()):
        return _graph.nodeResolve(self, args=args)

    def __call__(self, *args):
        return _graph.nodeValue(self.node(args=args))

    def setValue(self, value, *args):
        _graph.nodeSetValue(self.node(args=args), value)

    def clearValue(self, *args):
        _graph.nodeClearValue(self.node(args=args))

    def setWhatIf(self, value, *args):
        _graph.nodeSetWhatIf(self.node(args=args), value)

    def clearWhatIf(self, *args):
        _graph.nodeClearWhatIf(self.node(args=args))

class Node(object):
    NONE  = 0x0000
    VALID = 0x0001
    SET   = 0x0002

    def __init__(self, graph, key, descriptor, args=(), flags=NONE):
        self._graph = graph
        self._key = key
        self._descriptor = descriptor
        self._args = args
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
    def descriptor(self):
        return self._descriptor

    @property
    def obj(self):
        return self.descriptor.obj

    @property
    def method(self):
        return self.descriptor.method

    @property
    def settable(self):
        return self.descriptor.settable

    @property
    def serializable(self):
        return self.descriptor.serializable

    @property
    def stored(self):
        return self.descriptor.stored

    @property
    def args(self):
        return self._args

    @property
    def flags(self):
        return self._flags

    def valid(self, dataStore=None):
        return self._graph.nodeData(self, dataStore=dataStore).valid

    def fixed(self, dataStore=None):
        return self._graph.nodeData(self, dataStore=dataStore).fixed

    def value(self, dataStore=None):
        return self._graph.nodeValue(self, dataStore=dataStore)

class NodeData(object):
    NONE  = 0x0000
    VALID = 0x0001
    FIXED = 0x0002

    def __init__(self, node, dataStore):
        self._node = node
        self._dataStore = dataStore
        self._flags = self.NONE
        self._value = None

    @property
    def node(self):
        return self._node

    @property
    def dataStore(self):
        return self._dataStore

    @property
    def flags(self):
        return self._flags

    @property
    def value(self):
        if not self.valid and not self.fixed:
            raise RuntimeError("This node's value needs to be computed or set.")
        return self._value

    @property
    def valid(self):
        return bool(self.flags & self.VALID)

    @property
    def fixed(self):
        return bool(self.flags & self.FIXED)

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
        self._nodesByKey = {}

        self._stateClass = stateClass or GraphState

        self._state = self._stateClass(self)
        self._state._activeDataStore = self._rootDataStore
        self._state._nodesByKey = {}

    @property
    def activeDataStore(self):
        return self._state._activeDataStore

    def nodeKey(self, descriptor, args=()):
        """Returns a key for the node given computation details.

        At the moment this computation is what distinctly identifies
        a node in the graph.

        """
        return descriptor.key(args=args)

    def nodeResolve(self, descriptor, args=(), createIfMissing=True):
        """Given a computation, attempts to find the node in
        the graph.

        If it doesn't exist and createIfMissing is set to True,
        a new node is created and added to the graph.

        """
        key = self.nodeKey(descriptor, args=args)
        node = self._nodesByKey.get(key)
        if not node and createIfMissing:
            node = self.nodeCreate(key, descriptor, args=args)
        return node

    def nodeCreate(self, key, descriptor, args=()):
        """Creates a new node, identified by key, based on the
        specified computation, and adds it to the graph.

        If the node already exists, a RuntimeError is raised.

        Returns the new node.

        """
        if key in self._nodesByKey:
            raise RuntimeError("A node with that key value already exists in this graph.")
        node = self._nodesByKey[key] = Node(self, key, descriptor, args=args)
        return node

    def nodeDelete(self, node):
        """Removes the node from the graph, if it exists
        and if and only if the node has no inputs or outputs.

        """
        raise NotImplementedError("Not yet implemented, nor clear that we should.")

    def nodeAddDependency(self, node, dependency):
        """Adds the dependency as an input to the node, and the node
        as an output of the dependency.

        """
        node._inputNodes.add(dependency)
        dependency._outputNodes.add(node)

    # 
    # The functions below work on node data.
    #

    def nodeData(self, node, dataStore=None, createIfMissing=True):
        """Returns any node data for the object, if it exists.

        If it doesn't exist and createIfMissing is True,
        a new NodeData object for the node is created in the
        data store and then returned.

        """
        dataStore = dataStore or self.activeDataStore
        return dataStore.nodeData(node, createIfMissing=createIfMissing)

    def nodeValue(self, node, dataStore=None, computeInvalid=True):
        """Returns a value for the given node, recomputing if necessary.

        If the final value returned is not valid, we raise an exception.

        """
        #
        #   Track the dependencies, even if the node data
        #   is valid.  We may have picked up a new output.
        #
        dataStore = dataStore or self.activeDataStore
        if self._state._activeParentNode:
            self.nodeAddDependency(self._state._activeParentNode, node)

        nodeData = self.nodeData(node, dataStore=dataStore)
        if nodeData.valid:
            return nodeData.value
        if not nodeData.valid and not computeInvalid:
            raise RuntimeError("Node is invalid and computeInvalid is False.")
        try:
            savedParentNode = self._state._activeParentNode
            self._state._activeParentNode = node
            nodeData._value = node.method(node.obj, *node.args)
            nodeData._flags |= nodeData.VALID
        finally:
            self._state._activeParentNode = savedParentNode
        return nodeData.value

    def nodeSetValue(self, node, value, dataStore=None):
        if not node.settable:
            raise RuntimeError("This is not a settable node.")
        dataStore = dataStore or self.activeDataStore
        nodeData = self.nodeData(node, dataStore=dataStore)
        if nodeData.fixed and nodeData.value == value:
            return
        nodeData._value = value
        nodeData._flags |= (nodeData.FIXED|nodeData.VALID)
        self.nodeInvalidateOutputs(node, dataStore=dataStore)

    def nodeClearValue(self, node, dataStore=None):
        if not node.settable:
            raise RuntimeError("This is not a settable node.")
        dataStore = dataStore or self.activeDataStore
        nodeData = self.nodeData(node, dataStore=dataStore)
        if not nodeData.fixed:
            raise RuntimeError("You cannot clear a value that hasn't been set.")
        del nodeData._value
        nodeData._flags &= ~(nodeData.FIXED|nodeData.VALID)
        self.nodeInvalidateOutputs(node, dataStore=dataStore)

    def nodeSetWhatIf(self, node, value, dataStore=None):
        if not node.overlayable:
            raise RuntimeError("This is not a what-if enabled node.")
        dataStore = dataStore or self.activeDataStore
        raise NotImplementedError("What-ifs are not yet supported.")

    def nodeClearWhatIf(self, node, dataStore=None):
        if not node.overlayable:
            raise RuntimeError("This is not a what-if enabled node.")
        dataStore = dataStore or self.activeDataStore
        raise NotImplementedError("What-ifs are not yet supported.")

    def nodeInvalidateOutputs(self, node, dataStore=None):
        dataStore = dataStore or self.activeDataStore
        outputs = list(node._outputNodes)
        while outputs:
            output = outputs.pop()
            outputData = self.nodeData(output, dataStore=dataStore, createIfMissing=False)
            if not outputData:
                continue
            if outputData.fixed:
                continue
            outputData._flags &= ~NodeData.VALID
            del outputData._value
            outputs.extend(list(output._outputNodes))
        return

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

_graph = Graph()        # We need somewhere to start.

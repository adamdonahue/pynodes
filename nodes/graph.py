import functools
import inspect

class NodeDescriptor(object):
    # TODO: Get rid of object, do this elsewhere.

    READONLY     = 0x0000                   # 00000000
    OVERLAYABLE  = 0x0001                   # 00000001
    SETTABLE     = 0x0003                   # 00000011          Implies OVERLAYABLE.
    SERIALIZABLE = 0x0004                   # 00000100
    STORED       = SETTABLE|SERIALIZABLE    # 00000111          Implies SETTABLE and SERIALIZABLE.

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
    def typename(self):
        return self.obj.__class__.__name__

    @property
    def name(self):
        return self.descriptor.name

    @property
    def flags(self):
        return self.descriptor.flags

    @property
    def settable(self):
        return self.descriptor.settable

    @property
    def overlayable(self):
        return self.descriptor.overlayable

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

    # TODO:  The difference between sets and whatIfs is, at the
    #        moment, rather artifical.  Sets go to the root
    #        data store; other values go to child data stores.
    def setValue(self, value, *args):
        _graph.nodeSetValue(self.node(args=args), value, dataStore=_graph.rootDataStore)

    def clearValue(self, *args):
        _graph.nodeClearValue(self.node(args=args), dataStore=_graph.rootDataStore)

    def setWhatIf(self, value, *args):
        _graph.nodeSetWhatIf(self.node(args=args), value)

    def clearWhatIf(self, *args):
        _graph.nodeClearWhatIf(self.node(args=args))

class Node(object):

    def __init__(self, graph, key, descriptor, args=(), flags=0):
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
    def name(self):
        return self.descriptor.name

    @property
    def obj(self):
        return self.descriptor.obj

    @property
    def typename(self):
        return self.descriptor.typename

    @property
    def method(self):
        return self.descriptor.method

    @property
    def settable(self):
        return self.descriptor.settable

    @property
    def overlayable(self):
        return self.descriptor.overlayable

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
        nodeData = self._graph.nodeData(self, dataStore=dataStore, createIfMissing=False)
        return nodeData.fixed if nodeData else False

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

    def _prettyFlags(self):
        if self.flags == self.NONE:
            return '(none)'
        if self.fixed:
            return 'FIXED|VALID'
        if self.valid:
            return 'VALID'

class GraphState(object):
    """Collects run-time state for a graph.  At the moment
    this means keeping track of which node is being
    computed so that we can built a dynamic dependency
    tree.

    """
    def __init__(self, graph):
        self._graph = graph
        self._activeParentNode = None
        self._activeDataStoreStack = None

class Graph(object):

    def __init__(self, dataStoreClass=None, stateClass=None):
        self._dataStoreClass = dataStoreClass or GraphDataStore
        self._rootDataStore = self._dataStoreClass(self)
        self._nodesByKey = {}
        self._stateClass = stateClass or GraphState
        self._state = self._stateClass(self)
        self._state._activeDataStoreStack = [self._rootDataStore]
        self._state._nodesByKey = {}

    @property
    def activeDataStore(self):
        return self._state._activeDataStoreStack[-1]

    @property
    def activeDataStores(self):
        return self._state._activeDataStoreStack

    @property
    def rootDataStore(self):
        return self._state._activeDataStoreStack[0]

    def activeDataStorePush(self, dataStore):
        parentDataStore = self.activeDataStore
        self._state._activeDataStoreStack.append(dataStore)
        return parentDataStore

    def activeDataStorePop(self):
        if self.activeDataStore == self.rootDataStore:
            raise RuntimeError("You cannot exit the root data store.")
        return self._state._activeDataStoreStack.pop()

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

    def nodeAddDependency(self, node, dependency):
        """Adds the dependency as an input to the node, and the node
        as an output of the dependency.

        """
        node._inputNodes.add(dependency)
        dependency._outputNodes.add(node)

    # 
    # The functions below work on node data.
    #

    def nodeData(self, node, dataStore=None, createIfMissing=True, searchParent=True):
        """Returns the NodeData object associated with the specified
        data store (or any of its ancestors, if searchParent is True),
        or creates it in the data store if createIfMissing is True.

        """
        dataStore = dataStore or self.activeDataStore
        return dataStore.nodeData(node, createIfMissing=createIfMissing, searchParent=searchParent)

    def nodeValue(self, node, dataStore=None, computeInvalid=True):
        """Returns a value for the given node, recomputing if necessary.

        If the final value returned is not valid, we raise an exception.

        """
        dataStore = dataStore or self.activeDataStore

        if self._state._activeParentNode:
            self.nodeAddDependency(self._state._activeParentNode, node)

        nodeData = self.nodeData(node, dataStore=dataStore, createIfMissing=False)
        if nodeData and nodeData.valid:
            return nodeData.value
        if not computeInvalid:
            raise RuntimeError("Node is invalid and computeInvalid is False.")

        if not nodeData or nodeData.dataStore != dataStore:
            nodeData = self.nodeData(node, dataStore=dataStore, searchParent=False)
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
        nodeData = self.nodeData(node, dataStore=dataStore, searchParent=False)
        if nodeData.fixed and nodeData.value == value:  # No change.
            return
        nodeData._value = value
        nodeData._flags |= (NodeData.FIXED|NodeData.VALID)
        self.nodeInvalidateOutputs(node, dataStore=dataStore)

    def nodeClearValue(self, node, dataStore=None):
        if not node.settable:
            raise RuntimeError("This is not a settable node.")
        dataStore = dataStore or self.activeDataStore
        nodeData = self.nodeData(node, dataStore=dataStore, createIfMissing=False, searchParent=False)
        if not nodeData or not nodeData.fixed:
            raise RuntimeError("You cannot clear a value that hasn't been set.")
        if node.key in dataStore._nodeDataByNodeKey:
            del dataStore._nodeDataByNodeKey[node.key]
        self.nodeInvalidateOutputs(node, dataStore=dataStore)

    def nodeSetWhatIf(self, node, value, dataStore=None):
        if not node.overlayable:
            raise RuntimeError("This is not a what-if enabled node.")
        dataStore = dataStore or self.activeDataStore
        if dataStore == self.rootDataStore:
            raise RuntimeError("You cannot use what-ifs outside of a scenario.")
        self.nodeSetValue(node, value, dataStore=dataStore)

    def nodeClearWhatIf(self, node, dataStore=None):
        if not node.overlayable:
            raise RuntimeError("This is not a what-if enabled node.")
        dataStore = dataStore or self.activeDataStore
        if dataStore == self.rootDataStore:
            raise RuntimeError("You cannot use what-ifs outside of a scenario.")
        self.nodeClearValue(node, dataStore=dataStore)

    def nodeInvalidateOutputs(self, node, dataStore=None):
        dataStore = dataStore or self.activeDataStore
        outputs = list(node._outputNodes)
        while outputs:
            output = outputs.pop()
            outputData = self.nodeData(output, dataStore=dataStore, createIfMissing=False)
            if outputData and outputData.fixed:
                continue
            if outputData.dataStore != dataStore:
                outputData = self.nodeData(output, dataStore=dataStore, searchParent=False)
            outputData._flags &= ~NodeData.VALID
            del outputData._value
            outputs.extend(list(output._outputNodes))
        return

class GraphDataStore(object):

    _nextID = 0

    def __init__(self, graph):
        self._id = GraphDataStore._nextID
        GraphDataStore._nextID += 1
        self._graph = graph
        self._nodeDataByNodeKey = {}
        self._activeParentDataStore = None

    @property
    def graph(self):
        return self._graph

    def nodeData(self, node, createIfMissing=True, searchParent=True):
        """Returns a NodeData object from this data store
        or any of its parents.

        If no data is found, and createIfMissing is True, creates
        a new NodeData object in the this data store.

        """
        nodeData = self._nodeDataByNodeKey.get(node.key)
        if nodeData is None and searchParent:
            dataStore = self._activeParentDataStore
            while dataStore:
                nodeData = dataStore._nodeDataByNodeKey.get(node.key)
                if nodeData:
                    break
                dataStore = dataStore._activeParentDataStore
        if not nodeData and createIfMissing:
            nodeData = self._nodeDataByNodeKey[node.key] = NodeData(node, self)
        return nodeData

class Scenario(GraphDataStore):

    def whatIfs(self):
        return [nodeData for nodeData in self._nodeDataByNodeKey.values() if nodeData.fixed]

    def activeWhatIfs(self):
        whatIfsByNodeKey = {}
        dataStore = self
        while dataStore is not None:
            for whatIf in dataStore.whatIfs():
                if whatIf.nodeKey in whatIfsByNodeKey:
                    continue
                whatIfsByNodeKey[whatIf.nodeKey] = whatIf
            dataStore = dataStore._activeParentDataStore
        return whatIfsByNodeKey.values()

    def cleanup(self):
        for nodeKey, nodeData in self._nodeDataByNodeKey.items():
            if nodeData.fixed:
                continue
            del self._nodeDataByNodeKey[nodeKey]

    def _applyWhatIfs(self):
        for whatIf in self.whatIfs():
            self.graph.nodeInvalidateOutputs(whatIf.node, self)

    def __enter__(self):
        if self in self.graph.activeDataStores:
            raise RuntimeError("You cannot reenter an active data store.")
        self._activeParentDataStore = self.graph.activeDataStorePush(self)
        self._applyWhatIfs()
        return self

    def __exit__(self, *args):
        self.cleanup()
        self.graph.activeDataStorePop()
        self._activeParentDataStore = None


def scenario():
    return Scenario(_graph)

_graph = Graph()        # We need somewhere to start.

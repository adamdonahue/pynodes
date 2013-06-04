class Node(object):
    NODE_DEFAULT = 0x0000
    NODE_FIXABLE = 0x0001
    NODE_DELEGATE_FIXINGS = 0x0002

    def __init__(self, graph, key=None, computation=None, delegate=None):
        self._graph = graph
        self._key = key
        self._computation = computation
        self._delegate = delegate
        self._inputNodes = set()
        self._outputNodes = set()

    @property
    def graph(self):
        return self._graph

    @property
    def computation(self):
        return self._computation

    @property
    def delegate(self):
        return self._delegate

    @property
    def edges(self):
        return self._edges

    @property
    def key(self):
        return self._key or hash(self)

    def value(self, dataStore=None):
        return self.graph.nodeData(self, dataStore=dataStore)

    def compute(self, dataStore=None):
        return self.graph.compute(self, dataStore=dataStore)

    def calced(self, dataStore=None):
        return self.graph.calced(self, dataStore=dataStore)

    def fixed(self, dataStore=None):
        return self.graph.fixed(self, dataStore=dataStore)

    def valid(self, dataStore=None):
        return self.graph.valid(self, dataStore=dataStore)

    def __hash__(self):
       return hash((self.__class__, self.computation, self.delegate))

class NodeData(object):
    INVALID = 0x0000
    CALCED  = 0x0001
    FIXED   = 0x0002

    def __init__(self, node, dataStore, value=None, status=INVALID):
        self._node = node
        self._dataStore = dataStore
        self.value = value
        self.status = status

    @property
    def node(self):
        return self._node

    @property
    def dataStore(self):
        return self._dataStore

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

    def __hash__(self):
        return hash((self.__class__, self.node, self.dataStore))

class GraphStack(list):

    @property
    def top(self):
        return self[-1]

    @property
    def bottom(self):
        return self[0]

    push = list.append

class Graph(object):

    def __init__(self, dataStoreClass=None):
        self._dataStoreClass = dataStoreClass or GraphDataStore
        self._dataStoreStack = GraphStack([self._dataStoreClass(self)])
        self._nodes = {}

    @property
    def activeDataStore(self):
        return self._dataStoreStack.top

    @property
    def baseDataStore(self):
        return self._dataStoreStack.bottom

    def nodeAdd(self, node):
        if node.key in self._nodes:
            raise RuntimeError("The node with key %s already exists in this graph.")
        self._nodes[node.key] = node

    def nodeDelete(self, node):
        pass

    def nodeData(self, node):
        for dataStore in reversed(self._dataStoreStack):
            nodeData = dataStore.nodeData(node)
            if nodeData:
                break
        return nodeData


    def nodeValue(self, node):
        nodeData = self.nodeData(node)
        if not nodeData:
            # No data for this node in any active data stores.
            # Create node in base data store (remember this is the 
            # graph side).
            nodeData = self.baseDataStore.nodeData(node, createIfMissing=True)



    def nodeComputeValue(self, node):
        pass

    def nodeSetValue(self, node, value):
        pass

    def nodeUnsetValue(self, node):
        pass


class GraphDataStore(object):
    def __init__(self, graph, parentDataStore=None):
        self._graph = graph
        self._parentDataStore = parentDataStore
        self._nodeData = {}

    @property
    def graph(self):
        return self._graph

    @property
    def parentDataStore(self):
        return self._parentDataStore

    def nodeData(self, node, createIfMissing=False):
        """Returns a NodeData object from this data store
        or any of its parents.

        """
        searching = self
        while searching:
            nodeData = self._nodeData.get(node.key)
            if nodeData:
                break
            searching = searching.parentDataStore
        if not nodeData and createIfMissing:
            nodeData = self._nodeData[node.key] = NodeData(node, self)
        return nodeData

    def nodeValue(self, node):
        nodeData = self.nodeData(node)
        if nodeData and nodeData.valid:
            nodeData.value
        raise Exception("No node data, or node data invalid.")

    def __enter__(self):
        """Activates this dataStore.  Note that this is subtly
        different from the parent hierarchy.  There is no
        implication that the currently active store (from
        the graph's perspective) is a parent of this store.
        This may be the case, for example, when the store
        is applied following its creation, or is created
        with a specific parent.

        """
        self._graph._dataStoreStack.push(self)

    def __exit__(self, *args):
        self._graph._dataStoreStack.pop()

if __name__ == '__main__':
    graph = Graph()
    node = Node(graph)
    graph.nodeAdd(node)
    print graph
    print graph.nodeData(node)

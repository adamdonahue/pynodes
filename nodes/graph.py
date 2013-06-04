import functools

class Node(object):
    """All graph nodes are built around the notion of a core
    computation, which can be bypassed by a setting a node
    value specifically (where the node has that option).

    """
    DEFAULT   = 0x0000
    SETTABLE  = 0x0001

    def __init__(self, graph, key=None, computation=None, handlers=None):
        self._graph = graph
        self._key = key
        self._computation = computation
        self._handlers = handlers or {}
        self._inputNodes = set()
        self._outputNodes = set()

    @property
    def graph(self):
        return self._graph

    @property
    def computation(self):
        # compute, tracking inputs, and invalidating outputs
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

class ObjectMethodComputation(object):
    def __init__(self, obj, method):
        self.obj = obj
        self.method = method

    def __call__(self, node):
        return self.method(self.obj, *self.args)

class ClassMethodComputation(object):
    def __init__(self, cls):
        self.cls = cls
        self.method = method

class StaticComputation(object):
    def __init__(self, value):
        self.value = value

    def __call__(self):
        return self.value

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

    def nodeResolve(self, computation, args=()):
        # TODO: This somehow needs to resolve to a real node
        pass

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

        There are two options; store the 'active' stack
        in the graph and the 'inactive' stack (parent) here.
        or both here.  we always need the inactive stack
        here because otherwise we can't decouple the store
        for persistence or later loading.

        note that when entering 'active' mode, calced values
        are cached and used where necessary, but when exiting
        all cached values are removed from the data store
        so as to avoid wasting memory.

        any and all fixed values, however, remain active
        in the store from when they are added until they
        are removed.

        the idea is that the data store serves two purposes:
        on the one hand it acts as a pure fixed value store.
        on the other hand, it is also a cache for an active
        graph so it can differentiate node data calculated
        based on set values in this data store from those
        set in the active parent store.

        """
        self._graph._dataStoreStack.push(self)

    def __exit__(self, *args):
        self._graph._dataStoreStack.pop()

# client interface
#
# we need to get from method defined on a class to a NODE 
#    the node reprs a callable AND its arguments
#    two possbilities here:
#        we can create custom argument for this
#        or we can create a partial that has already does this binding
#        
#    in either case, we STILL need to go from a class to a node call
#
#    a class function itself is not enough, we don't know what instance it's at
#    but a user will define code statically, so we know the node framework has
#    to be set up then.  the pythonic way is with a decorator
#
#    we also know that an object + class function is not enough.  we need args.
#
#    So:
#        in code the use can declare which methods are node computations, but
#        the impl can't stop there.
#
#        it needs the object.  so when an object is created do we need to
#        create something else?  
#
#        not sure.  let's assume we have some way of determining which fns
#        are nodes; they aren't really nodes yet but we need to mark them
#        as needing to be lifted to nodes at an appropriate time
#
#        when i first wrote this i though i needed an object-method level
#        handle and an object-method-args handle, but i don't think i need
#        the object method handle. instead i can possibly dynamically
#        check the first arg and if its an instance of ... i forgot, we need
#        some way to mark the class as one supporting these functions,
#        otherwise i can't do this test.  but i think if i bypass the object
#        piece, and so a late binding, i can get rid of the need to 
#        override __init__.  oh... no i can't.  dammit, there is no way around
#        the need for the extra level of indirection.
#
#        we a class to declare a class method as a node computation placeholder
#        we need a decorator that replaces the (class) method call with this object.
#        when i create an instance, i need to now replace the class method-specific
#        object with one that has a handle on the object just created and the
#        original class-level method object
#
#        then when somebody -calls- the method we must finally create the 
#        node computation, as this is the level at which graph decision
#        dependencies should be tracked
#
#        class Sample(GraphObject):
#            def regularMethod(self):
#                ...
#
#            @graphNode
#            def nodeMethod(self):
#                ...
#
#

class DeferredNode(object):
    def __init__(self, method, **kwargs):
        self.method = method
        self.instance = None
        self.computation = None

    def isBound(self):
        return bool(self.instance)

    def computation(self):
        return functools.partial(self.method, self.instance, *args)

    def resolve(self, args=()):
        return _graph.nodeResolve(self.computation(args))

    def __get__(self, instance, class_):
        self.instance = instance
        return self

    def __call__(self, *args):
        if not self.isBound():
            raise RuntimeError("You cannot call an unbound node-enabled method.")
        print self.resolve(args)
        return _graph.nodeValue(self.resolve(args))

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
            return node(g, f)
        return wrapper
    return DeferredNode(f, options=options)

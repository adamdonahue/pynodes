import nodes

class Portfolio(nodes.GraphObject):

    @nodes.graphMethod
    def Name(self):
        return None

    @nodes.graphMethod
    def BookNames(self):
        return []

    @nodes.graphMethod
    def BookObjects(self):
        return []

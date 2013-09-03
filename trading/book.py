import nodes

class Book(nodes.GraphMethod):

    @nodes.graphMethod
    def Name(self):
        return 

    @nodes.graphMethod
    def DealNames(self):
        return []       # state

    @nodes.graphMethod
    def DealObjects(self):
        return []

    @nodes.graphMethod
    def Positions(self):
        return 

    @nodes.graphMethod
    def AllPositions(self):
        # even zero quantity positions when netted across deals.
        return 



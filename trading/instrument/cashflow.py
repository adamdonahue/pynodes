import nodes

# inherit from instrument

class ForwardCashFlow(nodes.GraphObject):

    @nodes.graphMethod(nodes.Stored)
    def SettlementDate(self):
        return

    @nodes.graphMethod(nodes.Stored)
    def Currency(self):
        return




import nodes

class MarketEnv(nodes.GraphObject):

    @nodes.graphMethod(nodes.Settable)
    def BusinessDate(self):
        return

    @nodes.graphMethod(nodes.Settable)
    def MarketDataDate(self):
        return

    @nodes.graphMethod(nodes.Settable)
    def MarketDate(self):
        return

    @nodes.graphMethod(nodes.Settable)
    def CalculationDate(self):
        return

    # ...

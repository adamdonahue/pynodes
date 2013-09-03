import nodes
import rewind.event

class PortfolioEventBase(rewind.event.RewindEventBase):
    pass

class PortfolioEventUpdateBooks(PortfolioEventBase):

    @nodes.graphMethod(nodes.Stored)
    def BookNamesAdded(self):
        return []

    @nodes.graphMethod(nodes.Stored)
    def BookNamesRemoved(self):
        return []



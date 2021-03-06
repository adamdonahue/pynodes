import nodes

from .positional import EventDealPositional

class EventDealOpen(EventDealPositional)

    @nodes.graphMethod(nodes.Stored)
    def Book1Name(self):
        return None

    @nodes.graphMethod(nodes.Stored)
    def Book2Name(self):
        return None

    @nodes.graphMethod(nodes.Stored)
    def Instrument(self):
        # name, path, identity
        return None

    @nodes.graphMethod(nodes.Stored)
    def Quantity(self):
        # Decimal quantity, relative to book1.
        return None

    # ...

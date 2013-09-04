import nodes

from .positional import EventDealPositional

# Will probably join this with EventDealOpen, or
# make it just a general positional change, with a
# name

class EventDealOpenComplex(EventDealPositional)

    @nodes.graphMethod(nodes.Stored)
    def Book1Name(self):
        return None

    @nodes.graphMethod(nodes.Stored)
    def Book2Name(self):
        return None

    @nodes.graphMethod(nodes.Stored)
    def Positions(self):
        return []


import nodes

from .instrument import Instrument

class ForwardCashFlow(Instrument):

    @nodes.graphMethod(nodes.Stored)
    def SettlementDate(self):
        return

    @nodes.graphMethod(nodes.Stored)
    def Currency(self):
        return




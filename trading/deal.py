import nodes

class Deal(nodes.GraphObject):

    @nodes.graphMethod
    def Name(self):
        return

    @nodes.graphMethod
    def Positions(self):
        return []

    @nodes.graphMethod
    def BookNames(self):
        return []

    @nodes.graphMethod
    def Book1Name(self):
        return

    @nodes.graphMethod
    def Book2Name(self):
        return

    @nodes.graphMethod
    def Book2Names(self):
        return

    # positions are:
    #   (book, tag, inst, qty)
    #
    # tag used to label cash flows, etc.

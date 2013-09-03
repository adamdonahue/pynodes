import nodes

class Deal(nodes.GraphObject):

    @nodes.graphMethod
    def Name(self):
        return

    @nodes.graphMethod
    def Positions(self):
        return

    # positions are:
    #   ('tag', inst, qty)
    #
    # tag used to label cash flows, etc.

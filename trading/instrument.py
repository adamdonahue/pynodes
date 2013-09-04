import nodes

class Instrument(nodes.GraphObject):

    @nodes.graphMethod
    def NextLifeCycleDate(self):
        return

    @nodes.graphMethod
    def NextLifeCycleEvent(self):
        return

    @nodes.graphMethod
    def EventPositions(self, event):
        return

    @nodes.graphMethod
    def Barriers(self):
        return []

    @nodes.graphMethod
    def UnscheduledEvent(self):
        return


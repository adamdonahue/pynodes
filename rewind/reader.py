import nodes

class RewindableEventReader(nodes.GraphObject):

    def readEventDetails(self, asOfTime, physicalCutoffTime=None):
        raise NotImplementedError()




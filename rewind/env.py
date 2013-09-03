import nodes

class RewindEnv(nodes.GraphObject):
    """Environment through which users can set cutoffs
    and other variables that affect all Rewind-related
    operations in a session.

    """
    @nodes.graphMethod(nodes.Settable)
    def AsOfTimeCutoff(self):
        return              # TODO: Now.

    @nodes.graphMethod(nodes.Settable)
    def _PhysicalTimeCutoff(self):
        return              # TODO: Now.

    def setAsOfDateCutoff(self, asOfDate):
        # TODO: Make a datetime object of
        #           asOfDate-23:59:59
        #       or more granular.
        asOfTime = None
        return [nodes.NodeChange(self.AsOfTimeCutoff, asOfTime)]

    @nodes.graphMethod(delegate=setAsOfDateCutoff)
    def AsOfDateCutoff(self):
        # We just truncate to the last second/ms/ns of
        # the selected AsOfDate.
        return self.AsOfTimeCutoff().date()

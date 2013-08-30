import nodes

class RewindEventBase(nodes.GraphObject):

    @nodes.graphMethod(nodes.Stored)
    def _ContainerNames(self):
        """The names of the objects affected by this event.

        """
        return [c.Name() for c in self._ContainerObjects()]

    @nodes.graphMethod
    def _ContainerPaths(self):
        raise NotImplementedError()

    @nodes.graphMethod(nodes.Settable)
    def _ContainerObjects(self):
        raise NotImplementedError()

    @nodes.graphMethod(nodes.Settable)
    def AsOfDate(self):
        return self.AsOfDateTime().date()

    @nodes.graphMethod(nodes.Stored)
    def AsOfDateTime(self):
        return datetime.datetime.utcnow()

    @nodes.graphMethod
    def _PhysicalDateTime(self):
        raise NotImplementedError()

    @nodes.graphMethod(nodes.Stored)
    def EventNamesAmended(self):
        return []

    @nodes.graphMethod(nodes.Settable)
    def EventObjectsAmended(self):
        raise NotImplementedError()

class RewindEventCancel(RewindEventBase):
    """Cancels an existing event."""


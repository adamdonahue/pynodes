import nodes

class RewindEventBase(nodes.GraphObject):

    @nodes.graphMethod(nodes.Stored)
    def _ContainerNames(self):
        """The names of the container affected by this event.

        A container is just a class that uses the state
        objects that will be updated via this event.

        """
        return [c.Name() for c in self._ContainerObjects()]

    @nodes.graphMethod(nodes.Settable)
    def _ContainerObjects(self):
        raise NotImplementedError()

    @nodes.graphMethod(nodes.Stored)
    def AsOfTime(self):
        # The time during which the event happened.
        return datetime.datetime.utcnow()

    @nodes.graphMethod
    def _PhysicalTime(self):
        # The time at which the event was recorded.
        raise NotImplementedError()

    @nodes.graphMethod(nodes.Stored)
    def EventNamesAmended(self):
        # The names of any events this event amends.
        return []

    @nodes.graphMethod(nodes.Settable)
    def EventObjectsAmended(self):
        raise NotImplementedError()

class RewindEventCancel(RewindEventBase):
    """Cancels an existing event.

    A cancelation logically cancels an event.  If that
    event amended others, then those amended events are
    still 'canceled' via the fact the event that
    amended them was canceled.

    """

class RewindEventDelete(RewindEventBase):
    """Deletes an existing event.

    A delete is logically equivalent to having 'removed'
    a single event object as if that event were never
    written out to begin with.

    """
    



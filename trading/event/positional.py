import nodes
import rewind

class EventDealPositional(rewind.RewindEventBase):
    """Events that affect positions on a deal."""

    @nodes.graphMethod(nodes.Stored)
    def PositionEffects(self):
        """Changes to the positions of a deal effected
        by this event.

        """
        # {'book': {'instrument': 'delta'}, ...} ?




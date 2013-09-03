import nodes
import rewind

# The rewind model has the following fundamental design:
#
#   * A container is a graph or other object that leverages
#     stateful data.  It exposes state via its own
#     methods, but these methods actually retrieve their
#     values via state objects.
#
#   * A state object is an in-memory representation of
#     a stateful variable.
#       - A state object always has an initial state.
#       - This state transitions to another states based on
#         the application of events.
#
#   * An event is a persist representation of whatever
#     data a state object to perform a transition when
#     that event is applied.
#       - An event is an immutable object; once written, it
#         cannot be changed.
#       - An event has two times associated with it:
#           - An asOfTime, which indicates when the event really
#             or contractually should have happened.
#           - A physicalTime, which indicates when the event
#             was written out to disk.
#       - Even though an event itself is immutable, it is
#         possible to amend, cancel, or delete the event.
#         We don't remove the amended/canceled/deleted event
#         from disk; instead we write out a new event that
#         refers to the old one, so we always have a record
#         of the amended/canceled/deleted event as well as
#         time that event happened.  
#
#   * An event reader is responsible for reading in the
#     events needed to modify a particular state object.
#       - For example, if we are calculating state for
#         today, we probably don't care about canceled events.
#         We just want to know the ones that are active today.
#       - Another example is that different event types 
#         might apply to different states; an event that records
#         changes to the books in portfolio would not be of 
#         interest to an event that captures position changes
#         on a deal.  The reader would be responsible for
#         performing this filtering.
#      - We also may want to filter events based on when the
#        event happened.  If I want to calculate what I had
#        in my books last month, contractually, I can ask
#        that the event reader ignore any events having an
#        asOfTime after last month's last calendar date.
#        But note here I would not want to ignore physical
#        times after that date, because I may have amended
#        the a trade from last month this month.  On the
#        other hand, a regulator might wish to know why I 
#        reported a given number last month.  In this case
#        I would want to ignore events that were recorded
#        after last month, even if they affected last month's
#        contractual events, because when I sent my report
#        to the regulator at that time I obviously hadn't
#        yet recorded those amendments.
#           

class RewindableStateBase(object):

    eventReaderClass = None

    def setInitialState(self):
        raise NotImplementedError()

    def transition(event):
        """Applies the event to the current state to move it to
        the next state.

        """

    # Functions to read state.



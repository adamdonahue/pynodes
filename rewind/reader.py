# Job of an event reader is to identify some subset of events
# relevant to a given state object for a particular container
# or set of containers.
#

# Not sure we need this on the graph just yet.
#
class RewindableEventReader(object):

    # What do we need here?
    #
    # First, a reader is called by or in the context of
    # a state object in order to find the events it 
    # needs to bring its state current, based on user
    # inputs.
    #
    # Well, the inputs used to determine the events we want
    # to look at will include the following.
    #
    #    * The asOfTime cutoff.
    #    * The physicalTime cutoff.
    #    * The type(s) of event we are interested in.
    #    * The objects whose state we are interested
    #      in calculating.
    #    * Whether we want to include amended, canceled
    #      or otherwise inactive events.
    #     
    # among other things I suspect.
    #

    # First cut at a dummy object that just accepts the inputs 
    # enumerated above as arguments.
    #

    def __init__(self,
                 eventTypes = [],
                 names = [],
                 ):
        self.eventTypes = eventTypes
        self.names = names

    def eventNames(self, asOfTimeCutoff=None, physicalTimeCutoff=None):
        # Find all events of type in eventTypes, affecting name
        # in names, and having an asOfTime and physicalTime <=
        # the cutoffs.
        #
        # Return events in order in which they should be applied.
        #
        raise NotImplementedError()

    def eventObjects(self):
        raise NotImplementedError()

class RewindableActiveEventsReader(RewindableEventReader):
    """Responsible for reading only unamended or otherwise
    still active events.

    """

class RewindableAllEventsReader(RewindableEventReader):
    """Reads all events of interest, regardless of
    whether they have been canceled, amended, or otherwise.

    """

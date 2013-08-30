import collections

def eventInfos(eventType, asOfDateTime, physicalDateTime):
    raise NotImplementedError()

eventInfo = collections.namedtuple('eventInfo', ['eventType', 'asOfDateTime', 'physicalDateTime'])

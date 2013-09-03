import rewind

class PortfolioEventReader(rewind.RewindableEventReader):
    pass

class PortfolioState(rewind.RewindableStateBase):

    eventReaderClass = PortfolioEventReader

    def setInitialState(self):
        self._bookNames = set()

    def transition(self, event):
        self._bookNames.add(event.BookNamesAdded())
        self._bookNames.discard(event.BookNamesRemoved())

    def bookNames(self):
        return self._bookNames






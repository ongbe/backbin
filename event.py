class Event(object):
    """
    Event is base class providing an interface for all subsequent
    (inherited) events, that will trigger further events in the
    trading infrastructure.
    """
    pass


class MarketEvent(Event):
    """
    Handles the event of receiving a new market update with
    corresponding bars.
    """
    def __init__(self):
        """
        Initialises the MarketEvent.
        """
        self.type = 'MARKET'
        self.engines = []

    def connect(self, handler):
        self.engines.append(handler)

    def fire(self):
        for handler in self.engines:
            handler.receive(self)
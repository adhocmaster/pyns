from event.OnceEvent import OnceEvent
from event.EventTypes import EventTypes

class PacketEvent(OnceEvent):
    """OnceOnlyEvent extends GenericEvent, and so it inherits all of its
    methods, including __repr__, __comp__, _effect."""

    def __init__(self, name: EventTypes, time, packet):
        # We simply define an element of the superclass.
        # Here, super(OnceEvent, self) is the Python way for getting
        # access to the superclass methods from a subclass.
        super().__init__(name, time)
        self.packet = packet

    def do(self, eventManager):
        
        raise NotImplementedError()

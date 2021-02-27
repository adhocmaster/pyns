from event.GenericEvent import GenericEvent

class OnceEvent(GenericEvent):
    """OnceEvent extends GenericEvent, and so it inherits all of its
    methods, including __repr__, __comp__, _effect."""

    def __init__(self, name, time):
        # We simply define an element of the superclass.
        # Here, super(OnceEvent, self) is the Python way for getting
        # access to the superclass methods from a subclass.
        super().__init__(name, time)

    def do(self):
        self._effect()
        # No other events are generated.
        return []

from event.GenericEvent import GenericEvent


class PeriodicEvent(GenericEvent):
    """This is a periodic event like above, except that it has
    an optional maximum number of occurrences."""

    def __init__(self, name, time, periodicity, num_occurrences=None):
        """
        Let's document this constructor a bit better.
        @param name: name of the event.
        @param time: time of first occurrence of the event (datetime object).
        @param periodicity: periodicity of the event (timedelta object).
        @param num_occurrences: number of future occurrences of the event.
            If None, then infinite future occurrences can happen.

        """
        assert num_occurrences is None or num_occurrences > 0
        # We don't want to go back in time!
        assert periodicity.total_seconds() > 0.

        super().__init__(name, time)
        self.periodicity = periodicity
        self.num_occurrences = num_occurrences

    def do(self):
        self._effect()
        # Generates and returns the next occurrence of the event.
        if self.num_occurrences is None or self.num_occurrences > 1:
            return [PeriodicEvent(
                self.name,
                self.time + self.periodicity,
                self.periodicity,
                num_occurrences = None if self.num_occurrences is None
                                  else self.num_occurrences - 1
            )]
        else:
            return []
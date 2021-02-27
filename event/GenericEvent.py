from library.TimeUtils import TimeUtils

class GenericEvent(object):

    def __init__(self, name, time):
        self.name = name
        self.time = time

    def __repr__(self):
        return "Event {} of type {} will occurr at {}".format(
            self.name,
            type(self),
            self.time
        )

    def __lt__(self, other):
        """To sort events according to their time, we need to
        implement the __lt__ operator.  This will be used by heapq later."""
        return self.time < other.time

    def _effect(self):
        """In Python, methods that are supposed to be accessed only within
        the class are prepended with _.  Note that this is just a convention;
        nothing prevents you from calling these methods from outside the class.
        """
        # print("At {}ms ({}): {}".format(TimeUtils.getMS(), self.time, self.name))
        pass

    def do(self):
        """You are supposed to define what happens in each subclass."""
        raise NotImplementedError
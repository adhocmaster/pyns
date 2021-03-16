import queue

class Window(queue.Queue):

    def __init__(self, maxsize):
        super().__init__(maxsize=maxsize)
        self.maxSize=maxsize

    def put(self, item):
        if super().qsize() == self.maxSize:
            self.get()
        super().put(item)
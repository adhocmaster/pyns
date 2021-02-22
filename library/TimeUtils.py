import time
class TimeUtils:

    @staticmethod
    def getMS():
        return time.time_ns() // 1_000_000 
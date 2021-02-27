import time
class TimeUtils:

    @staticmethod
    def getMS():
        return time.time_ns() // 1_000_000 
        
    @staticmethod
    def getMicroS():
        return time.time_ns() // 1_000 
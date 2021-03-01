import time
class TimeUtils:

    @staticmethod
    def getMS():
        return time.time_ns() // 1_000_000 
        
    @staticmethod
    def getMicroS():
        return time.time_ns() // 1_000 

    @staticmethod
    def convertToMS(amount, timeResolutionUnit):
        
        if timeResolutionUnit == 'ms':
            return amount
        if timeResolutionUnit == 'mcs':
            return amount // 1_000
        if timeResolutionUnit == 'ns':
            return amount //  1_000_000

    @staticmethod
    def convertToMCS(amount, timeResolutionUnit):
        
        if timeResolutionUnit == 'ms':
            raise Exception("Cannot convert miliseconds to microseconds due to precision loss.")
        if timeResolutionUnit == 'mcs':
            return amount
        if timeResolutionUnit == 'ns':
            return amount //  1_000
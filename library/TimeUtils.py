import time
class TimeUtils:

    @staticmethod
    def getMS():
        return time.time_ns() // 1_000_000 
        
    @staticmethod
    def getMicroS():
        return time.time_ns() // 1_000 

    @staticmethod
    def convertToMS(amount, originalUnit, round=True):
        
        if originalUnit == 's':
            return amount * 1000

        if originalUnit == 'ms':
            return amount

        if round:
            if originalUnit == 'mcs':
                return amount // 1_000
            if originalUnit == 'ns':
                return amount //  1_000_000
        else:
            if originalUnit == 'mcs':
                return amount / 1_000
            if originalUnit == 'ns':
                return amount /  1_000_000
                
        raise NotImplementedError()

    @staticmethod
    def convertToMCS(amount, originalUnit, round=True):
        
        if originalUnit == 's':
            return amount * 1000_000
        if originalUnit == 'ms':
            return amount * 1000
        if originalUnit == 'mcs':
            return amount
        
        if round:
            if originalUnit == 'ns':
                return amount //  1_000
        else:
            if originalUnit == 'mcs':
                return amount
            if originalUnit == 'ns':
                return amount /  1_000

        raise NotImplementedError()


    @staticmethod 
    def convertTime(amount, originalUnit, toUnit, round=False):
    
        if toUnit == 'ms':
            return TimeUtils.convertToMS(amount, originalUnit, round=round)
        if toUnit == 'mcs':
            return TimeUtils.convertToMCS(amount, originalUnit, round=round)
        
        raise NotImplementedError()
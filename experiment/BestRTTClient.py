from experiment.TimeWindowClient import TimeWindowClient
import logging, math
import numpy as np

class BestRTTClient(TimeWindowClient):

    def __init__(self, 
                id, 
                pollCycle, 
                rttWindowSize, 
                bandWidthWindowSize, 
                delay_between_packets, 
                max_outstanding_packets, 
                timeResolutionUnit, 
                startAt=0,
                debug=True
                ):

        super().__init__(id,
                            pollCycle=pollCycle,
                            rttWindowSize=rttWindowSize,
                            bandWidthWindowSize=bandWidthWindowSize,
                            delay_between_packets=delay_between_packets,
                            max_outstanding_packets=max_outstanding_packets,
                            timeResolutionUnit=timeResolutionUnit,
                            startAt=startAt,
                            debug=debug)

        self.name = f"BestRTTClient {self.id}"
        self.previousPower = 0
        self.explorationProb = 0.2
        self.bestRTT = 9999999999
        self.bestRTTCycle = 10 # we only update best RTT every bestRTT cycle
        self.bestRTTInCurrentCycle = self.bestRTT
        self.bestRTTCounter = 0 # bestRTT count tracker. we only update best RTT every bestRTT cycle

    
    def getPowerTrend(self):
        currentPower = self.getPower()
        trend = currentPower - self.previousPower

        if self.debug:
            logging.debug(f"{self.name}: previousPower = {self.previousPower}, currentPower = {currentPower}")

        self.previousPower = currentPower
        return trend

    
    def shouldExplore(self):
        return np.random.choice([True, False], p=[self.explorationProb, 1 - self.explorationProb])

    def updatePolicy(self):

        if self.bestRTTInCurrentCycle > self._currentRTT:
            self.bestRTTInCurrentCycle = self._currentRTT

        self.bestRTTCounter += self.pollCycle

        if self.bestRTTCounter >= self.bestRTTCycle:
            self.bestRTT = self.bestRTTInCurrentCycle 
            self.bestRTTCounter = 0
            self.bestRTTInCurrentCycle = 999999999


        trend = self.bestRTT -  self._currentRTT

        if self.debug:
            logging.debug(f"{self.name}: power trend = {trend}")

        if trend >= 0: # increasing power
            # power is increasing, should we explore or exploit?
            if self.shouldExplore() == False:

                if self.debug:
                    logging.debug(f"{self.name} increasing max_outstanding_packets")

                # increase by 10%
                increment = max(1, math.ceil(self.max_outstanding_packets * 0.2))
                self.max_outstanding_packets += increment
                return
            
        # trend is negative or we are exploring for better rtt (more power)
        if self.max_outstanding_packets == 1:
            if self.debug:
                logging.debug(f"{self.name} cannot decrease max_outstanding_packets beyond 1. adding 1")
            self.max_outstanding_packets += 1
            return
        if self.debug:
            logging.debug(f"{self.name} decreasing max_outstanding_packets")

        decrement = max(1, math.ceil(self.max_outstanding_packets * 0.2))
        self.max_outstanding_packets -= decrement

        return
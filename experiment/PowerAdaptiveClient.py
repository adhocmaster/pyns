from experiment.AdaptiveClient import AdaptiveClient
import logging

class PowerAdaptiveClient(AdaptiveClient):

    def __init__(self, id, rttWindowSize, bandWidthWindowSize, delay_between_packets, max_outstanding_packets, timeResolutionUnit, debug=True):
        super().__init__(id,
                            rttWindowSize=rttWindowSize,
                            bandWidthWindowSize=bandWidthWindowSize,
                            delay_between_packets=delay_between_packets,
                            max_outstanding_packets=max_outstanding_packets,
                            timeResolutionUnit=timeResolutionUnit,
                            debug=debug)

        self.name = f"PowerAdaptiveClient {self.id}"
        self.previousPower = 0

    
    def getPowerTrend(self):
        currentPower = self.getPower()
        trend = currentPower - self.previousPower
        self.previousPower = currentPower
        return trend

    def updatePolicy(self):

        trend = self.getPowerTrend()

        if trend > 0: # increasing
            #increase delay?
            # if self.debug:
            #     logging.debug(f"{self.name} increasing delay_between_packets")
            # self.delay_between_packets *= 1.1
            if self.debug:
                logging.debug(f"{self.name} increasing max_outstanding_packets")
            self.max_outstanding_packets += 1
        else:
            # if self.debug:
            #     logging.debug(f"{self.name} decreasing delay_between_packets")
            # self.delay_between_packets *= 0.9
            if self.max_outstanding_packets == 1:
                if self.debug:
                    logging.debug(f"{self.name} cannot decrease max_outstanding_packets beyond 1")
                return
            if self.debug:
                logging.debug(f"{self.name} decreasing max_outstanding_packets")
            self.max_outstanding_packets -= 1

        return
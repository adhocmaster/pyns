from experiment.AdaptiveClient import AdaptiveClient
import logging

class RTTAdaptiveClient(AdaptiveClient):

    def __init__(self, id, rttWindowSize, bandWidthWindowSize, delay_between_packets, max_outstanding_packets, timeResolutionUnit, debug=True):
        super().__init__(id,
                            rttWindowSize=rttWindowSize,
                            bandWidthWindowSize=bandWidthWindowSize,
                            delay_between_packets=delay_between_packets,
                            max_outstanding_packets=max_outstanding_packets,
                            timeResolutionUnit=timeResolutionUnit,
                            debug=debug)

        self.name = f"RTTAdaptiveClient {self.id}"

    def updatePolicy(self):

        if self.lastAckedPacket is None:
            return
        
        rttTrend = self.getRTTTrend()

        if rttTrend > 0: # increasing
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
            if self.debug:
                logging.debug(f"{self.name} decreasing max_outstanding_packets")
            self.max_outstanding_packets -= 1

        return
from core.TCPClient import TCPClient
from experiment.RTTAdaptiveClient import RTTAdaptiveClient
from experiment.PowerAdaptiveClient import PowerAdaptiveClient
from experiment.PowerTWClient import PowerTWClient
from experiment.PowerChangeTWClient import PowerChangeTWClient
from experiment.BestRTTClient import BestRTTClient
from library.Configuration import Configuration
import logging
from library.TimeUtils import TimeUtils


class ClientManager:

    def __init__(self, timeResolutionUnit, debug=False):
        self.clients = {}
        self.nextClientId = 1
        self.timeResolutionUnit = timeResolutionUnit
        self.config = Configuration()
        self.name = "ClientManager"
        self.debug = debug
        pass


    def getDelayBetweenPacketsFromDeliveryRatePerS(self, deliveryRatePerS):

        # delay_between_packets is in timeResolutionUnit
        resolutionAmountPerSec = TimeUtils.convertTime(1, 's', self.timeResolutionUnit)
        delay = resolutionAmountPerSec // deliveryRatePerS

        if delay == 0:
            raise Exception(f"deliveryRatePerS is so high that delay in {self.timeResolutionUnit} becomes 0")

        return delay

    
    
    def createRTTAdaptiveClient(self, rttWindowSize, bandWidthWindowSize, deliveryRatePerS, max_outstanding_packets):

        delay_between_packets = self.getDelayBetweenPacketsFromDeliveryRatePerS(deliveryRatePerS)
        client = RTTAdaptiveClient(
                            self.nextClientId, 
                            rttWindowSize=rttWindowSize,
                            bandWidthWindowSize=bandWidthWindowSize,
                            delay_between_packets=delay_between_packets, 
                            max_outstanding_packets=max_outstanding_packets, 
                            timeResolutionUnit=self.timeResolutionUnit,
                            debug=self.debug
                            ) 
        self.clients[self.nextClientId] = client
        self.nextClientId += 1

        if self.debug:
            logging.info(f"{self.name}: created node {client}")

        return client

    
    def createPowerAdaptiveClient(self, rttWindowSize, bandWidthWindowSize, deliveryRatePerS, max_outstanding_packets):

        delay_between_packets = self.getDelayBetweenPacketsFromDeliveryRatePerS(deliveryRatePerS)
        client = PowerAdaptiveClient(
                            self.nextClientId, 
                            rttWindowSize=rttWindowSize,
                            bandWidthWindowSize=bandWidthWindowSize,
                            delay_between_packets=delay_between_packets, 
                            max_outstanding_packets=max_outstanding_packets, 
                            timeResolutionUnit=self.timeResolutionUnit,
                            debug=self.debug
                            ) 
        self.clients[self.nextClientId] = client
        self.nextClientId += 1

        if self.debug:
            logging.info(f"{self.name}: created node {client}")

        return client

    
    def createPowerTWClient(self, pollCycle, rttWindowSize, bandWidthWindowSize, deliveryRatePerS, max_outstanding_packets, startAt=0):

        delay_between_packets = self.getDelayBetweenPacketsFromDeliveryRatePerS(deliveryRatePerS)
        client = PowerTWClient(
                            self.nextClientId, 
                            pollCycle = pollCycle,
                            rttWindowSize=rttWindowSize,
                            bandWidthWindowSize=bandWidthWindowSize,
                            delay_between_packets=delay_between_packets, 
                            max_outstanding_packets=max_outstanding_packets, 
                            timeResolutionUnit=self.timeResolutionUnit,
                            startAt=startAt,
                            debug=self.debug
                            ) 
        self.clients[self.nextClientId] = client
        self.nextClientId += 1

        if self.debug:
            logging.info(f"{self.name}: created node {client}")

        return client


    
    def createPowerChangeTWClient(self, pollCycle, rttWindowSize, bandWidthWindowSize, deliveryRatePerS, max_outstanding_packets, startAt=0):

        delay_between_packets = self.getDelayBetweenPacketsFromDeliveryRatePerS(deliveryRatePerS)
        client = PowerChangeTWClient(
                            self.nextClientId, 
                            pollCycle = pollCycle,
                            rttWindowSize=rttWindowSize,
                            bandWidthWindowSize=bandWidthWindowSize,
                            delay_between_packets=delay_between_packets, 
                            max_outstanding_packets=max_outstanding_packets, 
                            timeResolutionUnit=self.timeResolutionUnit,
                            startAt=startAt,
                            debug=self.debug
                            ) 
        self.clients[self.nextClientId] = client
        self.nextClientId += 1

        if self.debug:
            logging.info(f"{self.name}: created node {client}")

        return client


    
    def createBestRTTClient(self, pollCycle, rttWindowSize, bandWidthWindowSize, deliveryRatePerS, max_outstanding_packets, startAt=0):

        delay_between_packets = self.getDelayBetweenPacketsFromDeliveryRatePerS(deliveryRatePerS)
        client = BestRTTClient(
                            self.nextClientId, 
                            pollCycle = pollCycle,
                            rttWindowSize=rttWindowSize,
                            bandWidthWindowSize=bandWidthWindowSize,
                            delay_between_packets=delay_between_packets, 
                            max_outstanding_packets=max_outstanding_packets, 
                            timeResolutionUnit=self.timeResolutionUnit,
                            startAt=startAt,
                            debug=self.debug
                            ) 
        self.clients[self.nextClientId] = client
        self.nextClientId += 1

        if self.debug:
            logging.info(f"{self.name}: created node {client}")

        return client


    def createTCPClient(self, deliveryRatePerS, max_outstanding_packets, startAt=0):

        delay_between_packets = self.getDelayBetweenPacketsFromDeliveryRatePerS(deliveryRatePerS)
        client = TCPClient(
                            self.nextClientId, 
                            delay_between_packets=delay_between_packets, 
                            max_outstanding_packets=max_outstanding_packets, 
                            timeResolutionUnit=self.timeResolutionUnit,
                            startAt=startAt,
                            debug=self.debug
                            ) 
        self.clients[self.nextClientId] = client
        self.nextClientId += 1

        if self.debug:
            logging.info(f"{self.name}: created node {client}")

        return client

    def createTCPClients(self, n, deliveryRatePerS, max_outstanding_packets, startAt=0):

        clients = []
        for _ in range(n):
            clients.append(self.createTCPClient(deliveryRatePerS, max_outstanding_packets, startAt=startAt))
        
        return clients
from core.Client import Client
from core.SenderType import SenderType
import logging
import math
import numpy as np
from library.TimeUtils import TimeUtils

class ConstClient(Client):

    def __init__(self, id, deliveryRate,
            timeResolutionUnit, 
            resolution=1, 
            debug=True,):
        """[summary]

        Args:
            id ([type]): [description]
            deliveryRate ([type]): number of packets in S
            debug (bool, optional): [description]. Defaults to True.
            timeResolutionUnit (str, optional): [description]. 
            resolution (int, optional): [description]. Defaults to 1.
        """
        super().__init__(id, SenderType.Noob, deliveryRate=deliveryRate, debug=debug, resolution=resolution, timeResolutionUnit=timeResolutionUnit)

        self._deliveryRateInTRU = 0
        self.setDeliveryRate(deliveryRate)
        self.totalPacketsCreated = 0


    def __str__(self):
        parentStr = super().__str__()

        return (
            f"{parentStr}"
            f"\n\tdeliveryRateInTRU: {self._deliveryRateInTRU}"
            f"\n\ttotalPacketsCreated: {self.totalPacketsCreated}\n"
        )
    
    def setDeliveryRate(self, deliveryRate):

        self._deliveryRate = deliveryRate
        self._deliveryRateInTRU = self._deliveryRate / TimeUtils.convertTime(1, 's', self.timeResolutionUnit)
        

    def getNumberOfPacketsToCreateForTimeStep(self, timeStep):

        # deliveryRate is per second
        numPackets = int(round((timeStep - self.lastTimeStep) * self._deliveryRateInTRU, 0))
        self.totalPacketsCreated += numPackets

        return numPackets
        

    def onTimeStepStart(self, timeStep):
        """To be called at the beginning of a timeStep

        Args:
            timeStep ([type]): [description]
        """
        pass


    def onTimeStepEnd(self, timeStep):
        """To be called at the end of a timeStep

        Args:
            timeStep ([type]): [description]
        """
        pass



    def onTimeStep(self, timeStep):
        """To be called at the end of a timeStep

        Args:
            timeStep ([type]): [description]
        """
        # if self.debug:
        #     logging.debug(f"{self.thread.getName()}: running at timeStep {timeStep}")

        # packets = self.createPacketsForTimeStep(timeStep)

        # # send the packets to next node
        # self.send(packets, timeStep)

        # pass
        return



    

    def onACK(self, packet, timeStep=None):

        super().onACK(packet, timeStep=timeStep)

        if self.debug:
            logging.debug(f"Client {self.id}: got ACK for packet no {packet.getPacketNumber()}")
        # packet loss conditions:
        # 1. ACK out of order.
        # 2. 
        # if self.debug:
        #     logging.info(f"{self.getName()}: got ack for packet {packet.getPacketNumber()}")
        pass

    
    def onShutDown(self, maxSteps):
        super().onShutDown(maxSteps)
from core.Client import Client
from core.SenderType import SenderType
import logging
import math
import numpy as np

class ConstClient(Client):

    def __init__(self, id, deliveryRate, debug=True,
    
            timeResolutionUnit='ms', 
            resolution=1):
        super().__init__(id, SenderType.Noob, deliveryRate=deliveryRate, debug=debug, resolution=resolution, timeResolutionUnit=timeResolutionUnit)

    def getNumberOfPacketsToCreateForTimeStep(self, timeStep):

        # deliveryRate is per second
        
        if self.timeResolutionUnit == 'ms':
            return ((timeStep - self.lastTimeStep) * self.deliveryRate) // 1000
        if self.timeResolutionUnit == 'mcs':
            # if timeStep >= 1000:
            #     print('h')
            return ((timeStep - self.lastTimeStep) * self.deliveryRate) // 1000_000
        if self.timeResolutionUnit == 'ns':
            return ((timeStep - self.lastTimeStep) * self.deliveryRate) // 1000_000_000
        

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
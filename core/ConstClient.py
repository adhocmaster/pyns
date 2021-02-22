from core.Client import Client
from core.SenderType import SenderType
import logging
import math
import numpy as np

class ConstClient(Client):

    def __init__(self, id, deliveryRate, debug=True):
        super().__init__(id, SenderType.Noob, deliveryRate=deliveryRate, debug=debug)

    def getNumberOfPacketsToCreateForTimeStep(self, timeStep):
        # num = math.floor(timeStep * self.deliveryRate)  - math.floor((self.lastTimeStep) * self.deliveryRate)
        num = ((timeStep - self.lastTimeStep) * self.deliveryRate) // 1000
        # print(num)
        # randomness
        # if self.debug:
        #     logging.info(f"Sender #{self.id} creating {numberOfPackets} packets at {timeStep}")
        # return math.floor( num * np.random.uniform(0.5, 1.1))
        return num
        

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
        logging.debug(f"{self.thread.getName()}: running at timeStep {timeStep}")
        pass



    

    def onACK(self, packet):

        super().onACK(packet)
        # packet loss conditions:
        # 1. ACK out of order.
        # 2. 
        # if self.debug:
        #     logging.info(f"{self.getName()}: got ack for packet {packet.getPacketNumber()}")
        pass
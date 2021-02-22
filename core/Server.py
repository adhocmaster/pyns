from core.NodeType import NodeType
from core.Node import Node
import queue, math, logging
import numpy as np
from core.Network import Network


class Server(Node):

    
    def __init__(
                    self, 
                    id,
                    debug=True
                ):
        super().__init__(id, NodeType.Server, debug=debug)
        self.ttlNoise = 10
        

    def onIncomingPacket(self, packet, timeStep):

        # the magic.
        packet.ackAt = timeStep + self.ttlNoise
        packet.ttl = packet.ackAt - packet.sentAt

        pass

    def onTimeStep(self, timeStep):
        """To be called at the end of a timeStep

        Args:
            timeStep ([type]): [description]
        """
        pass


    def getDataInFlightInKB(self):
        raise NotImplementedError()


    def getDataInQueueInKB(self):
        raise NotImplementedError()

    

    def getQueueSize(self):
        raise NotImplementedError()

    def getNumPacketInflight(self):
        raise NotImplementedError()

    def isOverflowed(self):
        raise NotImplementedError()

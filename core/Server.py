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

        if self.debug:
            if packet.curNode is None:
                logging.info(f"Server {self.id}: incoming packet from sender {packet.sender.id}")
            else:
                logging.info(f"Server {self.id}: incoming packet from node {packet.curNode.id}")
        
        # TODO do a godly ack back to the sender.

        packet.sender.onACK(packet)

        pass

    def onTimeStep(self, timeStep):
        """To be called at the end of a timeStep

        Args:
            timeStep ([type]): [description]
        """
        pass


    def getDataInFlightInKB(self):
        raise NotImplementedError()

    def getDataInQueueInBytes(self):
        raise NotImplementedError()

    def getDataInQueueInKB(self):
        raise NotImplementedError()

    

    def getQueueSize(self):
        raise NotImplementedError()

    def getNumPacketInflight(self):
        raise NotImplementedError()

    def isOverflowed(self):
        raise NotImplementedError()

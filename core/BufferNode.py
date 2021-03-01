from core.SimpleNode import SimpleNode
from core.NodeType import NodeType
import heapq
import numpy as np
import logging


class BufferNode(SimpleNode):
    """BufferNode does not have a queue, instead there is a map of packets which can be removed at will. No pop method.

    Args:
        SimpleNode ([type]): [description]
    """

    def __init__(
                    self, 
                    id,
                    maxDeliveryRate,
                    transmissionDelayPerByte = 0.0001,
                    maxDataInPipe=100000,
                    maxQsize = 10000, 
                    avgTTL=20, noiseMax=20,
                    debug=True, 
                    resolution=1
                ):

        super().__init__(id,
                        maxDeliveryRate=maxDeliveryRate,
                        transmissionDelayPerByte=transmissionDelayPerByte,
                        maxQsize=maxQsize,
                        maxDataInPipe=maxDataInPipe, avgTTL=avgTTL, noiseMax=noiseMax, debug=debug, resolution=1)
        self.nodeType = NodeType.HeapNode
        self.queue = []
        self.name = f"HeapNode {self.id}"
    
    
    # Queue methods start
    def getDataInQueueInBytes(self):
        s = 0
        for packet in self.queue: # accessing underlying deque, so, items are not consumed
            s += packet.size
        return s

    
    def getDataInQueueInKB(self):
        return round(self.getDataInQueueInBytes(), 2)


    
    def addToQueue(self, packet):

        if self.isOverflowed():
            logging.warn(f"{self.name}: packet {packet.id} dropped")
            raise Exception(f"{self.name}: queue overflowed")
        else:
            heapq.heappush(self.queue, packet)

    
    def getFromQueue(self):
        if len(self.queue) == 0:
            return None
        return heapq.heappop(self.queue)

    
    def getQueueSize(self):
        return len(self.queue)

    
    def isOverflowed(self):
        return self.getQueueSize() >= self.maxQsize

    # Queue methods end

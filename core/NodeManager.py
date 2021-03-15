from core.SimpleNode import SimpleNode
from core.HeapNode import HeapNode
from core.NodeType import NodeType
import numpy as np
from library.Configuration import Configuration
import logging
from library.TimeUtils import TimeUtils

class NodeManager:

    def __init__(self, timeResolutionUnit):
        self.nodes = {}
        self.nextNodeId = 1
        self.timeResolutionUnit = timeResolutionUnit
        self.config = Configuration()
        self.name = "NodeManager"


    def reset(self):

        for node in self.nodes.values():
            node.resetStats()


    def getTransmissionDelayPerByteFromDeliverRate(self, deliveryRateInS):
        # may be this should go to node implementation

        avgPacketSize = (self.config.get('minPacketSize') + self.config.get('maxPacketSize')) / 2
        bytesPerSecond = (deliveryRateInS * avgPacketSize)
        timeToTransmitAByte = TimeUtils.convertTime(1, 's', self.timeResolutionUnit, round=False) / bytesPerSecond
        return timeToTransmitAByte


    def createSimpleNode(self, 
            maxDeliveryRate=50,
            maxDataInPipe=100000,
            maxQsize = 10000, 
            debug=True, 
            resolution=1):

        
        transmissionDelayPerByte = self.getTransmissionDelayPerByteFromDeliverRate(maxDeliveryRate)
        
        newNode = SimpleNode(self.nextNodeId, 
                            timeResolutionUnit=self.timeResolutionUnit,
                            transmissionDelayPerByte = transmissionDelayPerByte,
                            maxDataInPipe=maxDataInPipe, 
                            maxQsize = maxQsize, 
                            debug=debug, 
                            resolution=resolution)
        self.nodes[newNode.id] = newNode
        self.nextNodeId += 1

        logging.info(f"{self.name}: created node {newNode}")
        return newNode
        
    
    def createSimpleNodes(self, n, 
            maxDeliveryRate=50,
            maxDataInPipe=100000,
            maxQsize = 10000, 
            debug=True, 
            resolution=1):

        
        
        for _ in range(n):
            self.createSimpleNode(
                            maxDeliveryRate=maxDeliveryRate, 
                            maxDataInPipe=maxDataInPipe, 
                            maxQsize = maxQsize, 
                            debug=debug, 
                            resolution=resolution
                            )
        
        return self.nodes.values()

    def createHeapNode(self,
            maxDeliveryRate=50,
            maxDataInPipe=100000,
            maxQsize = 10000, 
            debug=True, 
            resolution=1):
        
        transmissionDelayPerByte = self.getTransmissionDelayPerByteFromDeliverRate(maxDeliveryRate)
        newNode = HeapNode(self.nextNodeId, 
                            maxDeliveryRate=maxDeliveryRate, 
                            transmissionDelayPerByte = transmissionDelayPerByte,
                            maxDataInPipe=maxDataInPipe, 
                            maxQsize = maxQsize, 
                            debug=debug, 
                            resolution=resolution)
        self.nodes[newNode.id] = newNode
        self.nextNodeId += 1
        return newNode
        
    
    def createHeapNodes(self, n, 
            maxDeliveryRate=50,
            maxDataInPipe=100000,
            maxQsize = 10000, 
            debug=True, 
            resolution=1):
        
        for _ in range(n):
            self.createHeapNode(
                            maxDeliveryRate=maxDeliveryRate, 
                            maxDataInPipe=maxDataInPipe, 
                            maxQsize = maxQsize, 
                            debug=debug, 
                            resolution=resolution
                            )
        
        return self.nodes.values()

    
    def getRandomNodes(self, maxN):

        if maxN >= len(self.nodes):
            return list(self.nodes.values())

        return list(np.random.choice(list(self.nodes.values()), maxN, replace=False))



    def startNodes(self):
        for node in self.nodes.values():
            node.start()
    
    def stopNodes(self):
        for node in self.nodes.values():
            node.stop()
    
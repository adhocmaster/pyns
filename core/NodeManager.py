from core.SimpleNode import SimpleNode
from core.NodeType import NodeType
import numpy as np

class NodeManager:

    def __init__(self):
        self.nodes = {}
        self.nextNodeId = 0

    def createNode(self, nodeType, maxDeliveryRate,
            maxDataInPipe=1000.0, debug=True, resolution=1):
        
        newNode = SimpleNode(self.nextNodeId, maxDeliveryRate=maxDeliveryRate, maxDataInPipe=maxDataInPipe, resolution=resolution)
        self.nodes[newNode.id] = newNode
        self.nextNodeId += 1
        return newNode
        
    
    def createSimpleNodes(self, n, maxDeliveryRate=50,
            maxDataInPipe=1000.0, debug=True, resolution=1):
        
        for _ in range(n):
            self.createNode(nodeType=NodeType.SimpleQueue, maxDeliveryRate=maxDeliveryRate, maxDataInPipe=maxDataInPipe, debug=debug, resolution=resolution)
        
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
    
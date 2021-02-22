from core.Node import Node
from core.NodeType import NodeType

class NodeManager:

    def __init__(self):
        self.nodes = {}
        self.nextNodeId = 0

    def createNode(self, nodeType: NodeType=NodeType.SimpleQueue,
            maxDataInPipe=1000.0,
            avgTTL=20, noiseMax=20, debug=True):
        
        newNode = Node(self.nextNodeId, nodeType=nodeType, maxDataInPipe=maxDataInPipe, )
        


    def startNodes(self):
        for node in self.nodes:
            node.start()

from core.Node import Node
from core.Client import Client
from core.Path import Path

class PathManager:
    
    def __init__(self):
        self.channels = {} # keys are informat 'fromId-toId', values are float denoting transmission delay in ms. All the nodes that have point to point links must have an entry here. unidirectional only. For bidirectional, two entries needs to be created.
        self.nextPathId = 0
        self.paths = {}

    # Channels
    def getChannelKey(self, fromNode, toNode):
        return f"{fromNode.id}-{toNode.id}"

    def createChannels(self, node1, node2, delay=2, biDirectional=True):

        self.channels[self.getChannelKey(node1, node2)] = delay
        if biDirectional:
            self.channels[self.getChannelKey(node2, node1)] = delay

    
    def hasChannel(self, fromNode, toNode):
        if self.getChannelKey(fromNode, toNode) in self.channels:
            return True
        return False


    def updateChannel(self, fromNode, toNode, delay=2):
        self.channels[self.getChannelKey(fromNode, toNode)] = delay

    
    # Paths
    def createPath(self, client=None, nodes=None, server=None):
        newPathId = self.nextPathId
        self.paths[newPathId] = Path(newPathId, client=client, nodes=nodes, server=server)
        self.nextPathId += 1
        return newPathId


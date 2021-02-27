import time
import logging
from core.NodeManager import NodeManager
from core.Network import Network
from core.ConstClient import ConstClient
from core.Server import Server
from event.EventSimulator import EventSimulator
from library.TimeUtils import TimeUtils

logging.basicConfig(level=logging.DEBUG)



network = Network.get()
nodeManager = NodeManager()
nodeManager.createSimpleNodes(n=10, resolution=10, debug=False)

randomNodes = nodeManager.getRandomNodes(5)
randomNodes2 = nodeManager.getRandomNodes(2)

client = ConstClient(1, deliveryRate=1000, debug=True, resolution=10)
client2 = ConstClient(2, deliveryRate=2000, debug=True, resolution=10)
server = Server(-1)

path = network.createPath(client=client, nodes=randomNodes, server=server)
path2 = network.createPath(client=client2, nodes=randomNodes2, server=server)


print("path for client1:")
print([node.id for node in path.getNodesWithServer()])
print("path for client2:")
print([node.id for node in path2.getNodesWithServer()])

simulator = EventSimulator(timeResolutionUnit="ms", debug=True)

simulator.addClient(client)
simulator.addClient(client2)

endAt = TimeUtils.getMS() + 10000

while TimeUtils.getMS() < endAt:
    simulator.step()
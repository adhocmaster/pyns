import time
import logging
from core.NodeManager import NodeManager
from core.Network import Network
from core.ConstClient import ConstClient
from core.Server import Server
from event.EventSimulator import EventSimulator
from library.TimeUtils import TimeUtils
from library.Configuration import Configuration

logging.basicConfig(level=logging.DEBUG, filename="debug.log")

print(f"Logging file at: debug.log")

config = Configuration()

timeResolutionUnit = config.get('timeResolutionUnit')
network = Network.get()
nodeManager = NodeManager()
nodeManager.createSimpleNodes(n=10, resolution=10, maxDeliveryRate=5000, debug=False)
# nodeManager.createHeapNodes(n=10, resolution=10, debug=False)

randomNodes = nodeManager.getRandomNodes(5)
randomNodes2 = nodeManager.getRandomNodes(2)

client = ConstClient(1, deliveryRate=1000, debug=True, timeResolutionUnit=timeResolutionUnit)
client2 = ConstClient(2, deliveryRate=2000, debug=True, timeResolutionUnit=timeResolutionUnit)
server = Server(-1)

path = network.createPath(client=client, nodes=randomNodes, server=server)
path2 = network.createPath(client=client2, nodes=randomNodes2, server=server)


logging.info("path for client1:")
logging.info([node.id for node in path.getNodesWithServer()])
logging.info("path for client2:")
logging.info([node.id for node in path2.getNodesWithServer()])

simulator = EventSimulator(timeResolutionUnit=timeResolutionUnit, debug=True)

simulator.addClient(client)
simulator.addClient(client2)

# endAt = TimeUtils.getMS() + 1000

# while TimeUtils.getMS() < endAt:
#     simulator.step()

maxSteps = 5000 # equivalent to maxStep timeResolution unit
for _ in range(maxSteps):
    simulator.step()

print(simulator.timeStep)
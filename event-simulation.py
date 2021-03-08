import time
import logging
from core.NodeManager import NodeManager
from core.Network import Network
from core.ConstClient import ConstClient
from core.AIClient import AIClient
from core.Server import Server
from event.EventSimulator import EventSimulator
from library.TimeUtils import TimeUtils
from library.Configuration import Configuration
from sim.AnalyzerTools import AnalyzerTools

logging.basicConfig(level=logging.INFO, filename="debug.log")

print(f"Logging file at: debug.log")

config = Configuration()

timeResolutionUnit = config.get('timeResolutionUnit')
network = Network.get()
nodeManager = NodeManager()
nodeManager.createSimpleNodes(n=4, resolution=10, maxDeliveryRate=5000, debug=False)
# nodeManager.createHeapNodes(n=10, resolution=10, debug=False)

randomNodes = nodeManager.getRandomNodes(3)
randomNodes2 = nodeManager.getRandomNodes(2)

client = ConstClient(1, deliveryRate=1000, debug=True, timeResolutionUnit=timeResolutionUnit)
client2 = AIClient(2, delay_between_packets=5, max_outstanding_packets=10, debug=True)
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

logging.info(simulator)

# endAt = TimeUtils.getMS() + 1000

# while TimeUtils.getMS() < endAt:
#     simulator.step()

maxSteps = 5000 # equivalent to maxStep timeResolution unit
simulator.run(maxSteps)
print(simulator.timeStep)

# visualization for client 2

analyzer = AnalyzerTools()

# analyzer.createPlotForTimeSteps(client2.stats, 'outStandingPackets')
# analyzer.createPlotsForTimeSteps(client2.stats, ['outStandingPackets', 'packetsAcked', 'totalPacketsSent', 'totalPacketsAcked', 'ttlMS'])
# analyzer.createPlotForTimeSteps(client2.stats, 'ttlMS')
analyzer.createPlotsForTimeSteps(client2.stats, ['outStandingPackets', 'packetsInFlight', 'packetsInQueue', 'ttlMS'])
analyzer.createPlotsForTimeSteps(client2.stats, ['bottleNeck', 'dataInFlight', 'dataInQueue', 'ttlMS'])
# 
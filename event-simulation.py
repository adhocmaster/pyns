import time
import logging
import numpy as np
from core.NodeManager import NodeManager
from core.ClientManager import ClientManager
from core.Network import Network
from core.ConstClient import ConstClient
from core.TCPClient import TCPClient
from core.Server import Server
from event.EventSimulator import EventSimulator
from library.TimeUtils import TimeUtils
from library.Configuration import Configuration
from sim.AnalyzerTools import AnalyzerTools

np.random.seed(39)

logfile = "debug.log"
with open(logfile, 'w') as f:
    f.truncate()
logging.basicConfig(level=logging.DEBUG, filename="debug.log")

print(f"Logging file at: debug.log")

config = Configuration()

timeResolutionUnit = config.get('timeResolutionUnit')
network = Network.get()
nodeManager = NodeManager(timeResolutionUnit)
nodeManager.createSimpleNodes(n=4, resolution=10, maxDeliveryRate=5000, debug=True)
# nodeManager.createHeapNodes(n=10, resolution=10, debug=False)

randomNodes = nodeManager.getRandomNodes(1)
randomNodes2 = nodeManager.getRandomNodes(2)

clientManager = ClientManager(timeResolutionUnit, debug=True)
clients = clientManager.createTCPClients(2, deliveryRatePerS=10000, max_outstanding_packets=10)
client = clients[0]
client2 = clients[1]
# client = ConstClient(1, deliveryRate=250, debug=True, timeResolutionUnit=timeResolutionUnit)
# client = TCPClient(1, delay_between_packets=50, max_outstanding_packets=10, debug=True) # delivery rate is 2k packets per sec for 500
# client2 = TCPClient(2, delay_between_packets=500, max_outstanding_packets=10, debug=True) # delivery rate is 2k packets per sec for 500


server = Server(-1)
server2 = Server(-2)

path = network.createPath(client=client, nodes=randomNodes, server=server)
path2 = network.createPath(client=client2, nodes=randomNodes2, server=server2)

logging.info("path for client1:" + str([node.id for node in path.getNodesWithServer()]))
logging.info("path for client2:" + str([node.id for node in path2.getNodesWithServer()]))

simulator = EventSimulator(timeResolutionUnit=timeResolutionUnit, nodeManager=nodeManager, debug=True)

simulator.addClient(client)
# simulator.addClient(client2)

logging.info(simulator)

# endAt = TimeUtils.getMS() + 1000

# while TimeUtils.getMS() < endAt:
#     simulator.step()

maxSteps = 10000 # equivalent to maxStep timeResolution unit 50ms
simulator.run(maxSteps)
print(simulator.timeStep)


# visualization for client 2

analyzer = AnalyzerTools()

# analyzer.createPlotForTimeSteps(client.stats, 'outStandingPackets')
# analyzer.createPlotsForTimeSteps(client.stats, ['outStandingPackets', 'packetsAcked', 'totalPacketsSent', 'totalPacketsAcked', 'rttMS'])
# # analyzer.createPlotForTimeSteps(client.stats, 'rttMS')
# analyzer.createPlotsForTimeSteps(client.stats, ['outStandingPackets', 'packetsInFlight', 'packetsInQueue', 'rttMS'])
# analyzer.createPlotsForTimeSteps(client.stats, ['bottleNeck', 'dataInFlight', 'dataInQueue', 'rttMS'])
# 

# What's important in client view?
# analyzer.createPlotsForTimeSteps(client.stats, ['outStandingPackets', 'packetsAcked', 'totalPacketsSent', 'totalPacketsAcked', 'rttMS'])
# analyzer.createPlotsForTimeSteps(client.stats, ['bottleNeck', 'dataInFlight', 'dataInQueue', 'rttMS'])
# analyzer.createPlotsForTimeSteps(randomNodes[0].stats, ['qSize', 'queued', 'dequeued', 'deliveryRateInS', 'utilization'])
analyzer.createPlotsForTimeSteps(randomNodes[0].stats, ['qSize', 'queued', 'dequeued', 'utilization'], title="Node 0 stats")
# print(randomNodes[0].stats)
# analyzer.createPlotsForTimeSteps(randomNodes[0].stats, ['qSize', 'queued', 'dequeued'])
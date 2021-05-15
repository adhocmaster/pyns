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
logging.basicConfig(level=logging.ERROR, filename="debug.log")

print(f"Logging file at: debug.log")

config = Configuration()

timeResolutionUnit = config.get('timeResolutionUnit')
network = Network.get()
nodeManager = NodeManager(timeResolutionUnit)
clientManager = ClientManager(timeResolutionUnit, debug=False)
client = clientManager.createTCPClient(deliveryRatePerS=1500, max_outstanding_packets=100)
client2 = clientManager.createPowerTWClient(pollCycle=2,rttWindowSize=5, bandWidthWindowSize=5, deliveryRatePerS=3000, max_outstanding_packets=100)
nodes = [
    nodeManager.createSimpleNode(maxDeliveryRate=10000, debug=False),
    nodeManager.createSimpleNode(maxDeliveryRate=2000, debug=False),
    nodeManager.createSimpleNode(maxDeliveryRate=5000, debug=False),
    nodeManager.createSimpleNode(maxDeliveryRate=3000, debug=False)
]
nodes2 = [
    nodeManager.createSimpleNode(maxDeliveryRate=1500, debug=False),
    nodes[1],
    nodeManager.createSimpleNode(maxDeliveryRate=5000, debug=False)
]

server = Server(-1, debug=False)
server2 = Server(-2, debug=False)

path = network.createPath(client=client, nodes=nodes, server=server)
path2 = network.createPath(client=client2, nodes=nodes2, server=server2)


logging.info("path for client1:" + str([node.id for node in path.getNodesWithServer()]))
logging.info("path for client2:" + str([node.id for node in path2.getNodesWithServer()]))

nodeManager.reset()
simulator = EventSimulator(timeResolutionUnit=timeResolutionUnit, nodeManager=nodeManager, debug=False, printStatFreq=10000)
simulator.addClient(client)
simulator.addClient(client2)

maxSteps = 500000 # equivalent to maxStep timeResolution unit
simulator.run(maxSteps)

# visualization for client 2

analyzer = AnalyzerTools()
binSize = 500
clients = [client, client2]
analyzer.binStats(nodes, columnNames= ['qSize', 'utilization'], binSize=binSize, method=np.max)
analyzer.binStats(nodes2, columnNames= ['qSize', 'utilization'], binSize=binSize, method=np.max)
analyzer.binStats(clients, columnNames= ['outStandingPackets', 'rttMS', 'actualRttMS'], binSize=binSize, method=np.median)
analyzer.createBinnedChartForNodeVsClient(nodes2, ['qSize'], [client2], ['outStandingPackets', 'rttMS', 'actualRttMS'], start=0, end=4000)
analyzer.createPacketVsRTT(client2)
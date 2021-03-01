from abc import ABC
from library.TimeUtils import TimeUtils
from event.PacketEvent import PacketEvent
from event.EventTypes import EventTypes
import logging
import math

class PacketEventManager(ABC):

    def __init__(self, timeResolutionUnit, debug=False):
        self.timeResolutionUnit = timeResolutionUnit
        self.name="PacketEventManager"
        self.checkQueueEvents = {}
        self.debug = debug

    
    def getQueueEventName(self, node, timeStep):
        return f"{node.id}-{timeStep}"


    def getQueueEvent(self, eventName):
        return self.checkQueueEvents.get(eventName, None)


    # def createQueueEvent(self, node, timeStep):
    #     return PacketEvent()


    def processEvent(self, simulator, eventType, packet):
        
        method = getattr(self, eventType.name)
        return method(simulator, packet)


    def EnterChannel(self, simulator, packet):
        """Entering channel has transmission delay. Transmission delay is the time to push bits into a wire.
           Schedules an ArriveNode event with transmission delay from now
           

        Args:
            packet ([type]): [description]
        """

        # remove from current queue and schedule channel transmission
        if packet.curNodeIndex >= 0:
            curNode = packet.curNode
            qPacket = curNode.getFromQueue()
            if qPacket.id != packet.id:
                raise Exception(f"Something happend in queue. Rmoved packet {qPacket.id} != {packet.id} ")
            
            delayMS = curNode.transmissionDelayPerByte * packet.size
            arriveEventTimeStep = math.ceil(simulator.timeStep + simulator.convertTimeToSimulatorUnit(delayMS, 'ms'))
            curNode.channelBusyUntil = arriveEventTimeStep
            
            if self.debug:
                logging.debug(f"{self.name}: {simulator.timeStep}: Scheduled Arrive Event at {arriveEventTimeStep}")

            e = PacketEvent(EventTypes.ArriveNode, arriveEventTimeStep, packet)
            return [e]
        
        else:
            raise Exception(f"Packet {packet.id} is not in the path")
            
        return []



    def getTimeToTransmit(self, node):
        # maxDeliveryRate is in seconds
        numInQ = node.getQueueSize()
        timeToSendInMS = (numInQ * 1000) // node.maxDeliveryRate

        if self.timeResolutionUnit == "ms":
            return timeToSendInMS
        if self.timeResolutionUnit == "mcs":
            return timeToSendInMS * 1000
        if self.timeResolutionUnit == "ns":
            return timeToSendInMS * 1000_000
        


    
    def ArriveNode(self, simulator, packet):
        """Arrives to the next node in the path

        Args:
            simulator ([type]): [description]
            packet ([type]): [description]
        """

        # timeStep = TimeUtils.getMS()
        timeStep = simulator.timeStep

        # 1. update curNode and curNodeIndex and release previous channel
        if packet.curNodeIndex < 0:
            packet.curNodeIndex = 0
        else:
            packet.curNodeIndex += 1

        # it will never overflow as server stops the packet propagation
        if (packet.curNodeIndex + 1) == len(packet.path.getNodesWithServer()):
            # arriving at server
            packet.path.server.onIncomingPacket(packet, timeStep)
            return []

        packet.curNode = packet.path._nodes[packet.curNodeIndex]
        packet.nodeReceivedAt = timeStep # when the packet arrived to the queue.
        curNode = packet.curNode

        # 2. TODO add to queue
        # channelTimeStep = when the packet needs to be removed from queue and pushed to channel
        # we need to how many packets we have in queue right now.
        # bytesInQueue = packet.curNode.getDataInQueueInBytes()
        # delivery rate in num packets
        # assuming queue is always delivering

        timeToTransmit = self.getTimeToTransmit(curNode)
        channelTimeStep = timeStep + timeToTransmit + 1 # added one so that, other other pending events at the same timeStep does not wait.
        if curNode.channelBusyUntil > timeStep:
            logging.warn(f"{self.name}: {timeStep}: Channel {curNode.id} is busy until {curNode.channelBusyUntil}")
            channelTimeStep = curNode.channelBusyUntil + timeToTransmit 

        try:
            # add to Queue
            curNode.addToQueue(packet)

            e = PacketEvent(EventTypes.EnterChannel, channelTimeStep, packet)

            if self.debug:
                logging.debug(f"{self.name}: {timeStep}: Packet {packet.id} arrrived at node {curNode.id}")
                logging.debug(f"{self.name}: {timeStep}: Scheduled Channel Event at {channelTimeStep}")

            return [e]
        except Exception as e:
            if self.debug:
                logging.warn(e)
        
        return []

    def initiatePacketEvents(self, simulator, timeStep, packets):
        """This packets are entering the network from a client

        Args:
            packets ([type]): [description]
        """
        for packet in packets:
            e = PacketEvent(EventTypes.ArriveNode, timeStep, packet)
            simulator.add_event(e)



        

        
from abc import ABC
from library.TimeUtils import TimeUtils
from event.PacketEvent import PacketEvent
from event.EventTypes import EventTypes
import logging

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


    def createQueueEvent(self, node, timeStep):
        return PacketEvent()


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
            qPacket = packet.curNode.getFromQueue()
            if qPacket.id != packet.id:
                raise Exception(f"Something happend in queue. Rmoved packet {qPacket.id} != {packet.id} ")

            delayMS = packet.curNode.transmissionDelayPerByte * packet.size
            e = PacketEvent(EventTypes.ArriveNode, TimeUtils.getMS()+delayMS, packet)
            return [e]
        
        else:
            raise Exception(f"Packet {packet.id} is not in the path")
            
        return []



    
    def ArriveNode(self, simulator, packet):
        """Arrives to the next node in the path

        Args:
            simulator ([type]): [description]
            packet ([type]): [description]
        """

        timeStep = TimeUtils.getMS()

        # 1. update curNode and curNodeIndex
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
        curNode = packet.curNode

        # 2. TODO add to queue
        # channelTimeStep = when the packet needs to be removed from queue and pushed to channel
        # we need to how many packets we have in queue right now.
        # bytesInQueue = packet.curNode.getDataInQueueInBytes()
        # delivery rate in num packets
        # assuming queue is always delivering
        numInQ = curNode.getQueueSize()
        timeToSendInMS = (numInQ * 1000) // curNode.maxDeliveryRate
        channelTimeStep = timeStep + timeToSendInMS

        curNode.addToQueue(packet)

        # schedule Channel event
        e = PacketEvent(EventTypes.EnterChannel, channelTimeStep, packet)

        if self.debug:
            logging.debug(f"{self.name}: {timeStep}: Packet {packet.id} arrrived at node {curNode.id}")
            logging.debug(f"{self.name}: {timeStep}: Scheduled Channel Event at {channelTimeStep}")

        # 3. schedule check queue even if none for the queue already exists in the future timeStep

        # eventName = self.getQueueEventName(packet.curNode, timeStep)
        
        # if self.getQueueEvent(eventName) is not None:
        #     # create an event
        #     e = PacketEvent(EventTypes.CheckQueue, timeStep)
        #     return [e]

    
        return [e]

    def initiatePacketEvents(self, simulator, timeStep, packets):
        """This packets are entering the network from a client

        Args:
            packets ([type]): [description]
        """
        for packet in packets:
            e = PacketEvent(EventTypes.ArriveNode, timeStep, packet)
            simulator.add_event(e)



        

        
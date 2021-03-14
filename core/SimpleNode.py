from core.NodeType import NodeType
from core.Node import Node
import queue, math, logging
import numpy as np
from core.Network import Network
from library.TimeUtils import TimeUtils

class SimpleNode(Node):

    def __init__(
                    self, 
                    id,
                    timeResolutionUnit, 
                    transmissionDelayPerByte,
                    maxDataInPipe=100000,
                    maxQsize = 10000, 
                    avgTTL=20, noiseMax=20,
                    debug=True, 
                    resolution=1
                ):

        """[summary]
    
        Raises:
            Exception: [description]
        """

        super().__init__(id, NodeType.SimpleQueue,
                        transmissionDelayPerByte=transmissionDelayPerByte,
                        maxDataInPipe=maxDataInPipe, avgTTL=avgTTL, noiseMax=noiseMax, debug=debug, resolution=1,
                        timeResolutionUnit=timeResolutionUnit)

        self.maxQsize = maxQsize
        self.queue = queue.Queue(maxsize=maxQsize)
        self.timeStep = 0
        self.lastTimeStep = None
       
    
    def __str__(self):

        nodeProps = super().__str__()

        return (
            f"{nodeProps}"
            f"\nmaxDeliveryRate: {self.getDeliveryRateInS(30)} packets/s for 30 byte packets"
            f"\nmaxQsize: {self.maxQsize} packets"
        )
    
    def getDeliveryRateInS(self, packetSize):
        timeToTransmitAPacket = self.getTimeToTransmit(packetSize)
        return TimeUtils.convertTime(1, 's', self.timeResolutionUnit, round=True) // timeToTransmitAPacket
    
    def onIncomingPacket(self, packet, timeStep):
        
        
        if self.debug:
            if packet.curNode is None:
                logging.info(f"SimpleNode {self.id}: incoming packet from sender {packet.sender.id}")
            else:
                logging.info(f"SimpleNode {self.id}: incoming packet from node {packet.curNode.id}")

        """
        1. when a packet arrives, it has a path object
        """

        packet.curNode = self
        packet.nextNode = packet.path.getNextNode(self.id)
        packet.nodeReceivedAt = timeStep
        self.addToQueue(packet)
        
        pass
    
    
    # def onIncomingPackets(self, packets):
    #     """ It assumes infinite arrival and delivery rate. This method is called every time step for every sender seperately."""
    #     if self.debug:
    #         logging.info(f"SimpleNode: {len(packets)} incoming packets from sender {packets[0].sender.id}")
    #     for packet in packets:
    #         self.addToQueue(packet)
    #     pass
    
    # def deliverOrEnqueuePacket(self, packet):
    #     if self.isPipeFull():
    #         # add to queue if pipe is full
    #         self.addToQueue(packet)
    #     else:
    #         # else, update ttl and add to pipe
    #         self.updateTTL(packet)
    #         self.addToPipe(packet)
    #     pass

    
    # def onTimeStepStart(self, timeStep):
    #     self.ackPackets = self.getPacketsByTimeStep(timeStep)
    #     self.tryDeliveringFromQueue(timeStep) # assumes infinite delivery rate.

    # def onTimeStepEnd(self, timeStep):
    #     """To be called at the end of a timeStep

    #     Args:
    #         timeStep ([type]): [description]
    #     """
    #     pass
    
    def getNumberOfPacketsToDeliver(self, timeStep):
        # delivery rate is in seconds, timeStep in ms
        num = ((timeStep - self.lastTimeStep) * self.maxDeliveryRate) // 1000
        return num

    def onTimeStep(self, timeStep):

        self.tryDeliveringFromQueue(timeStep, limit=self.getNumberOfPacketsToDeliver(timeStep))
        flushedPackets = self.getPipePacketsByTimeStep(timeStep)

        if self.debug and len(flushedPackets) > 0:
            logging.debug(f"SimpleNode {self.id}: flushing out {len(flushedPackets)} to next nodes")


        for packet in flushedPackets:
            packet.nextNode.onIncomingPacket(packet, timeStep)
        


    def tryDeliveringFromQueue(self, timeStep, limit=None):
        numDelivered = 0
        if self.isPipeFull() is False:
            sizeQBeforeFlushing = self.getQueueSize()
            while self.queue.empty() is False:
                packet = self.getFromQueue()
                self.schedulePacketForDelivery(packet, timeStep)
                numDelivered += 1
                if self.isPipeFull() is True:
                    break
                if limit is not None:
                    if numDelivered >= limit:
                        break

            if self.debug and numDelivered > 0:
                logging.info(f"SimpleNode {self.id}: #{numDelivered} of {sizeQBeforeFlushing} packets were sent to pipe from the queue")

        return numDelivered

    def schedulePacketForDelivery(self, packet, timeStep):
        # self.updateTTL(packet)
        # adjust for waiting time
        # packet.ackAt = timeStep + packet.ttl
        # packet.ttl = packet.ackAt - packet.sentAt 
        packet.nodeLeaveAt = timeStep + Network.get().getDelay(self, packet.nextNode)
        self.addToPipe(packet, packet.nodeLeaveAt)


    # def getACKs(self):
    #     return self.ackPackets

    
    def getNumPacketInflight(self):
        # return self.getNumPacketInPipe() + self.getQueueSize()
        if self.channelPacket is None:
            return self.getQueueSize()
        return self.getQueueSize() + 1
        

    def updateTTL(self, packet):
        packet.ttlNoise = np.random.randint(0, self.noiseMax)
        packet.ttl = math.floor( self.avgTTL + self.avgTTL * (self.getQueueSize() / self.maxQsize) + packet.ttlNoise )
        packet.ackAt = packet.sentAt + packet.ttl
        pass


    def getDataInFlightInKB(self):
        # return self.getDataInPipeInKB() + self.getDataInQueueInKB()
        if self.channelPacket is None:
            return self.getDataInQueueInKB()
        return (self.channelPacket.size / 1000) + self.getDataInQueueInKB()
    
    # Queue methods start
    def getDataInQueueInBytes(self):
        s = 0
        for packet in self.queue.queue: # accessing underlying deque, so, items are not consumed
            s += packet.size
        return s

    
    def getDataInQueueInKB(self):
        return round(self.getDataInQueueInBytes() / 1000, 2)


    def getTimeToFlushQueue(self):
        timeToTransmit = 0
        for packet in self.queue.queue: # accessing underlying deque, so, items are not consumed
            timeToTransmit += self.getTimeToTransmit(packet.size)
        return timeToTransmit

    
    def addToQueue(self, packet):

        try:
            self.queue.put(packet, block=False)
        except queue.Full:
            # packet dropped
            logging.warn(f"SimpleNode {self.id}: packet {packet.id} dropped")
            pass
    
    def getFromQueue(self):
        try:
            return self.queue.get(block=False)
        except queue.Empty:
            return None

    
    def getQueueSize(self):
        """[summary]

        Returns:
            [type]: approximate queue size
        """
        return self.queue.qsize()

    
    def isOverflowed(self):
        return self.getQueueSize() >= self.maxQsize

    # Queue methods end
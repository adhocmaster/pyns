from abc import abstractmethod
from core.TCPClient import TCPClient
import queue, math, logging
from library.TimeUtils import TimeUtils
from library.Window import Window


class AdaptiveClient(TCPClient):
    

    def __init__(self, id, rttWindowSize, bandWidthWindowSize, delay_between_packets, max_outstanding_packets, timeResolutionUnit, debug=True):

        super().__init__(id, 
                        delay_between_packets=delay_between_packets,
                        max_outstanding_packets=max_outstanding_packets,
                        timeResolutionUnit=timeResolutionUnit,
                        debug=debug
                        )

        self.rttWindowSize = rttWindowSize
        self.rttQueue = Window(maxsize=rttWindowSize)
        self.bandWidthWindowSize = bandWidthWindowSize
        self.bandWidthQueue = Window(maxsize=bandWidthWindowSize)
        self.lastAckedPacket = None
    
    def resetStats(self):
        super().resetStats()
        self.queue = queue.Queue(maxsize=self.rttWindowSize)
        self.bandWidthQueue = queue.Queue(maxsize=self.bandWidthWindowSize)


    def getAvgRTTWindow(self):
        """in timeResolutionUnit

        Returns:
            [type]: [description]
        """

        numPackets = self.rttQueue.qsize()
        if numPackets == 0:
            return 1000 # big number not to overflow the graph
        
        s = 0
        for packet in self.rttQueue.queue:
            s += packet.ttl

        return s / numPackets

    
    def getCurrentDeliveryRatePerS(self):

        numPackets = self.bandWidthQueue.qsize()
        if numPackets < 2:
            return 0

        firstAckedAt = self.bandWidthQueue.queue[0].ackAt
        lastAckedAt = self.bandWidthQueue.queue[-1].ackAt
        return (numPackets * TimeUtils.convertTime(1, 's', self.timeResolutionUnit)) / (lastAckedAt - firstAckedAt)
    
    def getCurrentDeliveryRate(self):

        numPackets = self.bandWidthQueue.qsize()
        if numPackets < 2:
            return 0

        firstAckedAt = self.bandWidthQueue.queue[0].ackAt
        lastAckedAt = self.bandWidthQueue.queue[-1].ackAt
        return numPackets / (lastAckedAt - firstAckedAt)

    def getThroughput(self):
        return self.getCurrentDeliveryRatePerS() / self.getMaxDeliveryRatePerS()

    def getRTTTrend(self):
        """+ increasing rtt, - decreasing, 0, same

        Returns:
            [type]: [description]
        """
        return self.lastAckedPacket.ttl - self.getAvgRTTWindow() 

    def getBandWidth(self):
        return self.outstanding_packets / self.getAvgRTTWindow()

    def getPower(self):
        # return self.getCurrentDeliveryRate() / self.getAvgRTTWindow()
        return self.getBandWidth() / self.getAvgRTTWindow()

    
    def onACK(self, packet, timeStep=None):
        super().onACK(packet, timeStep)
        self.lastAckedPacket = packet

        if self.rttQueue.qsize() == self.rttWindowSize:
            self.rttQueue.get()
        self.rttQueue.put(packet)
        if self.bandWidthQueue.qsize() == self.bandWidthWindowSize:
            self.bandWidthQueue.get()
        self.bandWidthQueue.put(packet)
        self.updatePolicy()

    @abstractmethod
    def updatePolicy(self):
        pass


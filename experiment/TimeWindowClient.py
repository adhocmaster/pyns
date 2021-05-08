from abc import abstractmethod
from core.TCPClient import TCPClient
import queue, math, logging
from library.TimeUtils import TimeUtils
from library.Window import Window



class TimeWindowClient(TCPClient):
    """This client updates policy every pollcycle in rtt estimate

    Args:
        TCPClient ([type]): [description]
    """

    def __init__(self, 
                id, 
                pollCycle, 
                rttWindowSize, 
                bandWidthWindowSize, 
                delay_between_packets, 
                max_outstanding_packets, 
                timeResolutionUnit, 
                startAt=0,
                debug=True
                ):

        super().__init__(id, 
                        delay_between_packets=delay_between_packets,
                        max_outstanding_packets=max_outstanding_packets,
                        timeResolutionUnit=timeResolutionUnit,
                        startAt=startAt,
                        debug=debug
                        )

        self.pollCycle = pollCycle # 1 means 1 rtt. 0.5 means half the rtt
        self.lastPolledAt = startAt
        self._currentRTT = 9999999999
        self.rttWindowSize = rttWindowSize
        self.rttQueue = Window(maxsize=rttWindowSize)
        self.bandWidthWindowSize = bandWidthWindowSize
        self.bandWidthQueue = Window(maxsize=bandWidthWindowSize)
        self.lastAckedPacket = None
        self.stats['deliveryRateInS'] = []
    
    def resetStats(self):
        super().resetStats()
        self.stats['deliveryRateInS'] = []
        self.queue = queue.Queue(maxsize=self.rttWindowSize)
        self.bandWidthQueue = queue.Queue(maxsize=self.bandWidthWindowSize)


    def getCurrentRTT(self):
        # return self.getAvgRTTWindow()
        return self._currentRTT
        # try:
        #     return self.getAvgRTTWindow()
        # except:
        #     return None


    def getAvgRTTWindow(self):
        """in timeResolutionUnit

        Returns:
            [type]: [description]
        """

        numPackets = self.rttQueue.qsize()
        if numPackets == 0:
            # return 1000 # big number not to overflow the graph
            raise Exception("getAvgRTTWindow is not available yet.")
        
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
        return self.lastAckedPacket.ttl - self.getCurrentRTT() 

    def getBandWidth(self):
        return self.outstanding_packets / self.getCurrentRTT()

    def getPower(self):
        # return self.getCurrentDeliveryRate() / self.getAvgRTTWindow()
        return self.getBandWidth() / self.getCurrentRTT()

    
    def onACK(self, packet, timeStep=None):
        super().onACK(packet, timeStep)
        self.lastAckedPacket = packet
        self._currentRTT = packet.ackAt - packet.sentAt

        if self.bandWidthQueue.qsize() == self.bandWidthWindowSize:
            self.bandWidthQueue.get()
        self.bandWidthQueue.put(packet)

        # check if this is a probe time


        isProbe = False
        if self.lastPolledAt == 0:
            isProbe = True
        elif packet.ackAt >= (self.lastPolledAt + self.getCurrentRTT() * self.pollCycle):
            isProbe = True

        if isProbe == False:
            return

        if self.debug:
            logging.debug(f"{self.name}: probing at {timeStep} with currentRTT: {self.getCurrentRTT()}")

        self.lastPolledAt = packet.ackAt
        if self.rttQueue.qsize() == self.rttWindowSize:
            self.rttQueue.get()
        self.rttQueue.put(packet)
        self.updatePolicy()


    
    def onTimeStep(self, timeStep):
        super().onTimeStep(timeStep)
        self.stats['deliveryRateInS'].append(self.getCurrentDeliveryRatePerS())

    @abstractmethod
    def updatePolicy(self):
        pass


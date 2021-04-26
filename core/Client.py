from abc import ABC, abstractmethod
import time, collections
import threading
from core.Packet import Packet
from core.SenderType import SenderType
import math
import numpy as np
import logging
import pandas as pd

from library.TimeUtils import TimeUtils

class Client(ABC):

    def __init__(self, id, 
            senderType: SenderType, 
            timeResolutionUnit,
            deliveryRate = 0.1, 
            debug=True,
            startAt=0,
            resolution=1):
        self.lock = threading.RLock()
        self.id = id
        self.nextPacketNumber = 1
        self.type = senderType
        self._deliveryRate = deliveryRate # KB per second or number of packets depending on Client
        self.debug = debug
        self.ackedPackets = {}
        self.minPacketSize = 20 # bytes
        self.maxPacketSize = 40
        self.thread = None
        self.resolution = resolution # miliseconds.
        self.forceStop = False
        self.lastTimeStep = None # last timeStep when some packets were created
        self.nextNode = None
        self.path = None
        self.timeResolutionUnit = timeResolutionUnit
        self.simulator = None
        self.startAt = startAt
        self.stats = {}
        self.stats['packetsAcked'] = []
        self.stats['rttMS'] = []
        self.stats['actualRttMS'] = []

    
    def __str__(self):

        return (
        f"\n\tid: {self.id} \n"
        f"\ttype: {self.type} \n"
        f"\tdeliveryRate: {self.getDeliveryRate()} \n"
        f"\tnextPacketNumber: {self.nextPacketNumber} \n"

        f"\tdebug: {self.debug} \n"
        )

    
    @abstractmethod
    def resetStats(self):
        self.nextPacketNumber = 1
        self.ackedPackets = {}
        self.lastTimeStep = None # last timeStep when some packets were created
        self.nextNode = None

        self.stats = {}
        self.stats['packetsAcked'] = []
        self.stats['rttMS'] = []
        self.stats['actualRttMS'] = []

        self.stats['outStandingPackets'] = []
        self.stats['dataInFlight'] = []
        self.stats['packetsInFlight'] = []
        self.stats['packetsSent'] = []
        self.stats['packetsAcked'] = []
        self.stats['totalPacketsSent'] = []
        self.stats['totalPacketsAcked'] = []

        self.stats["bottleNeck"] = []
        self.stats['dataInQueue'] = []
        self.stats['packetsInQueue'] = []

    
    def getDeliveryRate(self):
        return self._deliveryRate
        
    def setSimulator(self, simulator):
        self.simulator = simulator

    def getName(self):
        return self.type.name + " #" + str(self.id)


    def createPacketIdFromNumber(self, packetNumber):
        return str(self.id) + "-" + str(packetNumber)

    def getNewPacketId(self):

        with self.lock:
            packetNumber = self.nextPacketNumber
            self.nextPacketNumber += 1
        
        return self.createPacketIdFromNumber(packetNumber)


    def getNewPacketIds(self, numberOfPackets):

        ids = []
        with self.lock:
            nextPacketNumber = self.nextPacketNumber
            self.nextPacketNumber += numberOfPackets
        
        for _ in range(numberOfPackets):
            ids.append(self.createPacketIdFromNumber(nextPacketNumber))
            nextPacketNumber += 1
        
        return ids


    def getDeliveryRateInMBits(self):
        return (self.getDeliveryRate() * (self.minPacketSize + self.maxPacketSize) / 2 ) / 131072

    
    
    
    def createPacket(self, size, sentAt):
        
        packetId = self.getNewPacketId()
        return Packet(packetId, self, path=self.path, size=size, sentAt=sentAt)
    
    def createPackets(self, numberOfPackets, sentAt):


        size = self.minPacketSize
        if self.minPacketSize < self.maxPacketSize:
            size = np.random.randint(self.minPacketSize, self.maxPacketSize)
        
        ids = self.getNewPacketIds(numberOfPackets)
        packets = []
        for id in ids:
            packets.append(Packet(id, self, path=self.path, size=size, sentAt=sentAt))
        return packets


    def createPacketsForTimeStep(self, timeStep):
        
        numberOfPackets = self.getNumberOfPacketsToCreateForTimeStep(timeStep)
        packets = self.createPackets(numberOfPackets, sentAt=timeStep)
        if len(packets) > 0:
            self.lastTimeStep = timeStep
        return packets


    # def createAndSendPacketsForTimeStep(self, timeStep, path: Path):
    #     packets = self.createPacketsForTimeStep(timeStep)

    #     if len(packets) == 0:
    #         return 0

    #     if self.debug:
    #         logging.info(f"Sender #{self.id} created and sent {len(packets)} packets at {timeStep}")

    #     if packets[-1].sentAt != timeStep:
    #         raise Exception(f"sentAt is not the same as current timeStep")

    #     self.sendTo(packets, path)
        
    #     return len(packets)


    # def sendTo(self, packets, path: Path):
    #     path.onIncomingPackets(packets)
    #     pass

    
    def finalizeStats(self):
        self.ackedPackets = collections.OrderedDict(sorted(self.ackedPackets.items()))

    
    @abstractmethod
    def onTimeStep(self, timeStep):
        """To be called at the beginning of a timeStep

        Args:
            timeStep ([type]): [description]
        """
        pass

    @abstractmethod
    def onTimeStepStart(self, timeStep):
        """To be called at the beginning of a timeStep

        Args:
            timeStep ([type]): [description]
        """
        pass

    @abstractmethod
    def onTimeStepEnd(self, timeStep):
        """To be called at the end of a timeStep

        Args:
            timeStep ([type]): [description]
        """
        pass

    def getOutStandingPackets(self):
        return None
    
    def onFinish(self):
        """To be called after simulation is finished
        """
        self.finalizeStats()
    
    @abstractmethod
    def getNumberOfPacketsToCreateForTimeStep(self, timeStep):
        pass


    @abstractmethod
    def onACK(self, packet, timeStep=None):
        packets = self.ackedPackets.get(timeStep, [])
        packets.append(packet)
        self.ackedPackets[timeStep] = packets
        # self.ackedPackets[packet.getPacketNumber()] = packet
        pass

    
    @abstractmethod
    def onStartUp(self, maxStep):
        self.resetStats()


    @abstractmethod
    def onShutDown(self, maxSteps):
        # calculate more stats
        self.totalPacketsAcked = 0
        prevRTT = 0
        for ts  in range(maxSteps):
            numPacketsInTS = len(self.ackedPackets.get(ts, []))
            self.stats['packetsAcked'].append(numPacketsInTS)
            self.totalPacketsAcked += numPacketsInTS
            self.stats['totalPacketsAcked'].append(self.totalPacketsAcked)

            # ttl values
            if numPacketsInTS > 0:
                prevRTT = self.getAvgRTTMS(self.ackedPackets[ts])
            self.stats['rttMS'].append(prevRTT)


        self.stats['actualRttMS'] = np.zeros_like(self.stats['rttMS'])
        
        for packets in self.ackedPackets.values():
            for packet in packets:
                self.stats['actualRttMS'][packet.sentAt] = TimeUtils.convertToMS(packet.ttl, self.timeResolutionUnit, round=False)
        
        for i in range(1, maxSteps):
            if self.stats['actualRttMS'][i] == 0:
                self.stats['actualRttMS'][i] = self.stats['actualRttMS'][i-1]
        pass


    def getAvgRTTMS(self, packets):
        ttl = 0
        for packet in packets:
            ttl += packet.ttl
        
        ttl = TimeUtils.convertToMS(ttl, self.timeResolutionUnit, round=False)
        return ttl / len(packets)
    
    def send(self, packets, timeStep):
        if self.debug:
            logging.debug(f"Client {self.id}: sending {len(packets)} packets to Node {self.nextNode.id}.")
        for packet in packets:
            self.nextNode.onIncomingPacket(packet, timeStep)

    # threading

    def lifeCycle(self):
        while self.forceStop is False:
            time.sleep(self.resolution / 1000)
            timeStep = TimeUtils.getMS()
            self.onTimeStep(timeStep)
            self.lastTimeStep = timeStep
        
        if self.debug:
            logging.debug(f"{self.thread.getName()}: stopped")
        pass


    def start(self):
        self.forceStop = False

        if self.thread is not None:
            if self.thread.is_alive() is False:
                self.thread.run()
        
        self.thread = threading.Thread(name="ThClient-"+str(self.id), target=self.lifeCycle, daemon=True)
        if self.debug:
            logging.debug(f"{self.thread.getName()}: starting")
        
        self.lastTimeStep = TimeUtils.getMS()
        self.thread.start()
        return self.thread
    

    def stop(self):
        if self.debug:
            logging.debug(f"{self.thread.getName()}: stop requested")
        self.forceStop = True
        pass

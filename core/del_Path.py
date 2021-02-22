from abc import ABC, abstractmethod
from model.PathType import PathType
import logging
import math

class Path(ABC):

    def __init__(self, pathType: PathType=PathType.SimpleQueue,
            maxDataInPipe=1000.0,
            avgTTL=20, noiseMax=20, debug=True):
        self.pathType = pathType
        self.maxDataInPipe = maxDataInPipe # in Kilo Bytes
        self.pipe = {} # holds received packets with ttl
        self.queue = None
        self.noiseMax = noiseMax # ms
        self.avgTTL = avgTTL # ms
        self.debug = debug

        self.dataInPipe = 0
    
    
    def isPipeFull(self):
        return self.dataInPipe >= self.maxDataInPipe

    def addToPipe(self, packet):
        if self.isPipeFull():
            return False
        existingPackets = self.pipe.get(packet.ackAt, [])
        existingPackets.append(packet)
        self.pipe[packet.ackAt] = existingPackets

        self.dataInPipe += packet.size / 1000
        return True
    

    
    def getNumPacketInPipe(self):
        s = 0
        for packets in self.pipe.values():
            s += len(packets)
        return s

    def getDataInPipeInKB(self):
        return round(self.dataInPipe, 2)


    def getPacketsByTimeStep(self, timeStep):
        """removes the packets

        Args:
            timeStep ([type]): [description]

        Returns:
            [type]: [description]
        """
        existingPackets = self.pipe.get(timeStep, [])
        self.pipe[timeStep] = [] # removing the packets

        if self.debug and len(existingPackets) > 0:
            logging.info(f"SimpleQueuePath: receiving {len(existingPackets)} packets at {timeStep}")

        # reduce data in flight
        for packet in existingPackets:
            self.dataInPipe -= packet.size / 1000

        return existingPackets

    def getPipeStats(self):
        stats = {}
        for timeStep in self.pipe:
            if len(self.pipe[timeStep]) > 0:
                stats[timeStep] = len(self.pipe[timeStep])
        return stats


    @abstractmethod
    def getDataInFlightInKB(self):
        raise NotImplementedError()


    @abstractmethod
    def getDataInQueueInKB(self):
        raise NotImplementedError()

    @abstractmethod
    def onIncomingPackets(self, packets):
        pass

    @abstractmethod
    def getACKs(self):
        pass
    
    @abstractmethod
    def onTimeStepEnd(self, timeStep):
        """To be called at the end of a timeStep

        Args:
            timeStep ([type]): [description]
        """
        pass


    @abstractmethod
    def onTimeStepStart(self, timeStep):
        """Must be called at the beginning of a timeStep

        Args:
            timeStep ([type]): [description]
        """
        pass


    @abstractmethod
    def getQueueSize(self):
        pass

    @abstractmethod
    def getNumPacketInflight(self):
        pass

    @abstractmethod
    def isOverflowed(self):
        pass
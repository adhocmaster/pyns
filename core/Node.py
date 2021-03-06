from abc import ABC, abstractmethod
from core.NodeType import NodeType
import logging
import math
import threading
import time
from library.TimeUtils import TimeUtils

class Node(ABC):

    def __init__(self, id, 
            nodeType: NodeType=NodeType.SimpleQueue,
            transmissionDelayPerByte = 0.0001,
            maxDataInPipe=1000.0,
            avgTTL=20, noiseMax=20, debug=True,
            timeResolutionUnit='ms', 
            resolution=1):
        self.id = id
        self.nodeType = nodeType
        self.transmissionDelayPerByte = transmissionDelayPerByte # in mili, fraction allowed. For 1 micro, set it to 0.001
        self.maxDataInPipe = maxDataInPipe # in Kilo Bytes
        self.pipe = {} # holds received packets with ttl
        self.queue = None
        self.noiseMax = noiseMax # ms
        self.avgTTL = avgTTL # ms
        self.debug = debug

        self.dataInPipe = 0
        self.thread = None
        self.resolution = resolution # miliseconds.
        self.forceStop = False
        self.timeResolutionUnit = timeResolutionUnit
        self.channelBusyUntil = 0 
    

    def __str__(self):

        return (
            f"\nid: {self.id}"
            f"\nnodeType: {self.nodeType}"
            f"\ntransmissionDelayPerByte: {self.transmissionDelayPerByte} ms"
            f"\nmaxDataInPipe: {self.maxDataInPipe} KB"
            f"\ntimeResolutionUnit: {self.timeResolutionUnit}"
            f"\ndebug: {self.debug}"
        )
    
    def isPipeFull(self):
        return self.dataInPipe >= self.maxDataInPipe

    def addToPipe(self, packet, leaveAt):
        if self.isPipeFull():
            return False
        existingPackets = self.pipe.get(leaveAt, [])
        existingPackets.append(packet)
        self.pipe[leaveAt] = existingPackets

        self.dataInPipe += packet.size / 1000
        return True
    

    
    def getNumPacketInPipe(self):
        s = 0
        for packets in self.pipe.values():
            s += len(packets)
        return s

    def getDataInPipeInKB(self):
        return round(self.dataInPipe, 2)


    def getPipePacketsByTimeStep(self, timeStep):
        """removes the packets in last 100 ms starting from timeStep

        Args:
            timeStep ([type]): [description]

        Returns:
            [type]: [description]
        """
        existingPackets = []

        for oldTimeStep in range(100):
            oldPackets = self.pipe.get(timeStep - oldTimeStep, [])
            self.pipe[timeStep - oldTimeStep] = [] # removing the packets

            # reduce data in flight
            for packet in oldPackets:
                self.dataInPipe -= packet.size / 1000
            
            existingPackets += oldPackets


        # if self.debug and len(existingPackets) > 0:
        #     logging.info(f"Node: flushing {len(existingPackets)} packets at {timeStep}")
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
    def getDataInQueueInBytes(self):
        raise NotImplementedError()

    @abstractmethod
    def getDataInQueueInKB(self):
        raise NotImplementedError()

    # @abstractmethod
    # def onIncomingPackets(self, packets):
    #     pass

    @abstractmethod
    def onIncomingPacket(self, packet, timeStep):
        pass

    # @abstractmethod
    # def getACKs(self):
    #     pass
    
    @abstractmethod
    def onTimeStep(self, timeStep):
        """To be called at the end of a timeStep

        Args:
            timeStep ([type]): [description]
        """
        pass

    
    # @abstractmethod
    # def onTimeStepEnd(self, timeStep):
    #     """To be called at the end of a timeStep

    #     Args:
    #         timeStep ([type]): [description]
    #     """
    #     pass


    # @abstractmethod
    # def onTimeStepStart(self, timeStep):
    #     """Must be called at the beginning of a timeStep

    #     Args:
    #         timeStep ([type]): [description]
    #     """
    #     pass


    @abstractmethod
    def getQueueSize(self):
        pass

    @abstractmethod
    def getNumPacketInflight(self):
        pass

    @abstractmethod
    def isOverflowed(self):
        pass

    # thread
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
                
        name = "ThNode-"+str(self.id)
        if self.nodeType == NodeType.Server:
            name = "ThServer-"+str(self.id)

        self.thread = threading.Thread(name=name, target=self.lifeCycle, daemon=True)
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

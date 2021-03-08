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

    def __init__(self, id, senderType: SenderType, deliveryRate = 0.1, debug=True,
    
            timeResolutionUnit='ms', 
            resolution=1):
        self.lock = threading.RLock()
        self.id = id
        self.nextPacketNumber = 1
        self.type = senderType
        self.deliveryRate = deliveryRate # KB per second
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
        self.stats = {}
        self.stats['packetsAcked'] = []

    
    def __str__(self):

        return (
        f" \n\tid: {self.id} \n"
        f"\ttype: {self.type} \n"
        f"\tdeliveryRate: {self.deliveryRate} \n"
        f"\tnextPacketNumber: {self.nextPacketNumber} \n"

        f"\tdebug: {self.debug} \n"
        )
        
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
        return (self.deliveryRate * (self.minPacketSize + self.maxPacketSize) / 2 ) / 131072

    
    
    
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
        # if self.debug:
        #     logging.info(f"Sender #{self.id} creating {numberOfPackets} packets at {timeStep}")
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
    def onShutDown(self, maxSteps):
        # calculate more stats
        for ts  in range(maxSteps):
            self.stats['packetsAcked'].append(len(self.ackedPackets.get(ts, [])))
        pass
    
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

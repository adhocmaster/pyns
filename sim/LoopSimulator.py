from sim.Simulator import Simulator
from model.Sender import Sender
from model.Path import Path
from model.SimpleQueuePath import SimpleQueuePath
from model.NoobSender import NoobSender
import pprint
import matplotlib.pyplot as plt
import seaborn as sns
import logging
logging.basicConfig(level=logging.INFO)

class LoopSimulator(Simulator):

    def __init__(self, path: Path, printStatFreq=10):

        super().__init__()

        self.senders = {}
        self.path = path
        self.nextSenderId = 1
        self.pp = pprint.PrettyPrinter()
        self.printStatFreq = printStatFreq # print every printStatFreq time step

    def createSenderId(self):
        senderId = self.nextSenderId
        self.nextSenderId += 1
        return senderId


    def validateEnv(self):
        if len(self.senders) is 0:
            raise Exception("No sender in the net")
        if self.path is None:
            raise Exception("No path in the net")

    def run(self, timeMS):

        self.validateEnv()

        self.stats['dataInFlight'] = []
        self.stats['dataInQueue'] = []
        self.stats['packetsInFlight'] = []
        self.stats['packetsInQueue'] = []
        self.stats['queueSize'] = []
        self.stats['packetsSent'] = []
        self.stats['packetsAcked'] = []
        self.stats['totalPacketsSent'] = []
        self.stats['totalPacketsAcked'] = []
        totalPacketsSent = 0
        totalPacketsAcked = 0

        for timeStep in range(1, timeMS + 1):
            if timeStep % self.printStatFreq == 0:
                logging.info(f"\n************Time step: {timeStep}*********")

            # 0. onTimeStep # any prep work
            self.path.onTimeStepStart(timeStep)
            for sender in self.senders.values():
                sender.onTimeStepStart(timeStep)

            # 1. receiveACKs
            ackPackets = self.path.getACKs()
            self.stats['packetsAcked'].append(len(ackPackets))
            totalPacketsAcked += len(ackPackets)
            self.stats['totalPacketsAcked'].append(totalPacketsAcked)
            
            for packet in ackPackets:
                packet.sender.onACK(packet)

            # 2. sendPackets
            for sender in self.senders.values():
                numPackets = sender.createAndSendPacketsForTimeStep(timeStep, self.path)
                self.stats['packetsSent'].append(numPackets)
                totalPacketsSent += numPackets
                self.stats['totalPacketsSent'].append(totalPacketsSent)

            # 3. gather timestep stats
            self.stats['packetsInFlight'].append(self.path.getNumPacketInflight())
            self.stats['dataInFlight'].append(self.path.getDataInFlightInKB())
            self.stats['packetsInQueue'].append(self.path.getQueueSize())
            self.stats['dataInQueue'].append(self.path.getDataInQueueInKB())

            # 4. print stats
            if timeStep % self.printStatFreq == 0:
                logging.info(f"Packets in-flight: {self.path.getNumPacketInflight()}")
                logging.info(f"Data in-flight: {self.path.getDataInFlightInKB()}KB")
                # logging.info(self.pp.pformat(self.path.getPipeStats()))
                logging.info(f"packetsInQueue: {self.path.getQueueSize()}")

            # 5. terminate early if path overflowed
            if self.path.isOverflowed():
                logging.warn("Path overflowed. Terminating....")
                break

            # 6. timeStep end. any clean up work
            self.path.onTimeStepEnd(timeStep)
            for sender in self.senders.values():
                sender.onTimeStepEnd(timeStep)

            pass

            

        for sender in self.senders.values():
            sender.onFinish()

        pass
    pass
            
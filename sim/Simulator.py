from abc import ABC


class Simulator(ABC):

    def __init__(self):
        self.stats = {}
        self.stats['dataInFlight'] = []
        self.stats['dataInQueue'] = []
        self.stats['packetsInFlight'] = []
        self.stats['packetsInQueue'] = []
        self.stats['queueSize'] = []
        self.stats['packetsSent'] = []
        self.stats['packetsAcked'] = []
        self.stats['totalPacketsSent'] = []
        self.stats['totalPacketsAcked'] = []
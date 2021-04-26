from core.Client import Client
from event.PacketEvent import PacketEvent
from event.EventTypes import EventTypes
from core.SenderType import SenderType
from library.TimeUtils import TimeUtils
import logging

class TCPClient(Client):


    def __init__(self, id, delay_between_packets, max_outstanding_packets, timeResolutionUnit, 
            startAt=0,
            debug=True):

        super().__init__(id, SenderType.TCP, deliveryRate=0, debug=debug, resolution=None, timeResolutionUnit=timeResolutionUnit, startAt=startAt)
        
        self.delay_between_packets = delay_between_packets # in the same resolution as the simulator
        self.max_outstanding_packets = max_outstanding_packets
        self.debug = debug
        self.path = None
        self.simulator = None
        self.outstanding_packets = 0
        self.lastTimeStep = 0

        self.stats['outStandingPackets'] = []
        self.name = f"TCPClient {self.id}"
    
    
    def __str__(self):

        pathStr = "" if self.path is None else self.path.__str__()
        return (
            f" \n\tid: {self.id}"
            f" \n\tdelay_between_packets: {self.delay_between_packets} {self.timeResolutionUnit}"
            f" \n\tmax_outstanding_packets: {self.max_outstanding_packets}"
            f" \n\tpath: {pathStr}"
            f" \n\tdebug: {self.debug}"
        )
    
    def setSimulator(self, simulator):
        self.simulator = simulator
        self.timeResolutionUnit = simulator.timeResolutionUnit

    def resetStats(self):
        super().resetStats()
        self.outstanding_packets = 0
        self.lastTimeStep = 0


    def getMaxDeliveryRatePerS(self):
        return self.delay_between_packets * TimeUtils.convertTime(1, 's', self.timeResolutionUnit)


    def onTimeStepStart(self, timeStep):
        raise NotImplementedError()

    def onTimeStepEnd(self, timeStep):
        raise NotImplementedError()

    
    def getNumberOfPacketsToCreateForTimeStep(self, timeStep):
        raise NotImplementedError()

    def createPacketsForTimeStep(self, timeStep):
        return [] # it creates it's own events.

    def getOutStandingPackets(self):
        return self.outstanding_packets
    

    def onACK(self, packet, timeStep=None):

        super().onACK(packet, timeStep)


        self.outstanding_packets -= 1
        if self.debug:
            logging.debug(f"{self.name}: outstanding packets: {self.outstanding_packets}")
        

        # self.ackedPackets[packet.getPacketNumber()] = packet
        # raise NotImplementedError()


    def onTimeStep(self, timeStep):
        # create events
        if self.outstanding_packets >= self.max_outstanding_packets:
            return
        if timeStep < self.startAt:
            return
        
        if (self.lastTimeStep + self.delay_between_packets) <= timeStep:
            # send a packet
            packet = self.createPacket(size=30, sentAt=timeStep)
            e = PacketEvent(EventTypes.ArriveNode, timeStep, packet)
            self.simulator.add_event(e)
            self.lastTimeStep = timeStep
            self.outstanding_packets += 1

            if self.debug:
                logging.debug(f"{self.name}: created packet with id {packet.id}")
                logging.debug(f"{self.name}: outstanding packets: {self.outstanding_packets}")
        
        # self.stats['outStandingPackets'] = self.outstanding_packets
        
            
    def onStartUp(self, maxSteps):
        super().onStartUp(maxSteps)

            
    def onShutDown(self, maxSteps):
        if self.debug:
            logging.info(f"{self.name}: shutting down")
        super().onShutDown(maxSteps)

        # total sent packets = outstanding + acked
        for ts  in range(maxSteps):
            self.stats['totalPacketsSent'].append(self.stats['totalPacketsAcked'][ts] + self.stats['outStandingPackets'][ts])
        if self.debug:
            logging.info(f"{self.name}: shut down")

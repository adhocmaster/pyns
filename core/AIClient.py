from core.Client import Client
from event.PacketEvent import PacketEvent
from event.EventTypes import EventTypes
from core.SenderType import SenderType
import logging

class AIClient(Client):


    def __init__(self, id, delay_between_packets, max_outstanding_packets, debug=True):

        super().__init__(id, SenderType.AI, deliveryRate=0, debug=debug, resolution=None, timeResolutionUnit=None)
        
        self.delay_between_packets = delay_between_packets # in the same resolution as the simulator
        self.max_outstanding_packets = max_outstanding_packets
        self.debug = debug
        self.path = None
        self.simulator = None
        self.outstanding_packets = 0
        self.lastTimeStep = 0

    
    
    def __str__(self):

        return (
            f" \n\tid: {self.id}"
            f" \n\tdelay_between_packets: {self.delay_between_packets} {self.simulator.timeResolutionUnit}"
            f" \n\tmax_outstanding_packets: {self.max_outstanding_packets}"
            f" \n\tpath: {self.path.__str()}"
            f" \n\tdebug: {self.debug}"
        )
    
    def setSimulator(self, simulator):
        self.simulator = simulator
        self.timeResolutionUnit = simulator.timeResolutionUnit



    def onTimeStepStart(self, timeStep):
        raise NotImplementedError()

    def onTimeStepEnd(self, timeStep):
        raise NotImplementedError()

    
    def getNumberOfPacketsToCreateForTimeStep(self, timeStep):
        raise NotImplementedError()

    def createPacketsForTimeStep(self, timeStep):
        pass


    def onACK(self, packet):


        self.outstanding_packets -= 1
        if self.debug:
            logging.debug(f"AIClient {self.id}: outstanding packets: {self.outstanding_packets}")
        # self.ackedPackets[packet.getPacketNumber()] = packet
        # raise NotImplementedError()


    def onTimeStep(self, timeStep):
        # create events
        if self.outstanding_packets >= self.max_outstanding_packets:
            return
        
        if (self.lastTimeStep + self.delay_between_packets) <= timeStep:
            # send a packet
            packet = self.createPacket(size=30, sentAt=timeStep)
            e = PacketEvent(EventTypes.ArriveNode, timeStep, packet)
            self.simulator.add_event(e)
            self.lastTimeStep = timeStep
            self.outstanding_packets += 1

            if self.debug:
                logging.debug(f"AIClient {self.id}: created packet with id {packet.id}")
                logging.debug(f"AIClient {self.id}: outstanding packets: {self.outstanding_packets}")
        
            
        


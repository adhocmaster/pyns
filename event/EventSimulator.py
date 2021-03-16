import heapq
import time
from library.TimeUtils import TimeUtils
from library.Configuration import Configuration
import logging
from event.PacketEventManager import PacketEventManager
import pprint
from sim.Simulator import Simulator
class EventSimulator(Simulator):

    def __init__(self, timeResolutionUnit, nodeManager, startTimeStep=0, future_events=None, debug=False, printStatFreq=1000):
        
        super().__init__()

        self.future_events = future_events or []
        self.timeResolutionUnit = timeResolutionUnit
        self.nodeManager = nodeManager
        self.name="EventSimulator"
        self.eventManager = PacketEventManager(timeResolutionUnit, debug=debug)
        self.clients = []
        self.pp = pprint.PrettyPrinter(indent=4)
        self.timeStep = startTimeStep
        self.printStatFreq = printStatFreq # print every printStatFreq time step
        self.debug = debug
        self.config = Configuration()
        

    def __str__(self):
        return (
            f"\n name: {self.name}"
            f"\n debug: {self.debug}"
            f"\n timeResolutionUnit: {self.timeResolutionUnit}"
        )
    
    def addClient(self, client):
        client.lastTimeStep = self.timeStep
        client.setSimulator(self)
        client.timeResolutionUnit = self.timeResolutionUnit
        self.clients.append(client)
        
        

    def add_event(self, e):
        """Adds an event e, maintaining the heap invariant."""
        heapq.heappush(self.future_events, e)
        if self.debug:
            self.logEvents()


    
    def pop_event(self):
        e = heapq.heappop(self.future_events)
        if self.debug:
            self.logEvents()
        return e

    def hasDueEvent(self, timeStep):
        return len(self.future_events) > 0 and self.future_events[0].time <= timeStep
    
    def getCurrentTime(self):
        if self.timeResolutionUnit == 'ms':
            return TimeUtils.getMS()
        if self.timeResolutionUnit == 'mcs':
            return TimeUtils.getMicroS()
        if self.timeResolutionUnit == 'ns':
            return time.time_ns()
        raise NotImplementedError()

    def convertTimeToSimulatorUnit(self, amount, originalUnit):
        if originalUnit == 's':
            if self.timeResolutionUnit == 'ms':
                return amount * 1000
            
            if self.timeResolutionUnit == 'mcs':
                return amount * 1000_000
            
            if self.timeResolutionUnit == 'ns':
                return amount * 1000_000_000

        if originalUnit == 'ms':
            if self.timeResolutionUnit == 'ms':
                return amount
            
            if self.timeResolutionUnit == 'mcs':
                return amount * 1000
            
            if self.timeResolutionUnit == 'ns':
                return amount * 1000_000
            
        raise NotImplementedError()

    def logEvents(self):
        if len(self.future_events) == 0:
            return
        eStr = []
        for e in self.future_events:
            eStr.append( f"{e.time}: {e.name.name} p#{e.packet.id}")
        logging.debug(f"{self.name}: {self.timeStep}: Events: " + self.pp.pformat(eStr))

        
    def run(self, maxSteps):

        # self.validateEnv()

        for node in self.nodeManager.getNodes():
            node.onStartUp(maxSteps)

        for client in self.clients:
            client.onStartUp(maxSteps)
        pass

        for timeStep in range(maxSteps):
            self.step()
            self.collectStatsForClients()

            # 4. print stats
            if timeStep % self.printStatFreq == 0:
                logging.info(f"{self.name}: *************************************************** TimeStep {timeStep} ***********************************************")
                self.logClientStats(timeStep)
                
                # for client in self.clients:
                #     print(client.path.getNodeStats())

            

        for client in self.clients:
            client.onShutDown(maxSteps)
        pass
        for node in self.nodeManager.getNodes():
            node.onShutDown(maxSteps, self.config)


    def logClientStats(self, timeStep):
        for client in self.clients:
            logging.info(f"Client {client.id}: Stats")
            logging.info(f"outStandingPackets: {client.stats['outStandingPackets'][timeStep]}")
            logging.info(f"bottleNeck: {client.stats['bottleNeck'][timeStep]}")
            logging.info(f"dataInFlight: {client.stats['dataInFlight'][timeStep]}KB")
            logging.info(f"dataInQueue {client.stats['dataInQueue'][timeStep]}KB")
            logging.info(f"packetsInFlight: {client.stats['packetsInFlight'][timeStep]}")
            logging.info(f"packetsInQueue: {client.stats['packetsInQueue'][timeStep]}")


    def collectStatsForClients(self):
        """Runs every timestep
        """
        for client in self.clients:
            bottleNeck = client.path.getFirstBottleNeck()
            if bottleNeck is not None:
                client.stats["bottleNeck"].append(bottleNeck.id)
                client.stats['dataInQueue'].append(bottleNeck.getDataInQueueInKB())
                client.stats['packetsInQueue'].append(bottleNeck.getQueueSize())
            else:
                client.stats["bottleNeck"].append(0)
                client.stats['dataInQueue'].append(0)
                client.stats['packetsInQueue'].append(0)


            # path stats
            client.stats['outStandingPackets'].append(client.getOutStandingPackets())
            client.stats['dataInFlight'].append(client.path.getDataInFlightInKB())
            client.stats['packetsInFlight'].append(client.path.getNumPacketInflight())

    def step(self):
        """Performs one step of the event simulator."""
        
        # timeStep = self.getCurrentTime()
        timeStep = self.timeStep

        for node in self.nodeManager.getNodes():
            node.onTimeStepStart(timeStep)


        while self.hasDueEvent(timeStep):
            e = self.pop_event()

            if self.debug:
                logging.debug(f"{self.name}: {timeStep}: raised event ({e.name}, {e.time}) with packet {e.packet.id} which is currently at {e.packet.curNodeIndex}th node")
            # Causes e to happen.
            # generated_events = e.do()
            generated_events = self.eventManager.processEvent(self, e.name, e.packet)

            if self.debug:
                logging.debug(f"{self.name}: {timeStep}: done event ({e.name}, {e.time}), which generated {len(generated_events)} new events")

            # And inserts the resulting events into the heap of future events.
            for ge in generated_events:
                self.add_event(ge)

        # 1. let clients create events first
        self.notifyClients(timeStep)
        self.createClientEvents(timeStep)

        for node in self.nodeManager.getNodes():
            node.onTimeStepEnd(timeStep)

        self.timeStep += 1



    def createClientEvents(self, timeStep):
        # 1. Clients need to be allowed to create events instead of creating packets. So, let the client schedule it's own packets.  outstanding packets.
        for client in self.clients:
            packets = client.createPacketsForTimeStep(timeStep)
            self.eventManager.initiatePacketEvents(self, timeStep, packets)
            # client.lastTimeStep = timeStep # client should update it whenever it has created some packets

            if self.debug and len(packets) > 0:
                logging.debug(f"{self.name}: {timeStep}: initiated {len(packets)} packets from client {client.id}")

    def notifyClients(self, timeStep):
        # 1. Clients need to be allowed to create events instead of creating packets. So, let the client schedule it's own packets.  outstanding packets.
        for client in self.clients:
            client.onTimeStep(timeStep)


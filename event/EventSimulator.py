import heapq
import time
from library.TimeUtils import TimeUtils
import logging
from event.PacketEventManager import PacketEventManager

class EventSimulator(object):

    def __init__(self, timeResolutionUnit, future_events=None, debug=False):
        
        self.future_events = future_events or []
        self.timeResolutionUnit = timeResolutionUnit
        self.name="EventSimulator"
        self.debug = debug
        self.eventManager = PacketEventManager(timeResolutionUnit, debug=debug)
        self.clients = []

    
    def addClient(self, client):
        client.lastTimeStep = TimeUtils.getMS()
        self.clients.append(client)
        

    def add_event(self, e):
        """Adds an event e, maintaining the heap invariant."""
        heapq.heappush(self.future_events, e)

    
    def getTimeStep(self):
        if self.timeResolutionUnit == 'ms':
            return TimeUtils.getMS()
        raise NotImplementedError()
        

    def step(self):
        """Performs one step of the event simulator."""
        # Gets the first event.
        # check the timing for the first event, if it's due, pop it
        # how about multiple?

        timeStep = self.getTimeStep()

        # # 1. let clients create events first
        # self.createClientEvents(timeStep)

        # # 2. now process events!
        # if len(self.future_events) == 0:
        #     return


        if len(self.future_events) > 0 and self.future_events[0].time <= timeStep:
            e = heapq.heappop(self.future_events)
            # Causes e to happen.
            # generated_events = e.do()
            generated_events = self.eventManager.processEvent(self, e.name, e.packet)

            if self.debug:
                logging.debug(f"{self.name}: {timeStep}: processed event ({e.name}, {e.time}), which generated {len(generated_events)} new events")

            # And inserts the resulting events into the heap of future events.
            for ge in generated_events:
                self.add_event(ge)

        # 1. let clients create events first
        self.createClientEvents(timeStep)



    def createClientEvents(self, timeStep):
        for client in self.clients:
            packets = client.createPacketsForTimeStep(timeStep)
            self.eventManager.initiatePacketEvents(self, timeStep, packets)
            client.lastTimeStep = timeStep

            if self.debug and len(packets) > 0:
                logging.debug(f"{self.name}: {timeStep}: initiated {len(packets)} packets from client {client.id}")

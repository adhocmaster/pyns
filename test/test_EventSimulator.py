import unittest
from event.EventSimulator import EventSimulator
from event.OnceEvent import OnceEvent
from library.TimeUtils import TimeUtils
import numpy as np
import logging

logging.basicConfig(level=logging.DEBUG)

class test_EventSimulator(unittest.TestCase):

    def test_testWithNoPayload(self):

        simulator = EventSimulator(timeResolutionUnit='ms', debug=True)

        timeStep = TimeUtils.getMS()
        simulator.add_event(OnceEvent(name="packet1", time=timeStep))

        timeStep = TimeUtils.getMS() + np.random.randint(1, 100)
        simulator.add_event(OnceEvent(name="packet2", time=timeStep))

        timeStep = TimeUtils.getMS()
        simulator.add_event(OnceEvent(name="packet3", time=timeStep))
        timeStep = TimeUtils.getMS()
        simulator.add_event(OnceEvent(name="packet4", time=timeStep))

        timeStep = TimeUtils.getMS() + np.random.randint(1, 100)
        simulator.add_event(OnceEvent(name="packet5", time=timeStep))
        timeStep = TimeUtils.getMS() + np.random.randint(1, 100)
        simulator.add_event(OnceEvent(name="packet6", time=timeStep))

        print(simulator.future_events)

        stopAt = timeStep + 150

        while TimeUtils.getMS() < stopAt:
            simulator.step()
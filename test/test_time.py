import unittest
import time, sys
from library.TimeUtils import TimeUtils
class test_Time(unittest.TestCase):

    def test_Nano(self):
        print(type(1))
        print(type(time.time_ns()))
        print(time.time_ns())
        print(time.time_ns() + 1)

        print(sys.maxsize)

        print(round(1.4, 0))
        print(round(1.5, 0))
        print(round(1.6, 0))
    

    def test_conversion(self):

        seconds = 10

        assert TimeUtils.convertTime(seconds, 's', 'ms') == seconds * 1000
        assert TimeUtils.convertTime(seconds, 's', 'mcs') == seconds * 1000_000

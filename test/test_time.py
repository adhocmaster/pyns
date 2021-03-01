import unittest
import time, sys
class test_Time(unittest.TestCase):

    def test_Nano(self):
        print(type(1))
        print(type(time.time_ns()))
        print(time.time_ns())
        print(time.time_ns() + 1)

        print(sys.maxsize)
import unittest

from core.ClientManager import ClientManager


class test_ClientManager(unittest.TestCase):

    def test_getDelayBetweenPacketsFromDeliveryRatePerS(self):

        timeResolutionUnit = 'mcs'
        clientManager = ClientManager(timeResolutionUnit)

        delay = clientManager.getDelayBetweenPacketsFromDeliveryRatePerS(1)
        assert delay == 1000_000
        delay = clientManager.getDelayBetweenPacketsFromDeliveryRatePerS(10)
        assert delay == 1000_00
        delay = clientManager.getDelayBetweenPacketsFromDeliveryRatePerS(100)
        assert delay == 1000_0
        delay = clientManager.getDelayBetweenPacketsFromDeliveryRatePerS(1000)
        assert delay == 1000
        delay = clientManager.getDelayBetweenPacketsFromDeliveryRatePerS(5000)
        assert delay == 200
        delay = clientManager.getDelayBetweenPacketsFromDeliveryRatePerS(1000000)
        assert delay == 1
        try:
            delay = clientManager.getDelayBetweenPacketsFromDeliveryRatePerS(1000001)
            assert False
        except:
            assert True

        
        timeResolutionUnit = 'ms'
        clientManager = ClientManager(timeResolutionUnit)
        delay = clientManager.getDelayBetweenPacketsFromDeliveryRatePerS(1)
        assert delay == 1000
        delay = clientManager.getDelayBetweenPacketsFromDeliveryRatePerS(10)
        assert delay == 100
        delay = clientManager.getDelayBetweenPacketsFromDeliveryRatePerS(100)
        assert delay == 10
        delay = clientManager.getDelayBetweenPacketsFromDeliveryRatePerS(1000)
        assert delay == 1

        try:
            delay = clientManager.getDelayBetweenPacketsFromDeliveryRatePerS(1001)
            assert False
        except:
            assert True

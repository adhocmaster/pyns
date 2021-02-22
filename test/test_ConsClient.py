import unittest
from core.ConstClient import ConstClient
import time, threading
import logging

logging.basicConfig(level=logging.DEBUG)

class test_ConstClient(unittest.TestCase):

    def test_Start(self):

        logging.info(threading.current_thread().getName())
        client = ConstClient(1, deliveryRate=1, debug=True)
        client.start()
        logging.info(threading.current_thread().getName())
        time.sleep(3)
        client.stop()
        logging.info(threading.current_thread().getName())
        time.sleep(1)


import unittest
from core.ConstClient import ConstClient
import time, threading
import logging

logging.basicConfig(level=logging.DEBUG)

def raise_err():
    n=1
    while n < 10:
        logging.info(n)
        time.sleep(1)
        n += 1
    pass

if __name__ == "__main__":
    
    # logging.info(threading.current_thread().getName())
    # client = ConstClient(1, deliveryRate=1, debug=True)
    # client.start()
    # logging.info(threading.current_thread().getName())
    # # time.sleep(1)
    # client.stop()
    # logging.info(threading.current_thread().getName())
    # # time.sleep(1)


    try:
        t = threading.Thread(target=raise_err, daemon=True)
        # t.setDaemon(True)
        t.start()
        time.sleep(5)
        logging.info('no exception')
    except:
        logging.info('caught exception')
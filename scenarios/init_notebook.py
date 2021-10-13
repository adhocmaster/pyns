import os, sys
currentFolder = os.path.abspath('')
try:
    sys.path.remove(str(currentFolder))
except ValueError: # Already removed
    pass

projectFolder = 'C:\\Users\\adhocmaster\\Documents\\GitHub\\pyns'
sys.path.append(str(projectFolder))
os.chdir(projectFolder)
print( f"current working dir{os.getcwd()}")

import time
import logging
import numpy as np
from core.NodeManager import NodeManager
from core.Network import Network
from core.ClientManager import ClientManager
from core.ConstClient import ConstClient
from core.Server import Server
from event.EventSimulator import EventSimulator
from library.TimeUtils import TimeUtils
from library.Configuration import Configuration
from sim.AnalyzerTools import AnalyzerTools

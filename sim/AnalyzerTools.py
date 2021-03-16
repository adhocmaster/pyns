import pandas as pd
from core.Packet import Packet
import numpy as np
import matplotlib.pyplot as plt

class AnalyzerTools:

    def createDfFromPackets(self, packets):
        
        packNums = []
        ttls = []
        ttlNoises = []
        sentAt = []
        ackAt = []
        isDropped = []

        for packNum in packets:
            packNums.append(packNum)
            packet = packets[packNum]
            ttls.append(packet.ttl)
            ttlNoises.append(packet.ttlNoise)
            sentAt.append(packet.sentAt)
            ackAt.append(packet.ackAt)
            isDropped.append(packet.isDropped)

        
        data = {
            'packNum': packNums,
            'ttl': ttls,
            'ttlNoise': ttlNoises,
            'sentAt': sentAt,
            'ackAt': ackAt,
            'isDropped': isDropped
        }
        
        return pd.DataFrame(data)

    
    def getAvgTTLPerTimeStep(self, dfPackets:pd.DataFrame):
        return dfPackets.groupby(['sentAt']).mean()

    
    def getSenderStatsPerTimeStep(self, dfPackets:pd.DataFrame, simulatorStats):
        """Stats for timeSteps in dfPackets only, it is discontinuous and have a lot of missing values.

        Args:
            dfPackets (pd.DataFrame): [description]
            simulatorStats ([type]): [description]

        Returns:
            [pandas.DataFrame]: index = sentAt, Columns - avgTTL	minTTL	maxTTL	dataInFlight	dataInQueue
        """

        ttlDf = dfPackets.groupby(['sentAt']).agg(
            avgTTL = pd.NamedAgg(column = "ttl", aggfunc="mean"),
            minTTL = pd.NamedAgg(column = "ttl", aggfunc="min"),
            maxTTL = pd.NamedAgg(column = "ttl", aggfunc="max"),
        )
        sentAtArray = ttlDf.index.array

        dataInFlight = []
        dataInQueue = []
        for timeStep in sentAtArray:
            dataInFlight.append(simulatorStats['dataInFlight'][timeStep])
            dataInQueue.append(simulatorStats['dataInQueue'][timeStep])

        ttlDf['dataInFlight'] = dataInFlight
        ttlDf['dataInQueue'] = dataInQueue

        return ttlDf


    def createPlotsAgainstDataInFlight(self, dfStats, figsize=(20,10)):
        plt.figure(figsize=figsize)
        plt.plot(dfStats['dataInFlight'], dfStats['avgTTL'], label="avg ttl")
        plt.plot(dfStats['dataInFlight'], dfStats['maxTTL'], label="max ttl")
        plt.plot(dfStats['dataInFlight'], dfStats['dataInQueue'], label="data In Queue")
        plt.title("Simulation stats")
        plt.xlabel("Data in flight KB")
        plt.ylabel("ttl in ms")
        plt.legend()
        plt.show()
    

    def createPlotForTimeSteps(self, statsDic, columnName, figsize=(20,10)):
        plt.figure(figsize=figsize)
        timeSteps = list(range(len(statsDic[columnName])))
        plt.plot(timeSteps, statsDic[columnName], label=columnName)
        plt.title(f"{columnName} stats")
        plt.xlabel("Time Step")
        plt.ylabel(f"{columnName}")
        plt.legend()
        plt.show()

    def createPlotsForTimeSteps(self, statsDic, columnNames, figsize=(20,10), title='Stats'):
        plt.figure(figsize=figsize)
        timeSteps = list(range(len(statsDic[columnNames[0]])))



        for columnName in columnNames:
            if len(timeSteps) != len(statsDic[columnName]):
                raise Exception("Not all the columns have same number of items")
            plt.plot(timeSteps, statsDic[columnName], label=columnName)

        plt.title(title)
        plt.xlabel("Time Step")
        plt.ylabel(f"values")
        plt.legend()
        plt.show()





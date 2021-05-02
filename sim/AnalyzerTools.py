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

    
    def createDFFromStats(self, stats):
        return pd.DataFrame.from_dict(stats)


    def createBinnedChart(self, nodes, columnNames, start=0, end=None):


        numberOfItems = len(nodes[0].binnedStats[columnNames[0]])
        x = np.arange(numberOfItems)
        width=0.1


        for col in columnNames:
            for node in nodes:
                plt.bar(x, node.binnedStats[col], width=width, label=f"{col}-{node.id}")
                x = x + width

        plt.legend(loc='best')
        plt.show()

    
    def createPacketVsRTT(self, client, figsize=(20,10), start=0, end=None, xlabel=None, ylabel=None):
        plt.figure(figsize=figsize)
        plt.rcParams['font.size'] = '14'
        # df = self.createDFFromStats(client.stats)
        df = pd.DataFrame( {
            'outStandingPackets': client.stats['outStandingPackets'],
            'rttMS': client.stats['rttMS'],
            'actualRttMS': client.stats['actualRttMS']
        })
        meanRTTs = df.groupby(['outStandingPackets']).max()


        plt.plot(meanRTTs.index.to_numpy(), meanRTTs['rttMS'], label='observed rttMS')
        plt.plot(meanRTTs.index.to_numpy(), meanRTTs['actualRttMS'], label='actual RttMS')
        plt.legend(loc='best')
        if xlabel is None:
            plt.xlabel("data in flight in # packets")
        else:
            plt.xlabel(xlabel)
        if ylabel is None:
            plt.ylabel("rtt in MS")
        else:
            plt.ylabel(ylabel)
        
        plt.show()


    def createBinnedChartForNodeVsClient(self, nodes, nodeCols, clients, clientCols, figsize=(20,10), start=0, end=None, xlabel=None, ylabel=None):

        nodeColors = ['purple', 'lawngreen', 'red', 'gold', 'slategrey', 'navy', 'yellow', 'aquamarine', 'skyblue',
                    'purple', 'lawngreen', 'red', 'gold', 'slategrey', 'navy', 'yellow', 'aquamarine', 'skyblue']
        endBefore = len(nodes[0].binnedStats[nodeCols[0]])

        if (end is not None) and (end <= endBefore):
            endBefore = end 


        plt.figure(figsize=figsize)
        plt.rcParams['font.size'] = '14'

        x = np.arange(endBefore-start)
        x += start
        width=0.1
        for col in nodeCols:
            nodeIndex = 0
            for node in nodes:
                # plt.bar(x, node.binnedStats[col][start: endBefore], width=width, label=f"{col}-{node.name}")
                plt.scatter(x, node.binnedStats[col][start: endBefore], color=nodeColors[nodeIndex], s=2, alpha=0.5, label=f"{col}-{node.name}")
                x = x + width
                nodeIndex += 1

        x = np.arange(endBefore-start)
        x += start
        for col in clientCols:
            for client in clients:
                plt.plot(x, client.binnedStats[col][start: endBefore], ':', label=f"{col}-{client.name}")

        plt.legend(loc='best')
        if xlabel is None:
            plt.xlabel("time")
        else:
            plt.xlabel(xlabel)
        if ylabel is not None:
            plt.ylabel(ylabel)

        plt.show()


    def binStats(self, nodes, columnNames, binSize=100, method=max):
        """Creates binnedStats property in nodes

        Args:
            nodes ([type]): [description]
        """

        # init summary properties
        for node in nodes:
            print(node)
            node.binnedStats = {}
            for col in columnNames:
                node.binnedStats[col] = []
            


        binStart = 0
        binEndBefore = binStart + binSize
        numberOfItems = len(nodes[0].stats[columnNames[0]])

        while binEndBefore <= numberOfItems:
            for col in columnNames:
                for node in nodes:
                    colData = node.stats[col]
                    data = colData[binStart : binEndBefore]
                    agg = list(map(method, (data,)))[0]
                    node.binnedStats[col].append(agg)
            
            binStart = binEndBefore
            binEndBefore += binSize
        
    
    # def summarizeClientStats(self, clients, columnNames, binSize=100, method=max):








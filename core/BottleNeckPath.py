from model.SimpleQueuePath import SimpleQueuePath
import logging, math
import numpy as np

class BottleNeckPath(SimpleQueuePath):
    
    def __init__(
                    self, 
                    maxArrivalRate,
                    maxDeliveryRate,
                    maxDataInPipe=10000,
                    maxQsize = 10000, 
                    avgTTL=20, noiseMax=20,
                    debug=True,
                ):
        super().__init__(maxDataInPipe=maxDataInPipe, maxQsize=maxQsize, avgTTL=20, noiseMax=20, debug=debug)

        if maxArrivalRate < 1:
            raise Exception("maxArrivalRate less than 1 is not supported")
        if maxDeliveryRate < 1:
            raise Exception("maxDeliveryRate less than 1 is not supported")

        if maxArrivalRate < maxDeliveryRate:
            logging.warning(f"path's maxArrivalRate is less than its maxDeliveryRate")

        self.maxArrivalRate = math.floor(maxArrivalRate) # in packets for simplification. None if no restriction
        self.maxDeliveryRate = math.floor(maxDeliveryRate) # in packets for simplification. None if no restriction
        self.incomingPacketsInCurrentTimeStep = []

        logging.info(f"Maximum data in pipe is around (maxDeliveryRate * avgPacketSize * avgTTL) = {(self.maxDeliveryRate * 30 * self.avgTTL) / 1000} KB" )
        logging.info(f"Maximum data in flight can be around (pipe-data + queue-data) = {(self.maxDeliveryRate * 30 * self.avgTTL + self.maxQsize * 30) / 1000} KB" )
        logging.info(f"Optimal data in flight = {(self.maxDeliveryRate * 30 * self.avgTTL) / 1000} KB" )
        pass

    def onTimeStepStart(self, timeStep):
        self.ackPackets = self.getPacketsByTimeStep(timeStep)
        # self.tryFlushQueue(timeStep) # assumes infinite delivery rate.
        

    
    def onIncomingPackets(self, packets):
        """ This method is called every time step for every sender seperately. So, we need to process the incoming packets at the end of the timeStep."""
        if self.debug:
            logging.info(f"BottleNeckPath: {len(packets)} incoming packets from sender {packets[0].sender.id}")
        
        self.incomingPacketsInCurrentTimeStep += packets
    
        pass

    
    def onTimeStepEnd(self, timeStep):
        """To be called at the end of a timeStep. No new ACK at this step.
        We need to process the queue first.

        Args:
            timeStep ([type]): [description]
        """

        # 1. check arrival overflow. drop if overflowed
        self.losePacketsOnArrival()
        # 2. check delivery overflow

        # 2.0 first deliver from queue self.deliverRate
        numDeliveredFromQueue = self.tryDeliveringFromQueue(timeStep, limit=self.maxDeliveryRate)

        # 2.1 try deliverying first self.deliverRate - numDeliveredFromQueue number of packets. push to queue if pipe full.
        numDeliveredFromIncomingPackets = self.tryDeliveringFromIncomingPackets(numDeliveredFromQueue)

        # 2.2 push rest of the packets to queue
        numIncomingPackets = len(self.incomingPacketsInCurrentTimeStep) 
        if numIncomingPackets > numDeliveredFromIncomingPackets:
            for i in range(numDeliveredFromIncomingPackets, numIncomingPackets):
                self.addToQueue(self.incomingPacketsInCurrentTimeStep[i])
            
            if self.debug:
                logging.info(f"BottleNeckPath: Pushing rest {numIncomingPackets - numDeliveredFromIncomingPackets} to queue  on onTimeStepEnd")

        # clear cache
        self.incomingPacketsInCurrentTimeStep = []
        pass


    def losePacketsOnArrival(self):
        if self.maxArrivalRate is not None:
            currentNumPackets = len(self.incomingPacketsInCurrentTimeStep) 
            if currentNumPackets > self.maxArrivalRate:
                selectedIndices = np.random.choice(range(currentNumPackets), self.maxArrivalRate, replace=False)
                selectedPackets = []
                for selectedIndex in selectedIndices:
                    selectedPackets.append(self.incomingPacketsInCurrentTimeStep[selectedIndex])
                self.incomingPacketsInCurrentTimeStep = selectedPackets
                if self.debug:
                    logging.info(f"BottleNeckPath: dropped {currentNumPackets - self.maxArrivalRate} on onTimeStepEnd")
        pass

    
    def tryDeliveringFromIncomingPackets(self, numberDeliveredFromQueue):
        numDelivered = numberDeliveredFromQueue
        for packet in self.incomingPacketsInCurrentTimeStep:
            if numDelivered >= self.maxDeliveryRate:
                break
            self.deliverOrEnqueuePacket(packet)
            numDelivered += 1
        
        numDeliveredFromIncomingPackets = numDelivered - numberDeliveredFromQueue
        if self.debug:
            logging.info(f"BottleNeckPath: deliverMaxPacketsOrEnqueueIfPipeFull {numDeliveredFromIncomingPackets} on onTimeStepEnd")
        
        return numDeliveredFromIncomingPackets





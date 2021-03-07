class AIClient:


    def __init__(self, id, delay_between_packets, max_outstanding_packets, path, debug=True):

        self.id = id
        self.delay_between_packets = delay_between_packets # in the same resolution as the simulator
        self.max_outstanding_packets = max_outstanding_packets
        self.path = path
        self.debug = debug
        self.simulator = None
        self.outstanding_packets = 0
        self.lastSentAt = 0

    
    
    def __str__(self):

        return (
            f" \n\tid: {self.id}"
            f" \n\tdelay_between_packets: {self.delay_between_packets} {self.simulator.timeResolutionUnit}"
            f" \n\tmax_outstanding_packets: {self.max_outstanding_packets}"
            f" \n\tpath: {self.path.__str()}"
            f" \n\tdebug: {self.debug}"
        )
    
    def setSimulator(self, simulator):
        self.simulator = simulator


    def onTimeStep(self, timeStep):
        # create events
        if self.outstanding_packets >= self.max_outstanding_packets:
            return
        
        if (self.lastSentAt + self.delay_between_packets) <= timeStep:
            # send a packet
            
        


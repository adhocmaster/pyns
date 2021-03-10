# PyNS
 A network simulator written in python with the goal of applying game theory and reinforcement learning in network congestion control. 
## Requirements
1. Python 3.7+
2. pyyaml (conda install -c anaconda pyyaml)


# Node

1. maxDeliveryRate: number of packets per second. It is used to calculate getTransmissionDelayMSFromDeliverRate in NodeManager. In packet manager, transmission delay is used to ensure delivery rate.


# client
1. deliveryRate: number of packets per second. It is also used to calculate 

# Event Simulator:

1. time to transmit: time to push bytes + 1 timeResolutionUnit. 1 is a transmission gap which keeps the system clean. Otherwise, there will be moments when a packet is about to leave, another will try to enter the channel.

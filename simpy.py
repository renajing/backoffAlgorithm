# This is a simpy based  simulation of a M/M/1 queue system
import random
import simpy
import math


#given global variables
RANDOM_SEED = 9 #randomly chosen kappa
SIM_TIME = 2500000 #changed to allow for higher chance of finding dropped pkts
MU = 1
#additional global variables
TOTALSLOTS = 0
TOTALSUCCESSES = 0
TOTALCOLLISIONS = 0
global_arrival_rate = 0.01

class Host:
    def __init__(self, env, rate ):
        self.numPkts = 0
        self.slotNum = 0
        self.N = 0
        self.arrival_rate = rate

    def packets_arrival(self,env):
        while(True):
            yield env.timeout(random.expovariate(self.arrival_rate)) 
            self.numPkts += 1
            arrival_time = env.now  
         

def calculateDelayedSlots(numCollisions):
    K = min(numCollisions,10) #exponential => K = min(numCollisions,10) ; linear => K = min(numCollisions, 1024)
    delayedSlots = random.randint(0,math.pow(2,K)) #exponential => random.randint(0,math.pow(2,K)) ; linear => random.randint(0,K)
    return delayedSlots


#Runs entire simulation
class Simulation:
    def __init__(self,env,hosts):
        self.env = env
        self.hosts = hosts

    def process_packet(self,env):
        global TOTALSLOTS 
        global TOTALSUCCESSES
        global TOTALCOLLISIONS
        while True:
            yield env.timeout(1)
        
            #Check if duplicates exist in all host's slotNumbers 
            duplicates = []
            totalNumPkts = 0

            for i in range(0,10):       
                if self.hosts[i].slotNum == TOTALSLOTS:
                    #print("trying to transmit at this slot")
                    duplicates.append(i) 
                          

            #Packet successfully transmits
            if len(duplicates) == 1:
                if self.hosts[duplicates[0]].numPkts > 0:               #if there are packets to send 
                    index = duplicates[0]
                    TOTALSUCCESSES += 1
                    self.hosts[index].numPkts -= 1
                    self.hosts[index].slotNum += 1 
                    self.hosts[index].N = 0
                else:
                    index = duplicates[0]
                    self.hosts[index].slotNum += 1


            #Collision, update slot to be transmitted at
            if len(duplicates) > 1:
                for i in range(0,len(duplicates)):
                    TOTALCOLLISIONS += 1
                    index = int(duplicates[i])   #index of host that collided
                    self.hosts[index].N += 1 
                    self.hosts[index].slotNum += calculateDelayedSlots( self.hosts[index].N ) + 1       

            TOTALSLOTS += 1 



def main():
    global TOTALSUCCESSES
    global TOTALCOLLISIONS
    global TOTALSLOTS

    random.seed(RANDOM_SEED)
    for arrival_rate in [global_arrival_rate]:
        env = simpy.Environment()

        #initialize all 10 Hosts with same parameters
        hosts = []
        for i in range(0,10):
            hosts.append(Host(env, arrival_rate))

        simulation = Simulation(env, hosts)

        for i in range(0,10):
            env.process(hosts[i].packets_arrival(env))
        env.process(simulation.process_packet(env))

        env.run(until=SIM_TIME)


        throughput = (float(TOTALSUCCESSES)/float(TOTALSLOTS)) 
        print("Throughput for lambda = ")
        print(arrival_rate)
        print("is")
        print(throughput)

if __name__ == '__main__': main()

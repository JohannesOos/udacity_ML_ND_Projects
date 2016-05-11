import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        # mapping the Q values via a list of list
        self.qTable = {}        
        #learnign rate 0 = constant and 1 = all forgotten
        self.learningRate = 0.5
        
        #the following variables are for evaluating only
        #Steps for evaluating ho wgood the algorithm is 
        self.timeStep = 0
        # for keeping track how long it took, just for evaluation
        self.timeStepList = []
        # for knowing the deadline of the trial just for evaluation
        self.FullDeadline = 0
        self.FullDeadlineList = []

        
    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        # below is just for keeping track of how long the trial took
        self.timeStepList.append(self.timeStep-1)
        self.FullDeadlineList.append(self.FullDeadline)
        self.timeStep = 0
        print self.timeStepList
        print self.FullDeadlineList



    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)
        # definition of threshold, when to update a parameter
        epsilon = 1.5
        # TODO: Update state
        #update timestep for evaluation
        self.timeStep +=1
        if self.timeStep ==1:
            self.FullDeadline = deadline
        #change input from dictionary to tuple
        inputsTuple = (inputs['light'], inputs['oncoming'], inputs['left'], inputs['right'])
        # define state
        state = (inputsTuple, self.next_waypoint)
        self.state = state

        # TODO: Select action according to your policy
       
        #create actions to choose from
        action_options = [None, 'forward', 'right', 'left']

        #assign action to the randomized action
        action = random.choice(action_options)
        # in case we have a reward > threshold in teh list for the state the randomized will be replaced
        if True:
            # check if the state is known and has a good result
            if state in self.qTable:
                #print 'is in there'
                threshold = epsilon
                for pair in self.qTable[state]:
                    if pair[1] >= threshold:
                        threshold = pair[1]
                        #update action to best known action
                        action = pair[0]

        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        if state in self.qTable:
            # definign a support variable
            testvar = 0
            for pair in self.qTable[state]:
                if pair[0] == action:
                    pair[1] = (1-self.learningRate) * pair[1] + self.learningRate * reward
                    #increase support var to show that update has happen
                    testvar+=1
            #if update has not happen, it means this action has not yet been performed
            if testvar <1:
                self.qTable[state].append([action, reward])
        #if state not in qTabel it needs to be added
        else:
            self.qTable[state] =[[action,reward]]
        #print self.qTable

        #print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    # JohannesOos: Original values are update_delay = 0.5 and deisply = True
    sim = Simulator(e, update_delay=0.000001, display= False)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False
    
    # JohannesOos: Origingal is sim.run(n_trials=100) but does nto allow to kee track
    sim.run(n_trials=100)  # run for a specified number of trials
    
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()

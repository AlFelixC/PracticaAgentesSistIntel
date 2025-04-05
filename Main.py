from LGymClient import agentLoop
from BaseAgent import BaseAgent
from GoalOrientedAgent import GoalOrientedAgent


agent = GoalOrientedAgent("1","Rambo")
agentLoop(agent,True)


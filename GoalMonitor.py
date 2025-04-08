import random
from States.AgentConsts import AgentConsts
import numpy as np

import sys

class GoalMonitor:
    GOAL_COMMAND_CENTER = 0
    GOAL_LIFE = 1
    GOAL_PLAYER = 2

    def __init__(self, problem, goals):
        self.goals = goals
        self.problem = problem
        self.lastTime = -1
        self.recalculate = False

        #Añadimos el nuevo id del goal actual
        self.currentGoalID = -1

        #Variables para forzar movimiento si se estanca
        self.lastPos = None
        self.lastPosTime = -1

        #Para validar metas de la vida
        self.lifeOnMap = True

    def ForceToRecalculate(self):
        self.recalculate = True

    #determina si necesitamos replanificar
    def NeedReplaning(self, perception, map, agent):
        currentTime = perception[AgentConsts.TIME]
        currentPosition = (perception[AgentConsts.AGENT_X], perception[AgentConsts.AGENT_Y])
        print("ENTRAMOS EN NEEDREPLANING")
        map = self.problem.map
        if self.recalculate:
            print("REPLANIFICAMOS DE MANERA FORZADA")
            self.lastTime = perception[AgentConsts.TIME]
            self.lastPos = currentPosition
            self.lastPosTime = currentTime
            return True
        #TODO REALIZADO: definida la estrategia de cuando queremos recalcular
        #puede ser , por ejemplo cada cierto tiempo o cuanod tenemos poca vida.

        if perception[AgentConsts.HEALTH] < 2 and self.currentGoalID != self.GOAL_LIFE:
            print("REPLANIFICAMOS POR FALTA DE VIDA")
            return True
        
        if self.currentGoalID == self.GOAL_PLAYER:
            print("HAY QUE REPLANIFICAR PARA SABER DONDE ESTA EL AGENTE")
            return True

        """
            if self.lastPos == currentPosition:
                if (currentTime - self.lastPosTime) > 5000:
                    print("AGENTE ESTANCADO, se forzara el movimiento")
                    self.ForceMove(agent, map)
                    self.lastPosTime = currentTime
            else:
                self.lastPos = currentPosition
                self.lastPosTime = currentTime
            
            self.lifeOnMap = (perception[AgentConsts.LIFE_X] != -1 and perception[AgentConsts.LIFE_Y] != -1)

        """ 
        
        if self.currentGoalID == self.GOAL_COMMAND_CENTER:
            print("A POR EL COMMAND OE")
            return True

        if self.currentGoalID != -1 and self.isGoalValid(self.goals[self.currentGoalID], map):
            print("NO REPLANIFICAMOS, la meta actual sigue siendo válida")
            return True
    
        print("REPLANIFICAMOS PORQUE EL GOAL NO ES VALIDO")
        return True
    
    #selecciona la meta mas adecuada al estado actual
    def SelectGoal(self, perception, map, agent):
        #TODO REALIZADO: definida la estrategia del cambio de meta
        map = self.problem.map

        lifeGot = (perception[AgentConsts.LIFE_X] != -1 and perception[AgentConsts.LIFE_Y] != -1)
        
        print(f"LIFEGOT SIGUE EN EL MAPA = {lifeGot}")

        goalsPriority = [
            (self.GOAL_LIFE, perception[AgentConsts.HEALTH] < 2 and lifeGot), #Cambiamos la prioridad para que vaya a por la vida (si esta muy baja)#####
            (self.GOAL_PLAYER, perception[AgentConsts.HEALTH] == 3), #Ir en busca del jugador si tenemos la salud alta #####or agent.plan is None
            (self.GOAL_COMMAND_CENTER, True) #Es el objetivo principal    #####True
            
        ]

        
        if self.currentGoalID != -1 and self.isGoalValid(self.goals[self.currentGoalID], map):
            print(f"META ACTUAL ES VALIDA: {self.currentGoalID}")

            if self.currentGoalID == self.GOAL_PLAYER:
                playerGoal = (perception[AgentConsts.AGENT_X], perception[AgentConsts.AGENT_Y])
                commandGoal = self.goals[self.GOAL_COMMAND_CENTER]

                distToCommand = abs(playerGoal[0] - commandGoal.x) + abs(playerGoal[1] - commandGoal.y)

                print(f"Distancia entre jugador y Command Center: {distToCommand}")

                if distToCommand <= 5:
                    print("Command Center está cerca del jugador. Cambiando objetivo.")
                    self.currentGoalID = self.GOAL_COMMAND_CENTER
                    return commandGoal
                
                return self.goals[self.currentGoalID]

        print("NO HAY UNA META ACTUAL VALIDA")
        #Buscamos la primera meta valida segun nuestras prioridades
        for goalId, condition in goalsPriority:
            goal = self.goals[goalId]
            print(f"GOAL: {goalId}, CONDITION: {condition}")
            if condition and self.isGoalValid(goal, map):
                self.currentGoalID = goalId
                print(f"ESCOJO EL GOAL: {goal}")
                return goal

        print("NO SE ENCONTRÓ NINGUNA META VÁLIDA")
        self.currentGoalID = -1

        #Es la meta que estaba anteriormente ###self.goals[self.currentGoalID]
        return None
    
    def UpdateGoals(self, goal, goalId):
        self.goals[goalId] = goal


    #NUEVOS METODOS AUXILIARES
    def isGoalValid(self, goal, map):

        map = self.problem.map
        x, y = goal.x, goal.y

        # Verificar si `map` es una lista de listas
        if not isinstance(map, (list, np.ndarray)):
            print("A")
            return False
        
        if isinstance(map, np.ndarray):
            if map.ndim != 2:
                print("B (numpy pero no 2D)")
                return False
        else:
            if not all(isinstance(row, list) for row in map):
                print("B (lista mal formada)")
                return False
            

        if self.currentGoalID == self.GOAL_LIFE:
            
            print(f"ENTRO AL IF DE VER SI SE EL GOAL DE VIDA ES EL ACTUAL Y EL VALOR DE LIFE ON MAP ES : {self.lifeOnMap}")
            if not getattr(self, 'lifeOnMap', True):
                print("EL OBJETIVO DE VIDA YA NO ES VALIDO PORQUE NO ESTA EN EL MAPA")
                return False

        #Acceder a la celda y verificar su valor
        try:
            cell_value = map[x][y]  #Se usa [x][y]
            print(f"Valor en map[{x}][{y}]: {cell_value}")
        except IndexError:
            print(f"Error: IndexError al acceder a map[{x}][{y}].")
            return False

        # Comprobar si la celda es transitable
        cost = self.problem.GetCost(cell_value)
        print("POR EL COSTE")

        if self.currentGoalID == self.GOAL_COMMAND_CENTER:
            print("EL GOAL ES EL COMMAND")
        elif self.currentGoalID == self.GOAL_PLAYER:
            print("EL GOAL ES EL JUGADOR")
        else:
            print("EL GOAL ES LA VIDA")

        print(f"GOAL VALID DEVUELVE {cost < sys.maxsize}")
        print(f"COSTE: {cost}")
        print(f"SYS: {sys.maxsize}")
        
            
        return cost < sys.maxsize
    

    def ForceMove(self, agent, map):
        directions = [(-1,0), (1,0), (0,-1), (0,1)]
        for dx, dy in directions:
            newX, newY = agent.x + dx, agent.y + dy
            if 0 <= newX < len(map) and 0 <= newY < len(map[0]):
                if map[newX][newY].value == AgentConsts.EMPTY:
                    agent.x, agent.y = newX, newY
                    print(f"Agente movido forzosamente a ({newX}, {newY})")
                    break

    
    def AgentHunt(self):
        if self.currentGoalID == self.GOAL_PLAYER:
            return True
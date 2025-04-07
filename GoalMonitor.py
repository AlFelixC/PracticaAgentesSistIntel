import random
from States.AgentConsts import AgentConsts

import sys

class GoalMonitor:
    GOAL_COMMAND_CENTRER = 0
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

    def ForceToRecalculate(self):
        self.recalculate = True

    #determina si necesitamos replanificar
    def NeedReplaning(self, perception, map, agent):
        currentTime = perception[AgentConsts.TIME]
        currentPosition = (perception[AgentConsts.AGENT_X], perception[AgentConsts.AGENT_Y])

        if self.recalculate:
            self.lastTime = perception[AgentConsts.TIME]
            self.lastPos = currentPosition
            self.lastPosTime = currentTime
            return True
        #TODO REALIZADO: definida la estrategia de cuando queremos recalcular
        #puede ser , por ejemplo cada cierto tiempo o cuanod tenemos poca vida.
        if perception[AgentConsts.HEALTH] < 2:
            return True
        
        if self.lastPos == currentPosition:
            if (currentTime - self.lastPosTime) > 5000:
                print("Agente ESTANCADO, se forzara el movimiento")
                self.ForceMove(agent, map)
                self.lastPosTime = currentTime
        else:
            self.lastPos = currentPosition
            self.lastPosTime = currentTime
        
        if not self.isGoalValid(self.goals[self.currentGoalID], map):
            return True
        
        return False
    
    #selecciona la meta mas adecuada al estado actual
    def SelectGoal(self, perception, map, agent):
        #TODO REALIZADO: definida la estrategia del cambio de meta
        lifeGot = (perception[AgentConsts.LIFE_X] != -1 and perception[AgentConsts.LIFE_Y] != -1)
        print(f"LIFEGOT SIGUE EN EL MAPA = {lifeGot}")

        goalsPriority = [
            (self.GOAL_LIFE, perception[AgentConsts.HEALTH] < 2 and lifeGot), #Cambiamos la prioridad para que vaya a por la vida (si esta muy baja)
            (self.GOAL_PLAYER, perception[AgentConsts.HEALTH] >= 2 or agent.plan is None) #Ir en busca del jugador si tenemos la salud alta
            (self.GOAL_COMMAND_CENTRER, True), #Es el objetivo principal    
        ]

        #Buscamos la primera meta valida segun nuestras prioridades
        for goalId, condition in goalsPriority:
            goal = self.goals[goalId]
            print(f"GOAL: {goalId}, CONDITION: {condition}")
            if condition and self.isGoalValid(goal, map):
                self.currentGoalID = goalId
                return goal

        #Es la meta establecida por defecto
        return self.goals[random.randint(0,len(self.goals) - 1)]
    
    def UpdateGoals(self, goal, goalId):
        self.goals[goalId] = goal


    #NUEVOS METODOS AUXILIARES
    def isGoalValid(self, goal, map):
        x, y = goal.x, goal.y

        # Verificar si `map` es una lista de listas
        if not isinstance(map, list):
            return False
        
        if not all(isinstance(row, list) for row in map):
            return False

        #Imprimir dimensiones esperadas y reales
        expected_x, expected_y = self.problem.xSize, self.problem.ySize
        actual_x, actual_y = len(map), len(map[0]) if len(map) > 0 else "undefined"
        print(f"Dimensiones esperadas: ({expected_x}, {expected_y})")
        print(f"Dimensiones reales: ({actual_x}, {actual_y})")

        if actual_x != expected_x or actual_y != expected_y:
            print("Error: Las dimensiones del mapa no coinciden con el problema.")
            return False

        #Verificar limites de `x` e `y`
        if not (0 <= x < expected_x and 0 <= y < expected_y):
            print(f"Error: Coordenadas fuera de rango -> x: {x}, y: {y}")
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
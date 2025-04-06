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

    def ForceToRecalculate(self):
        self.recalculate = True

    #determina si necesitamos replanificar
    def NeedReplaning(self, perception, map, agent):
        if self.recalculate:
            self.lastTime = perception[AgentConsts.TIME]
            return True
        #TODO REALIZADO: definida la estrategia de cuando queremos recalcular
        #puede ser , por ejemplo cada cierto tiempo o cuanod tenemos poca vida.
        if perception[AgentConsts.HEALTH] < 2:
            return True
        
        currentTime = perception[AgentConsts.TIME]
        if (currentTime - self.lastTime) > 5000: #5000 ms desde la ultima replanificacion (5 segundines)
            return True
        
        if not self.isGoalValid(self.goals[self.currentGoalID], map):
            return True
        
        return False
    
    #selecciona la meta mas adecuada al estado actual
    def SelectGoal(self, perception, map, agent):
        #TODO REALIZADO: definida la estrategia del cambio de meta
        goalsPriority = [
            (self.GOAL_LIFE, perception[AgentConsts.HEALTH] < 3), #Cambiamos la prioridad para que vaya a por la vida (si esta baja)
            (self.GOAL_COMMAND_CENTRER, True), #Es el objetivo principal
            (self.GOAL_PLAYER, perception[AgentConsts.HEALTH] >= 3) #Ir en busca del jugador si tenemos la salud alta
        ]

        #Buscamos la primera meta valida segun nuestras prioridades
        for goalId, condition in goalsPriority:
            goal = self.goals[goalId]
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
            print("Error: `map` no es una lista.")
            return False
        
        if not all(isinstance(row, list) for row in map):
            print("Error: `map` no es una lista de listas.")
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
            cell_value = map[x][y]  # 📌 Se usa [x][y]
            print(f"Valor en map[{x}][{y}]: {cell_value}")
        except IndexError:
            print(f"Error: IndexError al acceder a map[{x}][{y}].")
            return False

        # Comprobar si la celda es transitable
        cost = self.problem.GetCost(cell_value)
        return cost < sys.maxsize
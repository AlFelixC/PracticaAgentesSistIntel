from BaseAgent import BaseAgent
from StateMachine.StateMachine import StateMachine
from States.ExecutePlan import ExecutePlan
from GoalMonitor import GoalMonitor
from AStar.AStar import AStar
from MyProblem.BCNode import BCNode
from MyProblem.BCProblem import BCProblem
from States.AgentConsts import AgentConsts
from States.Attack import Attack
from States.RandomMovement import RandomMovement

#implementación de un agente básico basado en objetivos.
#disponemos de la clase GoalMonitor que nos monitorea y replanifica cad cierto tiempo
#o cuando se establezca una serie de condiciones.
class GoalOrientedAgent(BaseAgent):
    def __init__(self, id, name):
        super().__init__(id, name)
        dictionary = {
        "ExecutePlan" : ExecutePlan("ExecutePlan"),
        "Attack" : Attack("Attack"),
        "RandomMovement" : RandomMovement("RandomMovement")
        }
        
        self.stateMachine = StateMachine("GoalOrientedBehavior",dictionary,"ExecutePlan")
        self.problem = None
        self.aStar = None
        self.plan = None
        self.goalMonitor = None
        self.agentInit = False

    #Metodo que se llama al iniciar el agente. No devuelve nada y sirve para contruir el agente
    def Start(self):
        print("Inicio del agente ")
        self.stateMachine.Start(self)
        self.problem = None
        self.aStar = None
        self.plan = None
        self.goalMonitor = None
        self.agentInit = False

    #Metodo que se llama en cada actualización del agente, y se proporciona le vector de percepciones
    #Devuelve la acción u el disparo si o no
    def Update(self, perception, map):
        if perception == True or perception == False:
            return 0,True
        #inicializamos el agente (no lo podemos hacer en el start porque no tenemos el mapa)
        if not self.agentInit:
            self.InitAgent(perception,map)
            self.agentInit = True
 
        #le damos update a la máquina de estados.
        action, shot = self.stateMachine.Update(perception, map, self)

        #Actualizamos el plan refrescando la posición del player (meta 2)
        goal3Player = self._CreatePlayerGoal(perception)
        self.goalMonitor.UpdateGoals(goal3Player,2)
        if self.goalMonitor.NeedReplaning(perception,map,self):
            self.problem.InitMap(map) ## refrescamos el mapa
            self.plan=self._CreatePlan(perception, map)
        return action, shot
    
    #método interno que encapsula la creacion de un plan
    def _CreatePlan(self,perception,map):
        #TODO REALIZADO (Sujeto a posibles cambios)
        currentGoal = self.problem.GetGoal()
        print("Objetivo actual ", {currentGoal.value})

        if self.goalMonitor is not None:
            print("Entramos en if de GOALMONITOR y vemos si hay que replanificar")

            #Seleccionamos el objetivo actual segun la estrategia que llevemos
            if self.plan is None or self.goalMonitor.NeedReplaning(perception, map, self): 

                newGoal = self.goalMonitor.SelectGoal(perception, map, self)  
                print("CAMBIO de objetivo a ", {newGoal.value})
                

                #Creamos el nuevo plan para alcanzar el objetivo
                self.problem.SetGoal(newGoal)
                initialNode = self._CreateInitialNode(perception)
                self.problem.InitMap(map) #Actualizamos el mapa
                self.problem.initial = initialNode

                #Volvemos a inicializar el A* con el nuevo problema
                self.aStar = AStar(self.problem)
                print("Hemos inicializado el algoritmo A*")
                newPlan = self.aStar.GetPlan()

                #Ejecutar la busqueda A*
                if newPlan:
                    print(f"Nuevo plan creado con {len(newPlan)} pasos. El plan es", newPlan)
                    return newPlan
                else:
                    print("No se ha encontrado plan, por lo tanto mantenemos el actual")
                    return self.plan
            else:
                print("Mantenemos el plan actual, no necesitamos uno nuevo")
                return self.plan

            
        return self.plan
        
    @staticmethod
    def CreateNodeByPerception(perception, value, perceptionID_X, perceptionID_Y,ySize):
        xMap, yMap = BCProblem.WorldToMapCoord(perception[perceptionID_X],perception[perceptionID_Y],ySize)
        newNode = BCNode(None,BCProblem.GetCost(value),value,xMap,yMap)
        return newNode

    def _CreatePlayerGoal(self, perception):
        return GoalOrientedAgent.CreateNodeByPerception(perception,AgentConsts.PLAYER,AgentConsts.PLAYER_X,AgentConsts.PLAYER_Y,15)

    
    def _CreateLifeGoal(self, perception):
        return GoalOrientedAgent.CreateNodeByPerception(perception,AgentConsts.LIFE,AgentConsts.LIFE_X,AgentConsts.LIFE_Y,15)
    
    def _CreateInitialNode(self, perception):
        node = GoalOrientedAgent.CreateNodeByPerception(perception,AgentConsts.NOTHING,AgentConsts.AGENT_X,AgentConsts.AGENT_Y,15)
        node.SetG(0)
        return node
    
    def _CreateDefaultGoal(self, perception):
        return GoalOrientedAgent.CreateNodeByPerception(perception,AgentConsts.COMMAND_CENTER,AgentConsts.COMMAND_CENTER_X,AgentConsts.COMMAND_CENTER_Y,15)
    
    #No podemos iniciarlo en el start porque no conocemos el mapa ni las posiciones de los objetos
    def InitAgent(self,perception,map):
        #TODO REALIZADOS
        initialNode = self._CreateInitialNode(perception)

        #Estos son los distintos objetivos del Agente
        goal1CommanCenter = self._CreateDefaultGoal(perception)
        goal2Life = self._CreateLifeGoal(perception)
        goal3Player = self._CreatePlayerGoal(perception)

        #Inicializamos el problema y A*
        mapLength = len(map)
        ySize = AgentConsts.MAP_YSIZE
        xSize = mapLength // ySize
        
        #Creamos el problema a resolver
        self.problem = BCProblem(initialNode, goal1CommanCenter, xSize, ySize)

        #Vamos a crear el Goal Monitor para saber si cumplimos los objetivos
        self.goalMonitor = GoalMonitor(self.problem,[goal1CommanCenter,goal2Life,goal3Player])
        
        #Y su algoritmo de estrella correspondiente
        self.aStar = AStar(self.problem)
        self.aStar.heuristic = self.problem.Heuristic(initialNode)
        self.plan = self._CreatePlan(perception,map)

       
    #muestra un plan por consola
    @staticmethod
    def ShowPlan(plan):
        for n in plan:
            print("X: ",n.x,"Y:",n.y,"[",n.value,"]{",n.G(),"} => ")

    def GetPlan(self):
        return self.plan
    
    #Metodo que se llama al finalizar el agente, se pasa el estado de terminacion
    def End(self, win):
        super().End(win)
        self.stateMachine.End()
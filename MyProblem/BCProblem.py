#import sys
#sys.path.insert(1, '../AStar')
from AStar.Problem import Problem
from MyProblem.BCNode import BCNode
from States.AgentConsts import AgentConsts
import sys
import numpy as np

#Clase que implementa el problema especifico que queremos resolver y que hereda de la calse
#Problema genérico.
class BCProblem(Problem):
    

    def __init__(self, initial, goal, xSize, ySize):
        super().__init__(initial, goal)
        self.map = np.zeros((xSize,ySize),dtype=int)
        self.xSize = xSize
        self.ySize = ySize
    
    #inicializa un mapa con el mapa proveniente del entorno Vector => Matriz
    def InitMap(self,m):
        for i in range(len(m)):
            x,y = BCProblem.Vector2MatrixCoord(i,self.xSize,self.ySize)
            self.map[x][y] = m[i]

    #Muestra el mapa por consola
    def ShowMap(self):
        for j in range(self.ySize):
            s = ""
            for i in range(self.xSize):
                s += ("[" + str(i) + "," + str(j) + "," + str(self.map[i][j]) +"]")
            print(s)

    #Calcula la heuristica del nodo en base al problema planteado (Se necesita reimplementar)
    def Heuristic(self, node):
        #TODO REALIZADO heurística del nodo
        goal = self.GetGoal()
        resul = abs(node.x - goal.x) + abs(node.y - goal.y)

        #Adicion por obstaculo encontrado
        if node.value == AgentConsts.BRICK or node.value == AgentConsts.UNBREAKABLE:
            resul += 2

        return resul

    #Genera la lista de sucesores del nodo (Se necesita reimplementar)
    def GetSuccessors(self, node):
        successors = []
        movements = [
            (AgentConsts.MOVE_UP, (0, -1)),
            (AgentConsts.MOVE_DOWN, (0, 1)),
            (AgentConsts.MOVE_LEFT, (-1, 0)),
            (AgentConsts.MOVE_RIGHT, (1, 0))
        ]
        
        for action, (dx, dy) in movements:
            new_x = node.x + dx
            new_y = node.y + dy
            
            if self.IsValidMove(new_x, new_y):
                new_value = self.GetCellValue(new_x, new_y)
                cost = 1  # Costo base por movimiento
                
                # Ajustar costo según el tipo de celda
                if new_value == AgentConsts.BRICK:
                    cost += 2  # Mayor costo para atravesar ladrillos
                
                new_node = BCNode(
                    parent=node,
                    g=node.g + cost,
                    value=new_value,
                    x=new_x,
                    y=new_y
                )
                
                # Priorizar power-ups sin alterar el costo real
                if new_value == AgentConsts.HEALTH:
                    new_node.priority = -1  # Prioridad alta (menor número)
                else:
                    new_node.priority = 0  # Prioridad normal
                
                successors.append(new_node)
        
        # Ordenar sucesores por prioridad
        successors.sort(key=lambda x: x.priority)
        
        return successors
    
    #métodos estáticos
    #nos dice si podemos movernos hacia una casilla, se debe poner el valor de la casilla como
    #parámetro
    @staticmethod
    def CanMove(value):
        return value != AgentConsts.UNBREAKABLE and value != AgentConsts.SEMI_UNBREKABLE and value != AgentConsts.SEMI_UNBREKABLE
    
    #convierte coordenadas mapa en formato vector a matriz
    @staticmethod
    def Vector2MatrixCoord(pos,xSize,ySize):
        x = pos % xSize
        y = pos // ySize #division entera
        return x,y

    #convierte coordenadas mapa en formato matriz a vector
    @staticmethod
    def Matrix2VectorCoord(x,y,xSize):
        return y * xSize + x
    
    #convierte coordenadas del mapa en coordenadas del entorno (World) (nótese que la Y está invertida)
    @staticmethod
    def MapToWorldCoord(x,y,ySize):
        xW = x * 2
        yW = (ySize - y - 1) * 2
        return xW, yW

    #convierte coordenadas del entorno (World) en coordenadas mapa (nótese que la Y está invertida)
    @staticmethod
    def WorldToMapCoord(xW,yW,ySize):
        x = xW // 2
        y = yW // 2
        y = ySize - y - 1
        return x, y
    
    #versión real del método anterior, que nos ayuda a buscar los centros de las celdas.
    #aqui nos dirá los decimales, es decir como de cerca estamos de la esquina superior derecha
    #un valor de 1.9,1.9 nos dice que estamos en la casilla 1,1 muy cerca de la 2,2
    #en realidad, lo que buscamos es el punto medio de la casilla, es decir la 1.5, 1.5 en el caso
    #de la casilla 1,1
    @staticmethod
    def WorldToMapCoordFloat(xW,yW,ySize):
        x = xW / 2
        invY = (ySize*2) - yW
        invY = invY / 2
        return x, invY

    #se utiliza para calcular el coste de cada elemento del mapa 
    @staticmethod
    def GetCost(value):
        #TODO: debes darle un coste a cada tipo de casilla del mapa.
        return sys.maxsize
    
    #crea un nodo y lo añade a successors (lista) con el padre indicado y la posición x,y en coordenadas mapa 
    def CreateNode(self,successors,parent,x,y):
        value=self.map[x][y]
        g=BCProblem.GetCost(value)
        rightNode = BCNode(parent,g,value,x,y)
        rightNode.SetH(self.Heuristic(rightNode))
        successors.append(rightNode)

    #Calcula el coste de ir del nodo from al nodo to (Se necesita reimplementar)
    def GetGCost(self, nodeTo):
        return BCProblem.GetCost(nodeTo.value)
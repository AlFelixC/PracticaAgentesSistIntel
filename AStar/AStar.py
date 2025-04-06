#Algoritmo A* genérico que resuelve cualquier problema descrito usando la plantilla de la
#la calse Problem que tenga como nodos hijos de la clase Node
class AStar:

    def __init__(self, problem):
        self.open = [] # lista de abiertos o frontera de exploración
        self.precessed = set() # set, conjunto de cerrados (más eficiente que una lista)
        self.problem = problem #problema a resolver

    def GetPlan(self):
        findGoal = False
        self.open.clear()
        self.precessed.clear()
        self.open.append(self.problem.Initial())
        path = []
        
        while not findGoal and self.open:
            # Seleccionar nodo con menor coste F
            current = min(self.open, key=lambda n: n.F())
            self.open.remove(current)
            self.precessed.add(current)
            
            # Verificar si es la meta
            if self.problem.IsASolution(current):
                print("Encontramos la meta: ", current)
                findGoal = True
                path = self.ReconstructPath(current)
                break

            # Generar y procesar sucesores
            for successor in self.problem.GetSucessors(current):
                new_g = current.G() + self.problem.GetGCost(successor)
                
                #Si ya esta procesado, saltar
                if any(successor == n for n in self.precessed):
                    continue
                    
                #Buscar en Open si el sucesor ya esta
                in_open = next((n for n in self.open if successor == n), None)
                
                if in_open:
                    # Actualizar si encontramos mejor camino
                    if new_g < in_open.G():
                        self._ConfigureNode(in_open, current, new_g)
                else:
                    # Configurar y añadir nuevo nodo
                    self._ConfigureNode(successor, current, new_g)
                    self.open.append(successor)

        return path if findGoal else []

    #nos permite configurar un nodo (node) con el padre y la nueva G
    def _ConfigureNode(self, node, parent, newG):
        #TODO REALIZADO
        node.SetParent(parent)
        node.SetG(newG)
        #Establecemos la heuristica del nodo
        node.SetH(self.problem.Heuristic(node))

    #nos dice si un sucesor está en abierta. Si esta es que ya ha sido expandido y tendrá un coste, comprobar que le nuevo camino no es más eficiente
    #En caso de serlos, _ConfigureNode para setearle el nuevo padre y el nuevo G, asi como su heurística
    def GetSucesorInOpen(self,sucesor):
        i = 0
        found = None
        while found == None and i < len(self.open):
            node = self.open[i]
            i += 1
            if node == sucesor:
                found = node
        return found


    #reconstruye el path desde la meta encontrada.
    def ReconstructPath(self, goal):
        #TODO REALIZADO
        #Reconstruimos el camino desde el nodo objetivo hasta el nodo inicial
        path = []
        current = goal

        while current is not None:  #Mientras no lleguemos al nodo inicial (padre=None)
            path.append(current)
            current = current.GetParent()

        return path[::-1]  #Invertimos el camino para devolverlo en orden correcto




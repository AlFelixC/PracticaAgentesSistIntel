

#Algoritmo A* genérico que resuelve cualquier problema descrito usando la plantilla de la
#la calse Problem que tenga como nodos hijos de la clase Node
class AStar:

    def __init__(self, problem):
        self.open = [] # lista de abiertos o frontera de exploración
        self.precessed = set() # set, conjunto de cerrados (más eficiente que una lista)
        self.problem = problem #problema a resolver

    def GetPlan(self):
        """
        findGoal = False
        #TODO implementar el algoritmo A*
        #cosas a tener en cuenta:
        #Si el número de sucesores es 0 es que el algoritmo no ha encontrado una solución, devolvemos el path vacio []
        #Hay que invertir el path para darlo en el orden correcto al devolverlo (path[::-1])
        #GetSucesorInOpen(sucesor) nos devolverá None si no lo encuentra, si lo encuentra
        #es que ese sucesor ya está en la frontera de exploración, DEBEMOS MIRAR SI EL NUEVO COSTE ES MENOR QUE EL QUE TENIA ALMACENADO
        #SI esto es asi, hay que cambiarle el padre y setearle el nuevo coste.
        self.open.clear()
        self.precessed.clear()
        self.open.append(self.problem.Initial())
        path = []
        #mientras no encontremos la meta y haya elementos en open....
        #TODO implementar el bucle de búsqueda del algoritmo A*
        return path"""

        findGoal = False
        self.open.clear()
        self.precessed.clear()
        self.open.append(self.problem.Initial())  #Metemos el nodo inicial en la lista open
        path = []

        #Mientras no encontremos la meta y haya elementos en open...
        while not findGoal and len(self.open) > 0:
            #Ordenamos open por el valor F (G + H) del nodo (menor primero)
            self.open.sort(key=lambda node: node.F())
            
            #Extraemos el nodo con menor F (el primero en la lista)
            current = self.open.pop(0)

            #Metemos el nodo actual al MAPA close
            self.precessed.add(current)

            #Comprobamos si hemos alcanzado el objetivo
            if self.problem.IsGoal(current):
                findGoal = True
                path = self.ReconstructPath(current)  #Reconstruimos el path

            else:
                #Expandimos los sucesores del nodo actual
                successors = self.problem.GetSuccessors(current)

                if len(successors) == 0:
                    #Si no existen sucesores, no existe una solucion apartir de aqui
                    #Devolvemos el path vacio
                    continue

                for successor in successors:
                    if successor in self.precessed:
                        continue  #Ignoramos nodos ya procesados

                    successorInOpen = self.GetSucesorInOpen(successor)
                    newG = current.G() + self.problem.Cost(current, successor)

                    if successorInOpen is None:
                        #Si no esta en open, lo configuramos y lo metemos en open
                        self._ConfigureNode(successor, current, newG)
                        self.open.append(successor)
                    else:
                        # Si ya esta en open, comprobamos si el nuevo camino es mas eficiente
                        if newG < successorInOpen.G():
                            self._ConfigureNode(successorInOpen, current, newG)

        return path

    #nos permite configurar un nodo (node) con el padre y la nueva G
    def _ConfigureNode(self, node, parent, newG):
        #TODO REALIZADO
        node.SetParent(parent)
        node.SetG(newG)
        # Seteamos la heurística usando el método del problema.
        node.SetH(self.problem.Heuristic(node))

    #nos dice si un sucesor está en abierta. Si esta es que ya ha sido expandido y tendrá un coste, comprobar que le nuevo camino no es más eficiente
    #En caso de serlos, _ConfigureNode para setearle el nuevo padre y el nuevo G, asi como su heurística
    def GetSucesorInOpen(self,sucesor):
        i = 0
        found = None
        while found == None and i < len(self.open):
            node = self.open[i]
            i += 1
            if node.IsEqual(sucesor):
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




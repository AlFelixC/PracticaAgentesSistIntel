from AStar.Node import Node
#Creamos una clase hija como se nos pide en Node.py
class SibNode(Node):
    def __init__(self, parent, g, state):
        super().__init__(parent, g)
        self.state = state  #Estado especifico del nodo
    
    def __eq__(self, node):
        #Verificar si el nodo comparado es del mismo tipo
        if not isinstance(node, SibNode):
            return False
        #Comparar el estado almacenado en ambos nodos
        return self.state == node.state

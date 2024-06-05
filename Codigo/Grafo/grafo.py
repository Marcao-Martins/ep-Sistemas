import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Agora você pode importar o peer.py
from Grafo.nodo import Nodo

class Grafo:
    def __init__(self):
        self.nodos = {}

    def adiciona_nodo(self, endereco, porta):
        identificador = f"{endereco}:{porta}"
        if identificador not in self.nodos:
            self.nodos[identificador] = Nodo(endereco, porta)

    def adiciona_aresta(self, endereco1, porta1, endereco2, porta2):
        identificador1 = f"{endereco1}:{porta1}"
        identificador2 = f"{endereco2}:{porta2}"
        if identificador1 in self.nodos and identificador2 in self.nodos:
            self.nodos[identificador1].adicionar_vizinho(identificador2)
            self.nodos[identificador2].adicionar_vizinho(identificador1)
        else:
            print(f"Erro ao adicionar aresta: um ou ambos os nodos {identificador1}, {identificador2} não existem.")

    def __str__(self):
        return '\n'.join([str(nodo) for nodo in self.nodos.values()])
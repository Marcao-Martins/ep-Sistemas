import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Grafo.grafo import Grafo

class Testes:
    def __init__(self, pasta_de_arquivos):
        self.grafo = Grafo()
        self.pasta_de_arquivos = pasta_de_arquivos

    def carregar_arquivos(self):
        """Carrega todos os arquivos na pasta especificada e adiciona nodos e arestas ao grafo."""
        # Primeiro, adiciona todos os nodos
        for arquivo in os.listdir(self.pasta_de_arquivos):
            if arquivo.endswith(".txt") and arquivo != "topologia.txt":
                numero_do_nodo = arquivo.split('.')[0]  # Assume que o nome do arquivo é o número do nodo
                endereco_nodo = "127.0.0.1"
                porta_nodo = f"500{numero_do_nodo}"
                self.grafo.adiciona_nodo(endereco_nodo, porta_nodo)

        # Em seguida, adiciona todas as arestas
        for arquivo in os.listdir(self.pasta_de_arquivos):
            if arquivo.endswith(".txt") and arquivo != "topologia.txt":
                numero_do_nodo = arquivo.split('.')[0]  # Assume que o nome do arquivo é o número do nodo
                endereco_nodo = "127.0.0.1"
                porta_nodo = f"500{numero_do_nodo}"
                identificador_nodo = f"{endereco_nodo}:{porta_nodo}"

                caminho_completo = os.path.join(self.pasta_de_arquivos, arquivo)
                with open(caminho_completo, 'r') as file:
                    for linha in file:
                        endereco, porta = linha.strip().split(':')
                        self.grafo.adiciona_aresta(endereco_nodo, porta_nodo, endereco, porta)

    def mostrar_grafo(self):
        """Imprime a representação do grafo."""
        print(self.grafo)

# Uso da classe Testes
testes = Testes(r"E:\ep-Sistemas\arquivos\topologia_arvore_binaria")
testes.carregar_arquivos()
testes.mostrar_grafo()

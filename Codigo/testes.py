import os
from Grafo.grafo import Grafo

class Testes:
    def __init__(self, pasta_de_arquivos):
        self.grafo = Grafo()
        self.pasta_de_arquivos = pasta_de_arquivos
        self.prefixo_ip = "127.0.0.1:500"  # Prefixo comum para todos os nodos

    def carregar_arquivos(self):
        """Carrega todos os arquivos na pasta especificada e adiciona nodos e arestas ao grafo."""
        for arquivo in os.listdir(self.pasta_de_arquivos):
            if arquivo.endswith(".txt") and arquivo != "topologia.txt":
                numero_do_nodo = arquivo.split('.')[0]  # Assume que o nome do arquivo é o número do nodo
                endereco_nodo = "127.0.0.1"
                porta_nodo = f"500{numero_do_nodo}"
                identificador_nodo = f"{endereco_nodo}:{porta_nodo}"
                self.grafo.adiciona_nodo(endereco_nodo, porta_nodo)

                # Adicionar arestas
                caminho_completo = os.path.join(self.pasta_de_arquivos, arquivo)
                with open(caminho_completo, 'r') as file:
                    for linha in file:
                        endereco, porta = linha.strip().split(':')
                        self.grafo.adiciona_aresta(endereco_nodo, porta_nodo, endereco, porta)

    def mostrar_grafo(self):
        """Imprime a representação do grafo."""
        print(self.grafo)

# Uso da classe Testes
testes = Testes(r"E:\EP Sistemas Distribuidos\arquivos\topologia_arvore_binaria")
testes.carregar_arquivos()
testes.mostrar_grafo()

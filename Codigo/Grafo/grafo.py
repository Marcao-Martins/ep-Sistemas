from .nodo import Nodo
class Grafo:
    def __init__(self):
        self.nodos = {}  # Dicionário para armazenar os nodos pelo identificador

    # Adicionar parte de fazer a conexão entre os nodos aqui 
    def adiciona_nodo(self, endereco, porta):
        """Adiciona um novo nodo ao grafo se ele ainda não existir."""
        identificador = f"{endereco}:{porta}"
        if identificador not in self.nodos:
            self.nodos[identificador] = Nodo(endereco, porta)
            return self.nodos[identificador]
        return None

    def adiciona_aresta(self, endereco1, porta1, endereco2, porta2):
        """Adiciona uma conexão bidirecional entre dois nodos usando endereço e porta."""
        identificador1 = f"{endereco1}:{porta1}"
        identificador2 = f"{endereco2}:{porta2}"
        if identificador1 in self.nodos and identificador2 in self.nodos:
            self.nodos[identificador1].adiciona_vizinho(identificador2)
            self.nodos[identificador2].adiciona_vizinho(identificador1)

    def obtem_nodo(self, endereco, porta):
        """Retorna o nodo com o identificador especificado, se existir."""
        identificador = f"{endereco}:{porta}"
        return self.nodos.get(identificador, None)

    def __str__(self):
        """Representação em string do grafo, mostrando todos os nodos e seus vizinhos."""
        grafo_str = "Grafo:\n"
        for identificador, nodo in self.nodos.items():
            vizinhos = ', '.join(nodo.vizinhos)
            grafo_str += f"{identificador}: {vizinhos}\n"
        return grafo_str
    
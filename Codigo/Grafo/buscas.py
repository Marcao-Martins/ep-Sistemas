import random
import random
import pickle
from Codigo.peer import Peer
class Buscas:
    def __init__(self, grafo, endereco, porta, arquivo_vizinhos=None, arquivo_chave_valor=None):
        self.grafo = grafo
        self.peer = Peer(endereco, porta)  # Instanciando a classe Peer
        
        if arquivo_vizinhos:
            self.peer.load_neighbors(arquivo_vizinhos)
        if arquivo_chave_valor:
            self.peer.load_key_value_pairs(arquivo_chave_valor)
        
        self.mensagens_vistas = set()  # Para armazenar mensagens já vistas

    def flooding(self, mensagem):
        chave = mensagem['chave']
        origem = mensagem['origem']
        ttl = mensagem['ttl']
        seq_no = mensagem['seq_no']
        visitados = mensagem.get('visitados', set())

        mensagem_id = (origem, seq_no)
        if mensagem_id in self.mensagens_vistas:
            print("Flooding: Mensagem repetida!")
            return "Chave não encontrada"

        self.mensagens_vistas.add(mensagem_id)
    
        nodo_origem = self.grafo.obtem_nodo(*origem.split(':'))
        resultado = nodo_origem.busca_local(chave)
        if resultado:
            return f"Chave encontrada: {resultado}"

        if ttl > 0:
            visitados.add(origem)
            for vizinho in nodo_origem.vizinhos:
                if vizinho not in visitados:
                    nova_mensagem = mensagem.copy()
                    nova_mensagem['origem'] = vizinho
                    nova_mensagem['ttl'] = ttl - 1
                    nova_mensagem['seq_no'] = seq_no + 1
                    nova_mensagem['visitados'] = visitados
                    self.peer.transmite_mensagem(nova_mensagem, exclude_socket=None)
                    resultado = self.flooding(nova_mensagem)
                    if resultado:
                        return resultado

        return "Chave não encontrada"

    def random_walk(self, mensagem):
        chave = mensagem['chave']
        origem = mensagem['origem']
        ttl = mensagem['ttl']
        seq_no = mensagem['seq_no']
        ultimo_vizinho = mensagem.get('ultimo_vizinho', None)

        nodo_origem = self.grafo.obtem_nodo(*origem.split(':'))
        resultado = nodo_origem.busca_local(chave)
        if resultado:
            return f"Chave encontrada: {resultado}"

        if ttl <= 0 or not nodo_origem.vizinhos:
            return "Chave não encontrada"

        vizinhos_possiveis = list(nodo_origem.vizinhos - {ultimo_vizinho}) if ultimo_vizinho else list(nodo_origem.vizinhos)
        if not vizinhos_possiveis:
            vizinhos_possiveis = list(nodo_origem.vizinhos)

        vizinho_escolhido = random.choice(vizinhos_possiveis)
        nova_mensagem = mensagem.copy()
        nova_mensagem['origem'] = vizinho_escolhido
        nova_mensagem['ttl'] = ttl - 1
        nova_mensagem['seq_no'] = seq_no + 1
        nova_mensagem['ultimo_vizinho'] = origem
        self.peer.envia_mensagem(self.peer.conecta_peer(*vizinho_escolhido.split(':')), nova_mensagem)
        return self.random_walk(nova_mensagem)

    def busca_em_profundidade(self, mensagem):
        chave = mensagem['chave']
        origem = mensagem['origem']
        ttl = mensagem['ttl']
        seq_no = mensagem['seq_no']
        visitados = mensagem.get('visitados', set())

        nodo_origem = self.grafo.obtem_nodo(*origem.split(':'))
        resultado = nodo_origem.busca_local(chave)
        if resultado:
            return f"Chave encontrada: {resultado}"

        if ttl > 0:
            visitados.add(origem)
            for vizinho in nodo_origem.vizinhos:
                if vizinho not in visitados:
                    nova_mensagem = mensagem.copy()
                    nova_mensagem['origem'] = vizinho
                    nova_mensagem['ttl'] = ttl - 1
                    nova_mensagem['seq_no'] = seq_no + 1
                    nova_mensagem['visitados'] = visitados
                    self.peer.envia_mensagem(self.peer.conecta_peer(*vizinho.split(':')), nova_mensagem)
                    resultado = self.busca_em_profundidade(nova_mensagem)
                    if resultado:
                        return resultado

        return "Chave não encontrada"

    def inicia_servidor(self):
        self.peer.inicia_servidor()

    def handle_client(self, client_socket):
        self.peer.handle_client(client_socket)

    def conecta_peer(self, endereco, porta):
        return self.peer.conecta_peer(endereco, porta)

    def adiciona_vizinho(self, endereco, porta):
        self.peer.adiciona_vizinho(endereco, porta)

    def load_neighbors(self, filename):
        self.peer.load_neighbors(filename)

    def armazena_valor(self, chave, valor):
        self.peer.armazena_valor(chave, valor)

    def load_key_value_pairs(self, filename):
        self.peer.load_key_value_pairs(filename)

    def handle_request(self, request, client_socket):
        self.peer.handle_request(request, client_socket)
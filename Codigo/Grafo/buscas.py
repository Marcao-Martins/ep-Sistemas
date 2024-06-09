import random
import random
import json
import threading
import time

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Agora você pode importar o peer.py
from peer import Peer

class Buscas:
    def __init__(self, peer):
        self.peer = peer

    def flooding(self, mensagem):
        chave = mensagem['chave']
        origem = mensagem['origem']
        ttl = mensagem['ttl']
        seq_no = mensagem['seq_no']
        visitados = set(mensagem.get('visitados', []))

        mensagem_id = (origem, seq_no)
        if mensagem_id in self.peer.mensagens_vistas:
            print(f"Flooding: Mensagem repetida! ID: {mensagem_id}")
            return "Chave não encontrada"

        print(f"Flooding: Processando mensagem {mensagem_id} com TTL {ttl}")

        self.peer.mensagens_vistas.add(mensagem_id)

        print(f"Flooding: Tabela chave-valor local: {self.peer.chave_valor}")
        resultado = self.peer.chave_valor.get(chave)
        if resultado:
            print(f"Flooding: Chave encontrada localmente: {resultado}")
            return f"Chave encontrada: {resultado}"

        if ttl > 0:
            visitados.add(self.peer.endereco + ':' + str(self.peer.porta))
            for vizinho in self.peer.vizinhos:
                vizinho_endereco, vizinho_porta = vizinho.split(':')
                vizinho_identificador = f"{vizinho_endereco}:{vizinho_porta}"
                if vizinho_identificador not in visitados:
                    print(f"Flooding: Encaminhando mensagem para {vizinho_identificador}")
                    nova_mensagem = mensagem.copy()
                    nova_mensagem['origem'] = origem  # Mantém a origem original
                    nova_mensagem['ttl'] = ttl - 1
                    nova_mensagem['seq_no'] = seq_no + 1
                    nova_mensagem['visitados'] = list(visitados)
                    # Conecta ao vizinho antes de transmitir a mensagem
                    vizinho_socket = self.peer.conecta_peer(vizinho_endereco, int(vizinho_porta))
                    if vizinho_socket:
                        resposta = self.peer.envia_mensagem_busca(vizinho_socket, nova_mensagem)
                        vizinho_socket.close()
                        if resposta:
                            return resposta

        print("Flooding: Chave não encontrada")
        return "Chave não encontrada"


        
    def random_walk(self, mensagem):
        chave = mensagem['chave']
        origem = mensagem['origem']
        ttl = mensagem['ttl']
        seq_no = mensagem['seq_no']
        ultimo_vizinho = mensagem.get('ultimo_vizinho', None)

        resultado = self.peer.chave_valor.get(chave)
        if resultado:
            return f"Chave encontrada: {resultado}"

        if ttl <= 0 or not self.peer.vizinhos:
            return "Chave não encontrada"

        vizinhos_possiveis = [v for v in self.peer.vizinhos if v.getpeername() != ultimo_vizinho] if ultimo_vizinho else self.peer.vizinhos
        if not vizinhos_possiveis:
            vizinhos_possiveis = self.peer.vizinhos

        vizinho_escolhido = random.choice(vizinhos_possiveis)
        nova_mensagem = mensagem.copy()
        nova_mensagem['origem'] = f"{vizinho_escolhido.getpeername()[0]}:{vizinho_escolhido.getpeername()[1]}"
        nova_mensagem['ttl'] = ttl - 1
        nova_mensagem['seq_no'] = seq_no + 1
        nova_mensagem['ultimo_vizinho'] = origem
        self.peer.envia_mensagem(vizinho_escolhido, nova_mensagem)
        return self.random_walk(nova_mensagem)

    def busca_em_profundidade(self, mensagem):
        chave = mensagem['chave']
        origem = mensagem['origem']
        ttl = mensagem['ttl']
        seq_no = mensagem['seq_no']
        visitados = mensagem.get('visitados', set())

        resultado = self.peer.chave_valor.get(chave)
        if resultado:
            return f"Chave encontrada: {resultado}"

        if ttl > 0:
            visitados.add(origem)
            for vizinho in self.peer.vizinhos:
                vizinho_endereco, vizinho_porta = vizinho.getpeername()
                vizinho_identificador = f"{vizinho_endereco}:{vizinho_porta}"
                if vizinho_identificador not in visitados:
                    nova_mensagem = mensagem.copy()
                    nova_mensagem['origem'] = vizinho_identificador
                    nova_mensagem['ttl'] = ttl - 1
                    nova_mensagem['seq_no'] = seq_no + 1
                    nova_mensagem['visitados'] = visitados
                    self.peer.envia_mensagem(vizinho, nova_mensagem)
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

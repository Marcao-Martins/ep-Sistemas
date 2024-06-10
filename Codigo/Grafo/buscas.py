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
        hop = mensagem['hop']
        visitados = set(mensagem.get('visitados', []))

        resultado = self.peer.chave_valor.get(chave)
        if resultado:
            print(f"Flooding: Chave encontrada localmente: {resultado}")
            print(f"Flooding: Encaminhando Mensagem <{self.peer.endereco + ':' + str(self.peer.porta)}> <{seq_no}> <{ttl}> VAL <FL> <{resultado}> <{hop}> para {origem}")
            return (f"Chave Encontrada: <{self.peer.endereco + ':' + str(self.peer.porta)}> <{seq_no}> <{ttl}> VAL <FL> <{resultado}> <{hop}>"), hop

        if ttl > 0:
            visitados.add(self.peer.endereco + ':' + str(self.peer.porta))
            ttl = ttl -1
            seq_no = seq_no + 1
            hop = hop + 1
            for vizinho in self.peer.vizinhos:
                vizinho_endereco, vizinho_porta = vizinho.split(':')
                vizinho_identificador = f"{vizinho_endereco}:{vizinho_porta}"
                if vizinho_identificador not in visitados:
                    nova_mensagem = mensagem.copy()
                    nova_mensagem['origem'] = origem  # Mantém a origem original
                    nova_mensagem['ttl'] = ttl
                    nova_mensagem['seq_no'] = seq_no
                    nova_mensagem['hop'] = hop
                    nova_mensagem['visitados'] = list(visitados)
                    print(f"Flooding: Encaminhando Mensagem <{self.peer.endereco + ':' + str(self.peer.porta)}> <{seq_no}> <{ttl}> <FL> <{hop}> para {vizinho_identificador}")

                    # Conecta ao vizinho antes de transmitir a mensagem
                    vizinho_socket = self.peer.conecta_peer(vizinho_endereco, int(vizinho_porta))
                    if vizinho_socket:
                        resposta = self.peer.envia_mensagem_busca(vizinho_socket, nova_mensagem)
                        vizinho_socket.close()
                        if resposta and "VAL" in resposta:
                            partes_resposta = resposta.split('<')
                            resposta_hop = int(partes_resposta[-1].strip('<>'))
                            return resposta, resposta_hop

        elif ttl == 0:
            print(" TTL igual a zero, descartando mensagem")

        print("Chave não encontrada")
        return "Chave não encontrada", hop

            
    def random_walk(self, mensagem):
        chave = mensagem['chave']
        origem = mensagem['origem']
        ttl = mensagem['ttl']
        seq_no = mensagem['seq_no']
        hop = mensagem['hop']
        ultimo_vizinho = mensagem.get('ultimo_vizinho', None)

        resultado = self.peer.chave_valor.get(chave)
        if resultado:
            print(f"Random Walk: Chave encontrada localmente: {resultado}")
            print(f"Random Walk: Encaminhando Mensagem <{self.peer.endereco + ':' + str(self.peer.porta)}> <{seq_no}> <{ttl}> VAL <RW> <{resultado}> <{hop}> para {origem}")
            return (f"Chave Encontrada: <{self.peer.endereco + ':' + str(self.peer.porta)}> <{seq_no}> <{ttl}> VAL <RW> <{resultado}> <{hop}>"),hop

        if ttl <= 0 or not self.peer.vizinhos:
            print("Random Walk: Chave não encontrada ou TTL esgotado")
            return "Chave não encontrada",hop

        # Filtra os vizinhos possíveis para não incluir o último vizinho
        vizinhos_possiveis = [v for v in self.peer.vizinhos if v != ultimo_vizinho] if ultimo_vizinho else self.peer.vizinhos
        if not vizinhos_possiveis:
            print("Random Walk: Nenhum vizinho disponível para encaminhar")
            vizinhos_possiveis = self.peer.vizinhos

        vizinho_escolhido = random.choice(vizinhos_possiveis)
        nova_mensagem = mensagem.copy()
        ttl = ttl -1
        seq_no = seq_no + 1
        hop = hop + 1
        nova_mensagem['origem'] = origem  # Mantém a origem original
        nova_mensagem['ttl'] = ttl
        nova_mensagem['seq_no'] = seq_no
        nova_mensagem['hop'] = hop
        nova_mensagem['ultimo_vizinho'] = self.peer.endereco + ':' + str(self.peer.porta)
        print(f"Random Walk: Encaminhando mensagem <{self.peer.endereco + ':' + str(self.peer.porta)}> <{seq_no}> <{ttl}> <RW> <{hop}> para {vizinho_escolhido}")

        # Conecta ao vizinho antes de transmitir a mensagem
        vizinho_endereco, vizinho_porta = vizinho_escolhido.split(':')
        vizinho_socket = self.peer.conecta_peer(vizinho_endereco, int(vizinho_porta))
        if vizinho_socket:
            resposta = self.peer.envia_mensagem_busca(vizinho_socket, nova_mensagem)
            vizinho_socket.close()
            if resposta and "VAL" in resposta:
                partes_resposta = resposta.split('<')
                resposta_hop = int(partes_resposta[-1].strip('<>'))
                return resposta, resposta_hop

        print("Random Walk: Chave não encontrada")
        return "Chave não encontrada",hop




    def busca_em_profundidade(self, mensagem):
        chave = mensagem['chave']
        origem = mensagem['origem']
        ttl = mensagem['ttl']
        seq_no = mensagem['seq_no']
        hop = mensagem['hop']
        ultimo_vizinho = mensagem.get('ultimo_vizinho', None)

        mensagem_id = (origem, seq_no)

        # Inicialização de estruturas para cada mensagem
        if mensagem_id not in self.peer.noh_mae:
            self.peer.noh_mae[mensagem_id] = f"{self.peer.endereco}:{self.peer.porta}"
            self.peer.vizinho_ativo[mensagem_id] = None
            self.peer.vizinhos_candidatos[mensagem_id] = list(self.peer.vizinhos)

        resultado = self.peer.chave_valor.get(chave)
        if resultado:
            print(f"BP: Chave encontrada localmente: {resultado}")
            print(f"BP: Encaminhando Mensagem <{self.peer.endereco + ':' + str(self.peer.porta)}> <{seq_no}> <{ttl}> VAL <BP> <{resultado}> <{hop}> para {origem}")
            self.limpa_busca_em_profundidade(mensagem_id)
            return (f"Chave Encontrada: <{self.peer.endereco + ':' + str(self.peer.porta)}> <{seq_no}> <{ttl}> VAL <BP> <{resultado}> <{hop}>"), hop

        if ttl == 0:
            print("BP: TTL igual a zero, descartando mensagem")
            self.limpa_busca_em_profundidade(mensagem_id)
            return "Chave não encontrada", hop

        # Remover último vizinho dos vizinhos candidatos
        if ultimo_vizinho and ultimo_vizinho in self.peer.vizinhos_candidatos[mensagem_id]:
            self.peer.vizinhos_candidatos[mensagem_id].remove(ultimo_vizinho)

        # Condição de Parada 1: Se o nó mãe é o próprio endereço, vizinho ativo é último vizinho e vizinhos candidatos está vazio
        if self.peer.noh_mae[mensagem_id] == f"{self.peer.endereco}:{self.peer.porta}" and \
                self.peer.vizinho_ativo[mensagem_id] == ultimo_vizinho and \
                not self.peer.vizinhos_candidatos[mensagem_id]:
            print(f"BP: Nao foi possivel localizar a chave {chave}")
            self.limpa_busca_em_profundidade(mensagem_id)
            return "Chave não encontrada", hop

        # Condição de Parada 2: Se vizinho ativo está definido e não é último vizinho
        if self.peer.vizinho_ativo[mensagem_id] and self.peer.vizinho_ativo[mensagem_id] != ultimo_vizinho:
            print("BP: ciclo detectado, devolvendo a mensagem...")
            proximo = ultimo_vizinho

        # Condição de Parada 3: Se vizinhos candidatos está vazio
        elif not self.peer.vizinhos_candidatos[mensagem_id]:
            print("BP: nenhum vizinho encontrou a chave, retrocedendo...")
            proximo = ultimo_vizinho

        # Continuar busca
        else:
            proximo = random.choice(self.peer.vizinhos_candidatos[mensagem_id])
            self.peer.vizinho_ativo[mensagem_id] = proximo
            self.peer.vizinhos_candidatos[mensagem_id].remove(proximo)

        if not proximo:
            print("BP: Não foi possível determinar o próximo vizinho, encerrando busca.")
            self.limpa_busca_em_profundidade(mensagem_id)
            return "Chave não encontrada", hop

        ttl = ttl -1
        seq_no = seq_no + 1
        hop = hop + 1
        nova_mensagem = mensagem.copy()
        nova_mensagem['origem'] = origem
        nova_mensagem['ttl'] = ttl
        nova_mensagem['seq_no'] = seq_no
        nova_mensagem['hop'] = hop
        nova_mensagem['ultimo_vizinho'] = f"{self.peer.endereco}:{self.peer.porta}"

        vizinho_endereco, vizinho_porta = proximo.split(':')
        print(f"BP: Enviando mensagem <{self.peer.endereco + ':' + str(self.peer.porta)}> <{seq_no}> <{ttl}> <BP> <{hop}> para {vizinho_endereco}:{vizinho_porta}")
        vizinho_socket = self.peer.conecta_peer(vizinho_endereco, int(vizinho_porta))
        if vizinho_socket:
            resposta = self.peer.envia_mensagem_busca(vizinho_socket, nova_mensagem)
            vizinho_socket.close()
            if resposta and "VAL" in resposta:
                partes_resposta = resposta.split('<')
                resposta_hop = int(partes_resposta[-1].strip('<>'))
                self.limpa_busca_em_profundidade(mensagem_id)
                return resposta, resposta_hop

        print("BP: Chave não encontrada")
        self.limpa_busca_em_profundidade(mensagem_id)
        return "Chave não encontrada", hop
    
        
    def limpa_busca_em_profundidade(self, mensagem_id):
        if mensagem_id in self.peer.noh_mae:
            del self.peer.noh_mae[mensagem_id]
        if mensagem_id in self.peer.vizinho_ativo:
            del self.peer.vizinho_ativo[mensagem_id]
        if mensagem_id in self.peer.vizinhos_candidatos:
            del self.peer.vizinhos_candidatos[mensagem_id]


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

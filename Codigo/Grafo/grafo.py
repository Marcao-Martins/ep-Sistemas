import random
from Codigo.peer import Peer

class Buscas:
    def __init__(self, peer):
        self.peer = peer
        self.mensagens_vistas = set()  # Para armazenar mensagens já vistas

    def flooding(self, mensagem):
        chave = mensagem['chave']
        origem = mensagem['origem']
        ttl = mensagem['ttl']
        seq_no = mensagem['seq_no']
        visitados = mensagem.get('visitados', set())

        # Verificar se a mensagem já foi vista
        mensagem_id = (origem, seq_no)
        if mensagem_id in self.mensagens_vistas:
            print("Flooding: Mensagem repetida!")
            return "Chave não encontrada"

        self.mensagens_vistas.add(mensagem_id)
    
        if chave in self.peer.chave_valor:
            return f"Chave encontrada: {self.peer.chave_valor[chave]}"

        if ttl > 0:
            visitados.add(origem)
            for vizinho_socket in self.peer.vizinhos:
                vizinho = f"{vizinho_socket.getpeername()[0]}:{vizinho_socket.getpeername()[1]}"
                if vizinho not in visitados:
                    nova_mensagem = mensagem.copy()
                    nova_mensagem['origem'] = vizinho
                    nova_mensagem['ttl'] = ttl - 1
                    nova_mensagem['seq_no'] = seq_no + 1
                    nova_mensagem['visitados'] = visitados
                    self.peer.envia_mensagem(vizinho_socket, nova_mensagem)
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

        if chave in self.peer.chave_valor:
            return f"Chave encontrada: {self.peer.chave_valor[chave]}"

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

        if chave in self.peer.chave_valor:
            return f"Chave encontrada: {self.peer.chave_valor[chave]}"

        if ttl > 0:
            visitados.add(origem)
            for vizinho_socket in self.peer.vizinhos:
                vizinho = f"{vizinho_socket.getpeername()[0]}:{vizinho_socket.getpeername()[1]}"
                if vizinho not in visitados:
                    nova_mensagem = mensagem.copy()
                    nova_mensagem['origem'] = vizinho
                    nova_mensagem['ttl'] = ttl - 1
                    nova_mensagem['seq_no'] = seq_no + 1
                    nova_mensagem['visitados'] = visitados
                    self.peer.envia_mensagem(vizinho_socket, nova_mensagem)
                    resultado = self.busca_em_profundidade(nova_mensagem)
                    if resultado:
                        return resultado

        return "Chave não encontrada"

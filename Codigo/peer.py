import threading
import pickle
import socket

class Peer:
    # Inicia cada um dos nós - OK
    def __init__(self, endereco, porta):
        self.endereco = endereco
        self.porta = porta
        self.vizinhos = []
        self.chave_valor = {}  # Armazenamento de pares chave-valor
        
    # Inicia o servidor - OK
    def inicia_servidor(self):
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.bind((self.endereco, self.porta))
        servidor.listen(5) # 5 é o número máximo de conexões pendentes que o sistema permitirá antes de recusar novas conexões
        print(f'Servidor iniciado em {self.endereco}:{self.porta}')
        
        # Mantém o servidor em execução contínua, permitindo que ele aceite conexões de clientes indefinidamente
        while True:
            client_socket, addr = servidor.accept() # Bloqueia a execução até que uma nova conexão seja aceita
            print(f'Connection from {addr}')
            threading.Thread(target=self.handle_client, args=(client_socket,)).start() # Cria nova thread para cada conexão de cliente

    # Lida com as mensagens recebidas de um cliente conectado (quando um servidor aceita uma conexão ou quando nó adiciona um vizinho) - OK
    def handle_client(self, client_socket):
        while True:
            try:
                mensagem = client_socket.recv(4096) # Recebe a mensagem
                
                # Se houver uma mensagem, ele lida com ela usando o handle_request
                if mensagem:
                    request = pickle.loads(mensagem)
                    print(f'Mensagem para ser enviada: {request}')
                    self.handle_request(request) # tinha um client_socket aqui, mas tirei. Ver se não precisa depois
                else:
                    break
            except Exception as e:
                print(f'Error: {e}')
                break

    # Peer se conecta a outro peer na rede
    def conecta_peer(self, endereco_peer, porta_peer):
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((endereco_peer, porta_peer))

            # Enviar a mensagem "hello"
            mensagem = "hello"
            peer_socket.sendall(mensagem.encode())
            
            # Receber a resposta do peer
            resposta = peer_socket.recv(1024).decode()
            
            if resposta == "hello":
                self.peers.append(peer_socket)
                threading.Thread(target=self.handle_peer, args=(peer_socket,)).start()
                print(f"Mensagem recebida: {endereco_peer}:{porta_peer} HELLO")
                print(f"Adicionando vizinho na tabela: {self.endereco}:{self.porta}")
            else:
                peer_socket.close()
                print(f"Conexão com {endereco_peer}:{porta_peer} recusada, resposta não foi 'hello'.")
        
        # print(f'Connected to peer {endereco_peer}:{porta_peer}')
        # TODO: adicionar mensagem "HELLO" para envio -> confirmação

    # Carrega os vizinhos
    def load_neighbors(self, peer, filename):
        with open(filename, 'r') as file:
            for line in file:
                endereco_vizinho, porta_vizinho = line.strip().split(':')
                print(f'Tentando adicionar vizinho {endereco_vizinho}:{porta_vizinho}')
                self.conecta_peer(peer, endereco_vizinho, int(porta_vizinho))

    # Lista todos os vizinhos
    # TODO: fiz praticamente um get mas talvez não seja a melhor opção (ou sim, porque na função que a gente vai precisar usar ele, vai ter que associar todas as linhas a um numero LÁ e não sei se dá pra fazer isso aqui)
    def listar_vizinhos(self):
        return self.vizinhos
    
    # 
    def load_key_value_pairs(peer, filename):
        with open(filename, 'r') as file:
            for line in file:
                chave, valor = line.strip().split(' ')
                peer.armazena_valor(chave, valor)


    # Recebe a mensagem e decide como lidar com ele
    def handle_peer(self, peer_socket):
        while True:
            try:
                mensagem = peer_socket.recv(4096)
                if mensagem:
                    request = pickle.loads(mensagem)
                    print(f'Received mensagem from peer: {request}')
                    self.handle_request(request, peer_socket)
                else:
                    break
            except Exception as e:
                print(f'Error: {e}')
                break

    # TODO: ver se vai precisar de todos esses tipos de mensagem mesmo

    # Envia mensagem para determinado peer
    def envia_mensagem (self, peer_socket, mensagem):
        peer_socket.send(pickle.dumps(mensagem))

    # Transmite a mensagem para os outros nós, exceto o atual
    def transmite_mensagem(self, mensagem):
        print(f'Broadcasting mensagem: {mensagem}')
        for peer in self.peers:
            self.envia_mensagem(peer, mensagem)

    # Envia mensagem para todos os peers, incluindo o nó atual
    def envia_mensagem_para_peers(self, mensagem):
        for peer in self.peers:
            self.envia_mensagem(peer, mensagem)

    # Armazena um par chave-valor no dicionário 'chave_valor' do peer - OK
    def armazena_valor(self, chave, valor):
        self.chave_valor[chave] = valor
        print(f'Dados armazenados: {chave} -> {valor}')

    # TODO: arrumar essa função 
    def carrega_vizinhos(self, filename):
        with open(filename, 'r') as file:
            for line in file:
                endereco_vizinho, porta_vizinho = line.strip().split(':')
                print(f'Tentando adicionar vizinho {endereco_vizinho}:{porta_vizinho}')
                self.conecta_peer(self, endereco_vizinho, int(porta_vizinho))
                # SE DEU CERTO; Adicionar em uma lista de vizinhos

    # Carrega pares chave-valor de um txt e armazena no array "chave_valor" de um Peer - OK
    def carrega_chave_valor(peer, filename):
        with open(filename, 'r') as file:
            for line in file:
                chave, valor = line.strip().split(' ')
                peer.armazena_valor(chave, valor)

    def envia_hello(self, endereco, porta):
        mensagem = {'type': 'HELLO'}
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((endereco, porta))
            peer_socket.send(pickle.dumps(mensagem))
            peer_socket.close()
            print(f'Enviou HELLO para {endereco}:{porta}')
        except Exception as e:
            print(f'Erro ao enviar HELLO para {endereco}:{porta}: {e}')
 
    # Tinha um parâmetro client_socket -> tirei, ver se vai fazer falta depois
    def handle_request(self, request, client_socket):
        from Grafo.buscas import flooding, random_walk, busca_em_profundidade
        
        # Acho que nao precisa disso aqui........ a não ser pra casos específicos (e se for usar os parâmetros mesmo nas funções)
        if request['type'] == 'HELLO':
            # Envia 'HELLO' para um nó
        elif request['type'] == 'SEARCH':
            chave = request['chave']
            metodo = request['metodo']
            origem = request['origem']
            ttl = request['ttl']
            seq_no = request['seq_no']
            if metodo == 'FLOODING':
                visitados = request['visitados']
                flooding(self, chave, origem, ttl, seq_no, visitados)
            elif metodo == 'RANDOM_WALK':
                ultimo_vizinho = request['ultimo_vizinho']
                random_walk(self, chave, origem, ttl, seq_no, ultimo_vizinho)
            elif metodo == 'DFS':
                visitados = request['visitados']
                busca_em_profundidade(self, chave, origem, ttl, seq_no,)
        # Ver se vai usar esse FOUND e se precisa de algum outro
        elif request['type'] == 'FOUND':
            chave = request['chave']
            valor = request['valor']
            origem = request['origem']
            if (self.endereco, self.porta) == origem:
                print(f'Found data: {chave} -> {valor}')
            else:
                self.envia_mensagem_para_peers(request)
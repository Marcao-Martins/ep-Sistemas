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

    # Lista todos os vizinhos
    # TODO: fiz praticamente um get mas talvez não seja a melhor opção (ou sim, porque na função que a gente vai precisar usar ele, vai ter que associar todas as linhas a um numero LÁ e não sei se dá pra fazer isso aqui)
    def listar_vizinhos(self):
        return self.vizinhos

    # Inicia o servidor - OK
    def inicia_servidor(self):
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.bind((self.host, self.port))
        servidor.listen(5) # 5 é o número máximo de conexões pendentes que o sistema permitirá antes de recusar novas conexões
        print(f'Servidor iniciado em {self.host}:{self.port}')
        
        # Mantém o servidor em execução contínua, permitindo que ele aceite conexões de clientes indefinidamente
        while True:
            client_socket, addr = servidor.accept() # Bloqueia a execução até que uma nova conexão seja aceita
            print(f'Connection from {addr}')
            threading.Thread(target=self.handle_client, args=(client_socket,)).start() # Cria nova thread para cada conexão de cliente

    # Lida com as mensagens recebidas de um cliente conectado - OK
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
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_socket.connect((endereco_peer, porta_peer))
        self.peers.append(peer_socket)
        threading.Thread(target=self.handle_peer, args=(peer_socket,)).start()
        print(f'Connected to peer {endereco_peer}:{porta_peer}')
        # TODO: adicionar mensagem "HELLO" para envio -> confirmação

    # Carrega os vizinhos
    def load_neighbors(peer, filename):
        with open(filename, 'r') as file:
            for line in file:
                endereco_vizinho, porta_vizinho = line.strip().split(':')
                print(f'Tentando adicionar vizinho {endereco_vizinho}:{porta_vizinho}')
                conecta_peer(peer, endereco_vizinho, int(porta_vizinho))

    # 
    def load_key_value_pairs(peer, filename):
        with open(filename, 'r') as file:
            for line in file:
                chave, value = line.strip().split(' ')
                peer.armazena_valor(chave, value)


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

    # Tinha um parâmetro client_socket -> tirei, ver se vai fazer falta depois
    def handle_request(self, request):
        from Grafo.buscas import flooding, random_walk, busca_em_profundidade
        
        # TODO: verificar se as chamadas estão corretas e adicionar o "HELLO"
        if request['type'] == 'STORE':
            chave = request['chave']
            value = request['valor']
            self.armazena_valor(chave, value)
        elif request['type'] == 'SEARCH':
            chave = request['chave']
            method = request['method']
            origin = request['origin']
            if method == 'FLOODING':
                flooding(self, chave, origin)
            elif method == 'RANDOM_WALK':
                steps = request.get('steps', 3)
                random_walk(self, chave, origin, steps)
            elif method == 'DFS':
                visited = set(request.get('visited', []))
                busca_em_profundidade(self, chave, origin, visited)
        elif request['type'] == 'FOUND':
            chave = request['chave']
            value = request['value']
            origin = request['origin']
            if (self.host, self.port) == origin:
                print(f'Found data: {chave} -> {value}')
            else:
                self.envia_mensagem_para_peers(request)
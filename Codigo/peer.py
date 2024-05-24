import threading
import pickle
import socket

class Peer:

    # Inicia cada um dos nós
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.peers = []
        self.data_store = {}  # Armazenamento de pares chave-valor

    # Inicia o servidor
    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(5)
        print(f'Server started on {self.host}:{self.port}')
        
        # A cada cliente novo ele cria uma nova thread para lidar com ele
        while True:
            client_socket, addr = server.accept()
            print(f'Connection from {addr}')
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    # Lida com as mensagens recebidas de um cliente conectado
    def handle_client(self, client_socket):
        while True:
            try:
                message = client_socket.recv(4096)
                
                # Se houver uma mensagem, ele lida com ela usando o handle_request
                if message:
                    request = pickle.loads(message)
                    print(f'Received request: {request}')
                    self.handle_request(request, client_socket)
                else:
                    break
            except Exception as e:
                print(f'Error: {e}')
                break

    # Peer se conecta a outro peer na rede
    def connect_to_peer(self, peer_host, peer_port):
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_socket.connect((peer_host, peer_port))
        self.peers.append(peer_socket)
        threading.Thread(target=self.handle_peer, args=(peer_socket,)).start()
        print(f'Connected to peer {peer_host}:{peer_port}')

    # Carrega os vizinhos
    def load_neighbors(peer, filename):
        with open(filename, 'r') as file:
            for line in file:
                neighbor_host, neighbor_port = line.strip().split(':')
                print(f'Tentando adicionar vizinho {neighbor_host}:{neighbor_port}')
                connect_to_peer(peer, neighbor_host, int(neighbor_port))

    # 
    def load_key_value_pairs(peer, filename):
        with open(filename, 'r') as file:
            for line in file:
                key, value = line.strip().split(' ')
                peer.store_data(key, value)


    # Recebe a mensagem e decide como lidar com ele
    def handle_peer(self, peer_socket):
        while True:
            try:
                message = peer_socket.recv(4096)
                if message:
                    request = pickle.loads(message)
                    print(f'Received message from peer: {request}')
                    self.handle_request(request, peer_socket)
                else:
                    break
            except Exception as e:
                print(f'Error: {e}')
                break

    # Envia mensagem para determinado peer
    def send_message(self, peer_socket, message):
        peer_socket.send(pickle.dumps(message))
        

    # Transmite a mensagem para os outros nós
    def broadcast_message(self, message):
        print(f'Broadcasting message: {message}')
        for peer in self.peers:
            self.send_message(peer, message)

    # Provavelmente vou deletar essa
    def send_message_to_peers(self, message):
        for peer in self.peers:
            self.send_message(peer, message)

    # Armazena um par chave-valor no dicionário 'data_store' do peer
    def store_data(self, key, value):
        self.data_store[key] = value
        print(f'Stored data: {key} -> {value}')

    def handle_request(self, request, client_socket):
        # TODO: colocar as buscas aqui e corrigir a função
        from buscas import nome_das_buscas
        
        if request['type'] == 'STORE':
            key = request['key']
            value = request['value']
            self.store_data(key, value)
        elif request['type'] == 'SEARCH':
            key = request['key']
            method = request['method']
            origin = request['origin']
            if method == 'FLOODING':
                flooding(self, key, origin)
            elif method == 'RANDOM_WALK':
                steps = request.get('steps', 3)
                search_key_random_walk(self, key, origin, steps)
            elif method == 'DFS':
                visited = set(request.get('visited', []))
                search_key_dfs(self, key, origin, visited)
        elif request['type'] == 'FOUND':
            key = request['key']
            value = request['value']
            origin = request['origin']
            if (self.host, self.port) == origin:
                print(f'Found data: {key} -> {value}')
            else:
                self.send_message_to_peers(request)
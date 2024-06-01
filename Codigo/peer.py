import threading
import pickle
import socket
from Grafo.buscas import flooding, random_walk, busca_em_profundidade

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
                    self.handle_request(request, client_socket)
                else:
                    break
            except Exception as e:
                print(f'Error: {e}')
                break

    # Peer se conecta a outro peer na rede
    def conecta_peer(self, endereco, porta):
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((endereco, porta))
            return peer_socket
        except Exception as e:
            print(f'Erro ao conectar o peer {endereco}:{porta}: {e}')
            return None

    """
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
        except Exception as e:
            print(f'Error connecting to peer {endereco}:{porta}: {e}')
            return None

        # print(f'Connected to peer {endereco_peer}:{porta_peer}')
        # TODO: adicionar mensagem "HELLO" para envio -> confirmação

    """

    def adiciona_vizinho(self, endereco, porta):
        # Verificar se o vizinho já está na lista de vizinhos
        for vizinho_socket in self.vizinhos:
            if vizinho_socket.getpeername() == (endereco, porta):
                print(f'Vizinho {endereco}:{porta} já está na lista de vizinhos')
                return
    
        mensagem = {'type': 'HELLO'}
        try:
            vizinho_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            vizinho_socket.connect((endereco, porta))
            vizinho_socket.sendall(pickle.dumps(mensagem))
            resposta = pickle.loads(vizinho_socket.recv(4096))
            if resposta == "hello":
                self.vizinhos.append(vizinho_socket)
                threading.Thread(target=self.handle_client, args=(vizinho_socket,)).start()
                print(f'Conexão estabelecida com vizinho {endereco}:{porta}')
            else:
                print(f'Falha na conexão com vizinho {endereco}:{porta}, resposta não foi "hello"')
                vizinho_socket.close()
        except Exception as e:
            print(f'Erro ao conectar com vizinho {endereco}:{porta}: {e}')

    # Carrega os vizinhos a partir de um arquivo txt
    def load_neighbors(self, peer, filename):
        with open(filename, 'r') as file:
            for line in file:
                endereco_vizinho, porta_vizinho = line.strip().split(':')
                print(f'Tentando adicionar vizinho {endereco_vizinho}:{porta_vizinho}')
                self.adiciona_vizinho(peer, endereco_vizinho, int(porta_vizinho))
    
    # Armazena um par chave-valor no dicionário 'chave_valor' do peer - OK
    def armazena_valor(self, chave, valor):
        self.chave_valor[chave] = valor
        print(f'Dados armazenados: {chave} -> {valor}')

    # Carrega os pares chave-valores a partir de um arquivo txt
    def load_key_value_pairs(peer, filename):
        with open(filename, 'r') as file:
            for line in file:
                chave, valor = line.strip().split(' ')
                peer.armazena_valor(chave, valor)

    # Verificar o STORE e ver se tá passando a mensagem de forma certinha :)
    def handle_request(self, request, client_socket):
        operacao = request.get('type')

        if operacao == 'HELLO':
            self.handle_hello(client_socket)
        elif operacao == 'SEARCH':
            self.handle_search(request, client_socket)
        #elif operacao == "STORE":
        # Não tenho certeza se essa STORE precisa
            # self.handle_store(request, client_socket)
            """
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
        elif operacao == 'FOUND':
            chave = request['chave']
            valor = request['valor']
            origem = request['origem']
            if (self.endereco, self.porta) == origem:
                print(f'Found data: {chave} -> {valor}')
            else:
                self.envia_mensagem_para_peers(request)
            
            """
    
    def handle_hello(self, client_socket):
        try:
            client_socket.sendall(pickle.dumps("hello"))
            print(f'Enviou HELLO para {self.endereco}:{self.porta}')
        except Exception as e:
            print(f'Erro ao enviar HELLO para {self.endereco}:{self.porta}: {e}')

    def handle_search(self, request, client_socket):
        print("Começando processo de busca")
        chave = request.get('chave')
        metodo = request.get('metodo')
        origem = request.get('origem')
        ttl = request.get('ttl')
        seq_no = request.get('seq_no')
        
        if metodo == 'FLOODING':
            mensagem = {
            'chave': chave,
            'metodo': metodo,
            'origem': origem,
            'ttl': ttl,
            'seq_no': seq_no
            }
            flooding(mensagem, client_socket)
        elif metodo == 'RANDOM_WALK':
            ultimo_vizinho = request.get('ultimo_vizinho')
            mensagem = {
            'chave': chave,
            'metodo': metodo,
            'origem': origem,
            'ttl': ttl,
            'seq_no': seq_no,
            'ultimo_vizinho': ultimo_vizinho
            }
            random_walk(mensagem, client_socket)
        elif metodo == 'DFS':
            visitados = request.get('visitados')
            mensagem = {
            'chave': chave,
            'metodo': metodo,
            'origem': origem,
            'ttl': ttl,
            'seq_no': seq_no
            }
            busca_em_profundidade(mensagem, client_socket)
        """
        elif ttl > 0:
            ttl -= 1
            hop_count += 1
            mensagem = {
                'origin': origin,
                'seqno': seqno,
                'ttl': ttl,
                'search': 'SEARCH',
                'mode': mode,
                'last_hop_port': self.porta,
                'key': key,
                'hop_count': hop_count
            }
            self.encaminha_mensagem(mensagem, client_socket)
        """

    # Envia mensagem para determinado peer
    def envia_mensagem (self, peer_socket, mensagem):
        try:
            peer_socket.send(pickle.dumps(mensagem))
        except Exception as e:
            print(f'Erro ao enviar mensagem para o peer: {e}')

    # Transmite a mensagem para os outros nós, exceto o atual
    def transmite_mensagem(self, mensagem, exclude_socket=None):
        print(f'Transmitindo a mensagem: {mensagem}')
        for vizinho in self.vizinhos:
            if vizinho != exclude_socket:
                try:
                    self.envia_mensagem(vizinho, mensagem)
                except Exception as e:
                    print(f'Error forwarding message to neighbor: {e}')
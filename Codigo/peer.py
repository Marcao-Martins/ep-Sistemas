import threading
import pickle
import socket
import time
from mensagem import Message

class Peer:
    # Inicia cada um dos nós - OK
    def __init__(self, endereco, porta):
        self.endereco = endereco
        self.porta = porta
        self.vizinhos = []
        self.chave_valor = {}  # Armazenamento de pares chave-valor
        self.mensagens_vistas = set() # Para armazenar mensagens já vistas
        self.seq_no = 0

        # Inicializa o servidor em uma thread separada
        self.server_thread = threading.Thread(target=self.inicia_servidor)
        self.server_thread.daemon = True  # Isso permite que o programa termine mesmo que o servidor esteja rodando
        self.server_thread.start()

        # Aguarda um breve intervalo para garantir que o servidor esteja iniciado
        time.sleep(1)
        
    # Inicia o servidor - OK
    def inicia_servidor(self):
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.bind((self.endereco, self.porta))
        servidor.listen(5) # 5 é o número máximo de conexões pendentes que o sistema permitirá antes de recusar novas conexões
        print(f'Servidor criado: {self.endereco}:{self.porta}\n')
        
        # Mantém o servidor em execução contínua, permitindo que ele aceite conexões de clientes indefinidamente
        while True:
            peer_socket, addr = servidor.accept() # Bloqueia a execução até que uma nova conexão seja aceita
            print(f'Conexão de {addr}')
            threading.Thread(target=self.handle_peer, args=(peer_socket,)).start() # Cria nova thread para cada conexão de cliente

    # Lida com as mensagens recebidas de um peer conectado (quando um servidor aceita uma conexão ou quando nó adiciona um vizinho) - OK
    def handle_peer(self, peer_socket):
        while True:
            try:
                mensagem = peer_socket.recv(4096) # Recebe a mensagem
                
                # Se houver uma mensagem, ele lida com ela usando o handle_request
                if mensagem:
                    request = pickle.loads(mensagem)
                    print(f'Mensagem para ser enviada: {request}')
                    self.handle_request(request, peer_socket)
                else:
                    break
            except Exception as e:
                print(f'Error: {e}')
                peer_socket.close()
                break

    # Peer se conecta a outro peer na rede
    def conecta_peer(self, endereco, porta):
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((endereco, porta))
            return peer_socket
        except:
            print(f'    Erro ao conectar!')
            return None

    def adiciona_vizinho(self, endereco, porta):
        # Verificar se o vizinho já está na lista de vizinhos
        for vizinho_socket in self.vizinhos:
            if vizinho_socket.getpeername() == (endereco, porta):
                print(f'Vizinho {endereco}:{porta} já está na tabela de vizinhos')
                return
        mensagem = self.formata_mensagem('HELLO')
        self.log_encaminhamento(mensagem, endereco, porta)

        try:
            vizinho_socket = self.conecta_peer(endereco, porta)
            if vizinho_socket:
                self.seq_no += 1
                # se pa da pra substituir isso aqui por algum handle
                resposta = self.handle_request('HELLO', vizinho_socket)
                # self.envia_mensagem(vizinho_socket, mensagem)
                # resposta = vizinho_socket.recv(4096)
                # resposta = pickle.loads(resposta)
                if resposta == "hello":
                    self.vizinhos.append(vizinho_socket)
                    threading.Thread(target=self.handle_peer, args=(vizinho_socket,)).start()
                    print(f'Conexão estabelecida com vizinho {endereco}:{porta}')
                else:
                    vizinho_socket.close()
        except:
            # print(f'    Erro ao conectar!')
            return None
        
    def formata_mensagem(self, operacao, *argumentos):
        mensagem = f"{self.endereco}:{self.porta} {self.seq_no} 1 {operacao}"
        if argumentos:
            mensagem += " " + " ".join(map(str, argumentos))
        return mensagem + "\n"

    def log_encaminhamento(self, mensagem, endereco, porta):
        print(f'Encaminhando mensagem "{mensagem.strip()}" para {endereco}:{porta}')

    # Carrega os vizinhos a partir de um arquivo txt
    def load_neighbors(self, filename): # tinha um 'peer' aqui, tirei... não faz sentido
        with open(filename, 'r') as file:
            for line in file:
                endereco_vizinho, porta_vizinho = line.strip().split(':')
                print(f'Tentando adicionar vizinho {endereco_vizinho}:{porta_vizinho}')
                # vizinho = Peer(endereco_vizinho, porta_vizinho)
                self.adiciona_vizinho(endereco_vizinho, int(porta_vizinho))
    
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

    # Verificar o STORE e ver se tá passando a mensagem de forma certinha
    def handle_request(self, request, peer_socket):
        operacao = request.get('operacao')

        if operacao == 'HELLO':
            resposta = self.handle_hello(peer_socket)
            return resposta
        elif operacao == 'SEARCH':
            self.handle_search(request, peer_socket)
    
    def handle_hello(self, peer_socket):
        try:
            peer_socket.sendall(pickle.dumps("hello"))
            resposta = peer_socket.recv(4096)
            resposta = pickle.loads(resposta)
            print(f'Enviou HELLO para {self.endereco}:{self.porta}')

            return resposta
        except:
            print(f'Erro ao enviar HELLO para {self.endereco}:{self.porta}')

    def handle_search(self, request, peer_socket):
        from Grafo.buscas import flooding, random_walk, busca_em_profundidade
        
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
            flooding(mensagem, peer_socket)
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
            random_walk(mensagem, peer_socket)
        elif metodo == 'DFS':
            visitados = request.get('visitados')
            mensagem = {
            'chave': chave,
            'metodo': metodo,
            'origem': origem,
            'ttl': ttl,
            'seq_no': seq_no
            }
            busca_em_profundidade(mensagem, peer_socket)
        elif ttl > 0: # Decrementa o TTL e verifica se ainda é válido
            ttl -= 1
            hop_count += 1
            mensagem = {
                'origem': origem,
                'seqno': self.seq_no,
                'ttl': ttl,
                'last_hop_port': self.porta,
                'chave': chave,
                'hop_count': hop_count
            }
            self.encaminha_mensagem(mensagem, peer_socket)

    # Envia mensagem para determinado peer
    def envia_mensagem (self, peer_socket, mensagem):
        try:
            peer_socket.send(pickle.dumps(mensagem))
        except:
            print(f'Erro ao enviar mensagem para o peer!')

    # Transmite a mensagem para os outros nós, exceto o atual
    def transmite_mensagem(self, mensagem, exclude_socket=None):
        print(f'Transmitindo a mensagem: {mensagem}')
        for vizinho in self.vizinhos:
            if vizinho != exclude_socket:
                try:
                    self.envia_mensagem(vizinho, mensagem)
                except:
                    print(f'Erro ao transmitir mensagens para os vizinhos!')
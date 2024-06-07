import threading
import pickle
import socket
import time
from mensagem import Message

class Peer:
    def __init__(self, endereco, porta):
        self.endereco = endereco
        self.porta = porta
        self.vizinhos = []
        self.chave_valor = {}  # Armazenamento de pares chave-valor
        self.mensagens_vistas = set() # Para armazenar mensagens já vistas
        self.seq_no = 1

        # Inicializa o servidor em uma thread separada
        self.server_thread = threading.Thread(target=self.inicia_servidor)
        self.server_thread.daemon = True  # Isso permite que o programa termine mesmo que o servidor esteja rodando
        self.server_thread.start()

        # Aguarda um breve intervalo para garantir que o servidor esteja iniciado
        time.sleep(1)

    def inicia_servidor(self):
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.bind((self.endereco, self.porta))
        servidor.listen(5) # 5 é o número máximo de conexões pendentes que o sistema permitirá antes de recusar novas conexões
        print(f'Servidor criado: {self.endereco}:{self.porta}\n')

        while True:
            peer_socket, addr = servidor.accept() # Bloqueia a execução até que uma nova conexão seja aceita
            print(f'Conexão de {addr}')
            endereco_vizinho, porta_vizinho = addr  # Obtém o endereço e porta do vizinho
            threading.Thread(target=self.handle_peer, args=(peer_socket, endereco_vizinho, porta_vizinho)).start()

    def handle_peer(self, peer_socket, endereco_vizinho, porta_vizinho):
        try:
            print(f'Conexão estabelecida com vizinho {endereco_vizinho}:{porta_vizinho}')
            self.adiciona_vizinho(endereco_vizinho, porta_vizinho)
            while True:
                try:
                    mensagem = peer_socket.recv(4096) # Recebe a mensagem
                    if mensagem:
                        request = pickle.loads(mensagem)
                        print(f'Mensagem recebida: {request}')
                        self.handle_request(request, peer_socket)
                    else:
                        break
                except Exception as e:
                    print(f'Erro ao receber mensagem: {e}')
                    break
        except Exception as e:
            print(f'Erro ao lidar com o peer {endereco_vizinho}:{porta_vizinho}: {e}')
        finally:
            peer_socket.close()

    def conecta_peer(self, endereco, porta):
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((endereco, porta))
            return peer_socket
        except Exception as e:
            print(f'Erro ao conectar com o peer {endereco}:{porta}: {e}')
            return None

    def adiciona_vizinho(self, endereco, porta):
        for vizinho_socket in self.vizinhos:
            if vizinho_socket.getpeername() == (endereco, porta):
                print(f'Vizinho {endereco}:{porta} já está na tabela de vizinhos')
                return
        mensagem = self.formata_mensagem('HELLO')
        self.log_encaminhamento(mensagem, endereco, porta)
        try:
            vizinho_socket = self.conecta_peer(endereco, porta)
            if vizinho_socket:
                self.envia_mensagem(vizinho_socket, {'operacao': 'HELLO'})
                resposta = vizinho_socket.recv(4096)
                resposta = pickle.loads(resposta)
                if resposta.get('operacao') == 'HELLO_OK':
                    self.vizinhos.append(vizinho_socket)
                    threading.Thread(target=self.handle_peer, args=(vizinho_socket, endereco, porta)).start()
                    print(f'Conexão estabelecida com vizinho {endereco}:{porta}')
                else:
                    print(f'Falha ao receber resposta HELLO_OK de {endereco}:{porta}')
                    vizinho_socket.close()
        except Exception as e:
            print(f'Erro ao adicionar vizinho {endereco}:{porta}: {e}')

    def formata_mensagem(self, operacao, *argumentos):
        mensagem = f"{self.endereco}:{self.porta} {self.seq_no} 1 {operacao}"
        if argumentos:
            mensagem += " " + " ".join(map(str, argumentos))
        return mensagem + "\n"

    def log_encaminhamento(self, mensagem, endereco, porta):
        print(f'Encaminhando mensagem "{mensagem.strip()}" para {endereco}:{porta}')

    def load_neighbors(self, filename):
        with open(filename, 'r') as file:
            for line in file:
                endereco_vizinho, porta_vizinho = line.strip().split(':')
                print(f'Tentando adicionar vizinho {endereco_vizinho}:{porta_vizinho}')
                self.adiciona_vizinho(endereco_vizinho, int(porta_vizinho))

    def armazena_valor(self, chave, valor):
        self.chave_valor[chave] = valor
        print(f'\n Adicionando par ({chave}, {valor}) na tabela local')

    def load_key_value_pairs(self, filename):
        with open(filename, 'r') as file:
            for line in file:
                chave, valor = line.strip().split(' ')
                self.armazena_valor(chave, valor)

    def handle_request(self, request, peer_socket):
        operacao = request.get('operacao')
        if operacao == 'HELLO':
            resposta = self.handle_hello(peer_socket)
            return resposta
        elif operacao == 'SEARCH':
            self.handle_search(request, peer_socket)

    def handle_hello(self, peer_socket):
        try:
            response = {'operacao': 'HELLO_OK'}
            peer_socket.sendall(pickle.dumps(response))
            print(f'Enviou HELLO_OK para {peer_socket.getpeername()}')
        except Exception as e:
            print(f'Erro ao enviar HELLO_OK para {peer_socket.getpeername()}: {e}')

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
                'seq_no': seq_no,
                'visitados': visitados
            }
            busca_em_profundidade(mensagem, peer_socket)

    def envia_mensagem(self, peer_socket, mensagem):
        try:
            peer_socket.send(pickle.dumps(mensagem))
        except Exception as e:
            print(f'Erro ao enviar mensagem para o peer {peer_socket.getpeername()}: {e}')

    def transmite_mensagem(self, mensagem, exclude_socket=None):
        print(f'Transmitindo a mensagem: {mensagem}')
        for vizinho in self.vizinhos:
            if vizinho != exclude_socket:
                try:
                    self.envia_mensagem(vizinho, mensagem)
                except Exception as e:
                    print(f'Erro ao transmitir mensagem para o vizinho {vizinho.getpeername()}: {e}')

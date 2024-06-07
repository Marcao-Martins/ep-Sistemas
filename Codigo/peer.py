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
        self.server_thread.daemon = True  # Permite que o programa termine mesmo que o servidor esteja rodando
        self.server_thread.start()

        time.sleep(1) # Aguarda um breve intervalo para garantir que o servidor esteja iniciado

    def inicia_servidor(self):
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.bind((self.endereco, self.porta))
        servidor.listen(5) # número máximo de conexões pendentes que o sistema permitirá antes de recusar novas conexões
        
        print(f'Servidor criado: {self.endereco}:{self.porta}\n')

        while True:
            peer_socket, addr = servidor.accept()  # Bloqueia a execução 
            threading.Thread(target=self.handle_peer, args=(peer_socket,)).start()

    def formata_mensagem(self, operacao, *argumentos):
        mensagem = f"{self.endereco}:{self.porta} {self.seq_no} 1 {operacao}"
        if argumentos:
            mensagem += " " + " ".join(map(str, argumentos))
        return mensagem + "\n"

    def load_neighbors(self, filename):
        with open(filename, 'r') as file:
            for line in file:
                endereco_vizinho, porta_vizinho = line.strip().split(':')
                print(f'Tentando adicionar vizinho {endereco_vizinho}:{porta_vizinho}')
                self.adiciona_vizinho(endereco_vizinho, int(porta_vizinho))

    def load_key_value_pairs(self, filename):
        with open(filename, 'r') as file:
            for line in file:
                chave, valor = line.strip().split(' ')
                self.armazena_valor(chave, valor)

    def armazena_valor(self, chave, valor):
        self.chave_valor[chave] = valor
        print(f'\n Adicionando par ({chave}, {valor}) na tabela local')

    def extrai_informacoes_da_mensagem(self, mensagem):
        # No formato "127.0.0.1:5001 1 1 HELLO"
        partes = mensagem.split()
        endereco_porta = partes[0]
        end_peer, porta_peer = endereco_porta.split(':')
        operacao = partes[3]
        return end_peer, int(porta_peer), operacao

    def handle_peer(self, peer_socket):
        try:
            mensagem = peer_socket.recv(1024).decode()  # Lê a mensagem enviada pelo peer
            print(f"Mensagem recebida pelo servidor: {mensagem}")
            endereco_vizinho, porta_vizinho, operacao = self.extrai_informacoes_da_mensagem(mensagem)
            print(f"Essa é a operacao desejada: {operacao}")
            
            # Envia resposta de OK
            peer_socket.send(f"{operacao}_OK".encode())
            # peer_socket.close()

            if operacao == "HELLO":
                self.handle_hello(endereco_vizinho, porta_vizinho, 'ADC VIZINHO')
            elif operacao == "SEARCH":
                self.handle_search(peer_socket, mensagem)
        
        except Exception as e:
            print(f'Erro ao lidar com o peer {endereco_vizinho}:{porta_vizinho}: {e}')
        finally:
            peer_socket.close()
            

    def conecta_peer(self, endereco, porta):
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((endereco, porta))
            return peer_socket
        except:
            print(f'    Erro ao conectar!')
            return None

    def adiciona_vizinho(self, endereco, porta):
        """
            Função com a lógica de adicionar um vizinho a partir do txt dado

            agrs:
                endereco (string):
                porta (int):

        """
        if f"{endereco}:{porta}" in self.vizinhos:
            print(f'Vizinho {endereco}:{porta} já está na tabela de vizinhos')
            return
        
        try: 
            mensagem = f"{self.endereco}:{self.porta} {self.seq_no} 1 HELLO"
            print(f'Encaminhando mensagem "{mensagem}" para {endereco}:{porta}')

            vizinho_socket = self.conecta_peer(endereco, porta)
            resposta =  self.envia_mensagem(vizinho_socket, mensagem)
            if resposta:
                print(f'    Envio feito com sucesso: {mensagem}')
                self.vizinhos.append(f"{endereco}:{porta}")
            else:
                print(f'    Não foi possível enviar a mensagem {mensagem}')
        except:
            resposta =  False
        finally:
            if vizinho_socket:
                vizinho_socket.close()

        self.seq_no += 1


    def handle_hello(self, endereco, porta, op):
        if op == 'ADC VIZINHO':
            print(f' Adicionando vizinho na tabela de {endereco}:{porta}')
            self.vizinhos.append(f"{endereco}:{porta}")

        elif op == 'MENU HELLO': 
            try:
                mensagem = f"{self.endereco}:{self.porta} {self.seq_no} 1 HELLO"
                print(f'Encaminhando mensagem "{mensagem}" para {endereco}:{porta}')
                vizinho_socket = self.conecta_peer(endereco, porta)
                resposta =  self.envia_mensagem(vizinho_socket, mensagem)
            
                if resposta:
                    print(f'    Envio feito com sucesso: {mensagem}')
                else:
                    print(f'    Não foi possível enviar a mensagem {mensagem}')
            except:
                resposta =  False
            finally:
                if vizinho_socket:
                    vizinho_socket.close()

        self.seq_no += 1


    def handle_search(self, request, peer_socket, mensagem):
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
        """
            Função feita para enviar mensagens e receber uma resposta

            args:
                peer_socket: peer que está enviando a mensagem
                mensagem (string): mensagem a ser enviada
            return:
                resposta: resposta recebida a partir da função recv
        """
        try:
            peer_socket.send(mensagem.encode())
            resposta = peer_socket.recv(4096).decode()
            return resposta
        except:
            return

    def transmite_mensagem(self, mensagem, exclude_socket=None):
        print(f'Transmitindo a mensagem: {mensagem}')
        for vizinho in self.vizinhos:
            if vizinho != exclude_socket:
                try:
                    self.envia_mensagem(vizinho, mensagem)
                except Exception as e:
                    print(f'Erro ao transmitir mensagem para o vizinho {vizinho.getpeername()}: {e}')
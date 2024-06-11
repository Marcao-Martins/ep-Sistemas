import threading
import json
import socket
import time
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class Peer:
    def __init__(self, endereco, porta, ttl_padrao=100):
        self.endereco = endereco
        self.porta = porta
        self.vizinhos = []
        self.chave_valor = {}  # Armazenamento de pares chave-valor
        self.ttl_padrao = ttl_padrao
        self.mensagens_vistas = set()  # Para armazenar mensagens já vistas
        self.seq_no = 1

        # Estruturas para estatísticas
        self.contadores_busca = {'FL': 0, 'RW': 0, 'BP': 0}

        # Estruturas para busca em profundidade
        self.noh_mae = {}
        self.vizinho_ativo = {}
        self.vizinhos_candidatos = {}

        # Inicializa o servidor em uma thread separada
        self.server_thread = threading.Thread(target=self.inicia_servidor)
        self.server_thread.daemon = True  # Permite que o programa termine mesmo que o servidor esteja rodando
        self.server_thread.start()

        time.sleep(1)  # Aguarda um breve intervalo para garantir que o servidor esteja iniciado
        
    def inicia_servidor(self):
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.bind((self.endereco, self.porta))
        servidor.listen(5) # número máximo de conexões pendentes que o sistema permitirá antes de recusar novas conexões
        
        print(f'Servidor criado: {self.endereco}:{self.porta}\n')

        while True:
            peer_socket, addr = servidor.accept()  # Bloqueia a execução 
            threading.Thread(target=self.handle_peer, args=(peer_socket,)).start()

    # Carrega o arquivo de vizinhos
    def load_neighbors(self, filename):
        with open(filename, 'r') as file:
            for line in file:
                endereco_vizinho, porta_vizinho = line.strip().split(':')
                print(f'Tentando adicionar vizinho {endereco_vizinho}:{porta_vizinho}')
                self.adiciona_vizinho(endereco_vizinho, int(porta_vizinho))

    # Carrega o arquivo de chave-valor
    def load_key_value_pairs(self, filename):
        with open(filename, 'r') as file:
            for line in file:
                chave, valor = line.strip().split(' ')
                self.armazena_valor(chave, valor)

    # Armazena valor a partir do arquivo de chave-valor
    def armazena_valor(self, chave, valor):
        self.chave_valor[chave] = valor
        print(f'\n Adicionando par ({chave}, {valor}) na tabela local')

    # Usada para extrair informações de mensagens
    def extrai_informacoes_da_mensagem(self, mensagem):
        # No formato "127.0.0.1:5001 1 1 HELLO"
        partes = mensagem.split()
        endereco_porta = partes[0]
        end_peer, porta_peer = endereco_porta.split(':')
        operacao = partes[3]
        return end_peer, int(porta_peer), operacao

    # Principal função para lidar com as mensagens recebidas de um peer
    def handle_peer(self, peer_socket):
        try:
            mensagem = peer_socket.recv(1024).decode()  # Lê a mensagem enviada pelo peer
            print(f'Mensagem recebida: "{mensagem}"')

            # Verifica se a mensagem é um JSON
            try:
                mensagem_json = json.loads(mensagem)
                operacao = mensagem_json.get('metodo', 'UNKNOWN')
            except json.JSONDecodeError:
                mensagem_json = None
                endereco_vizinho, porta_vizinho, operacao = self.extrai_informacoes_da_mensagem(mensagem)

            # Envia resposta de OK para HELLO e BYE
            if operacao == "HELLO" or operacao == "BYE":
                peer_socket.send(f'{operacao}_OK'.encode())

            if operacao == "HELLO":
                self.handle_hello(endereco_vizinho, porta_vizinho, 'ADC VIZINHO')
            elif (operacao == "FL" or operacao == "RW" or operacao == "BP") and mensagem_json:
                self.handle_search(mensagem_json, peer_socket)
            elif operacao == "BYE":
                self.handle_bye(endereco_vizinho, porta_vizinho)
        
        except Exception as e:
            print(f'Erro ao lidar com a mensagem recebida: {e}')
        finally:
            peer_socket.close()

    # Conecta um peer ao outro
    def conecta_peer(self, endereco, porta):
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((endereco, porta))
            return peer_socket
        except:
            print(f'    Erro ao conectar!')
            return None

    # Função para adicionar vizinhos inicialmente, usada depois do carregamento do arquivo txt de vizinhos
    def adiciona_vizinho(self, endereco, porta):
        if f'{endereco}:{porta}' in self.vizinhos:
            print(f'Vizinho {endereco}:{porta} já está na tabela de vizinhos')
            return
        
        try: 
            mensagem = f'{self.endereco}:{self.porta} {self.seq_no} 1 HELLO'
            print(f'Encaminhando mensagem "{mensagem}" para {endereco}:{porta}')

            vizinho_socket = self.conecta_peer(endereco, porta)
            resposta =  self.envia_mensagem(vizinho_socket, mensagem)
            if resposta == "HELLO_OK":
                print(f'    Envio feito com sucesso: {mensagem}')
                self.vizinhos.append(f'{endereco}:{porta}')
            else:
                print(f'    Não foi possível enviar a mensagem {mensagem}')
        except:
            resposta =  False
        finally:
            if vizinho_socket:
                vizinho_socket.close()

        self.seq_no += 1

    # Lida com a operação HELLO, para adicionar vizinho ou enviar HELLO pelo MENU
    def handle_hello(self, endereco, porta, op):
        if op == 'ADC VIZINHO':
            if f'{endereco}:{porta}' in self.vizinhos:
                print(f'    Vizinho {endereco}:{porta} já está na tabela de vizinhos')
                return
            else:
                print(f'    Adicionando vizinho na tabela de {endereco}:{porta}\n')
                self.vizinhos.append(f'{endereco}:{porta}')

        elif op == 'MENU HELLO': 
            try:
                mensagem = f'{self.endereco}:{self.porta} {self.seq_no} 1 HELLO'
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

    # Função usada na operação BYE para remover vizinhos
    def remove_vizinhos(self):
        mensagem = f'{self.endereco}:{self.porta} {self.seq_no} 1 BYE' # Constrói mensagens que vai enviar para vizinhos

            # Cria uma cópia da lista de vizinhos para evitar problemas ao remover elementos durante a iteração
        vizinhos_copia = self.vizinhos.copy()

        for vizinho_str in vizinhos_copia:
            try:    
                endereco_vizinho, porta_vizinho = vizinho_str.split(':')
                porta_vizinho = int(porta_vizinho)
                print(f'Encaminhando mensagem "{mensagem}" para {endereco_vizinho}:{porta_vizinho}')
                vizinho_socket = self.conecta_peer(endereco_vizinho, porta_vizinho)
                resposta =  self.envia_mensagem(vizinho_socket, mensagem)
                if resposta == "BYE_OK":
                    print(f'    Envio feito com sucesso: {mensagem}')
                    self.vizinhos.remove(f'{endereco_vizinho}:{porta_vizinho}')
                else:
                    print(f'    Não foi possível enviar a mensagem {mensagem}')
            except:
                resposta =  False
            finally:
                if vizinho_socket:
                    vizinho_socket.close()
    
    # Lida com a operação BYE
    def handle_bye(self, endereco, porta):
        print(f'    Removendo vizinho da tabela {endereco}:{porta}')
        self.vizinhos.remove(f'{endereco}:{porta}')
        
        
    # Envia as mensagens de busca
    def envia_mensagem_busca(self, peer_socket, mensagem):
        try:
            # Converta qualquer set na mensagem para lista
            mensagem['visitados'] = list(mensagem.get('visitados', []))
            mensagem_json = json.dumps(mensagem)
            peer_socket.send(mensagem_json.encode())
            resposta = peer_socket.recv(4096).decode()
            if resposta:
                resposta_dict = json.loads(resposta)
                return resposta_dict
            else:
                return None
        except Exception as e:
            print(f"Erro ao enviar mensagem de busca: {e}")
            return None

    # Lida com as mensagens de busca
    def handle_search(self, request, peer_socket):
        from Grafo.buscas import Buscas
        buscas = Buscas(self)

        chave = request.get('chave')
        metodo = request.get('metodo')
        origem = request.get('origem')
        ttl = request.get('ttl')
        seq_no = request.get('seq_no')
        hop = request.get('hop')

        # Verificar se a mensagem já foi vista
        mensagem_id = (origem, seq_no)
        if mensagem_id in self.mensagens_vistas:
            print("Mensagem repetida!")
            resposta = {"status": "Mensagem repetida"}
            peer_socket.send(json.dumps(resposta).encode())
            return

        self.mensagens_vistas.add(mensagem_id)

        # Incrementa o contador de mensagens de busca
        if metodo in self.contadores_busca:
            self.contadores_busca[metodo] += 1

        if metodo == 'FL':
            mensagem = {
                'chave': chave,
                'metodo': metodo,
                'origem': origem,
                'ttl': ttl,
                'seq_no': seq_no,
                'hop': hop,
                'visitados': request.get('visitados', [])
            }
            resultado, total_hop = buscas.flooding(mensagem)
        elif metodo == 'RW':
            ultimo_vizinho = request.get('ultimo_vizinho')
            mensagem = {
                'chave': chave,
                'metodo': metodo,
                'origem': origem,
                'ttl': ttl,
                'seq_no': seq_no,
                'hop': hop,
                'ultimo_vizinho': ultimo_vizinho
            }
            resultado,total_hop = buscas.random_walk(mensagem)
            
        elif metodo == 'BP':
            ultimo_vizinho = request.get('ultimo_vizinho')
            mensagem = {
                'chave': chave,
                'metodo': metodo,
                'origem': origem,
                'ttl': ttl,
                'seq_no': seq_no,
                'hop': hop,
                'ultimo_vizinho': ultimo_vizinho,

            }
            resultado,total_hop = buscas.busca_em_profundidade(mensagem)
        else:
            resultado = "Método de busca desconhecido"

        resposta_json = json.dumps(resultado)
        peer_socket.send(resposta_json.encode())

        self.limpa_mensagens_vistas()  # Limpa a lista de mensagens vistas após cada busca

    # Envia mensagem de um peer para outro e retorna uma resposta
    def envia_mensagem(self, peer_socket, mensagem):
        try:
            peer_socket.send(mensagem.encode())
            resposta = peer_socket.recv(4096).decode()
            return resposta
        except:
            return

    # Limpa as mensagens vistas
    def limpa_mensagens_vistas(self):
        self.mensagens_vistas.clear()
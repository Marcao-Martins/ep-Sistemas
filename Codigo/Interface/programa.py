import sys
import os
import statistics
import time
import threading

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Grafo.grafo import Grafo  # Ajuste conforme necessário
from Grafo.buscas import Buscas
from peer import Peer


class Interface:
    def __init__(self, endereco, porta, arquivo_vizinhos=None, arquivo_chave_valor=None):
        self.running = True
        self.peer = Peer(endereco, porta) # Instanciando a classe Peer
        self.buscas = Buscas(self.peer)
        
        if arquivo_vizinhos:
            self.peer.load_neighbors(arquivo_vizinhos)
        if arquivo_chave_valor:
            self.peer.load_key_value_pairs(arquivo_chave_valor)
        
    def run(self):
        while self.running:
            self.show_menu()
            choice = input("Digite a opção desejada: ").strip()
            self.handle_choice(choice)

    def show_menu(self):
        print("\nEscolha o comando")
        print("[0] Listar vizinhos")
        print("[1] HELLO")
        print("[2] SEARCH (flooding)")
        print("[3] SEARCH (random walk)")
        print("[4] SEARCH (busca em profundidade)")
        print("[5] Estatísticas")
        print("[6] Alterar valor padrão de TTL")
        print("[9] Sair\n")

    def exit_program(self):
        print("Saindo...")
        self.peer.remove_vizinhos()
        self.running = False
        
    def handle_choice(self, choice):
        if choice == '0':
            self.list_neighbors()
        elif choice == '1':
            self.send_hello()
        elif choice == '2':
            self.search_flooding()
        elif choice == '3':
            self.search_random_walk()
        elif choice == '4':
            self.search_dfs()
        elif choice == '5':
            self.show_statistics()
        elif choice == '6':
            self.change_ttl()
        elif choice == '9':
            self.exit_program()
        else:
            print("Opção inválida. Tente novamente.")

    def list_neighbors(self):
        print(f"Há {len(self.peer.vizinhos)} vizinhos na tabela:")
        for i, vizinho in enumerate(self.peer.vizinhos):
            print(f"[{i}] {vizinho}")

    def send_hello(self):
        self.list_neighbors()
        choice = int(input("Escolha o vizinho para enviar HELLO: ").strip())
        if 0 <= choice < len(self.peer.vizinhos):
            vizinho_str = self.peer.vizinhos[choice]
            endereco, porta = vizinho_str.split(':')
            porta = int(porta)
            self.peer.handle_hello(endereco, porta, 'MENU HELLO')
        else:
            print("Opção inválida. Tente novamente.")

    def search_flooding(self):
        chave = input("Digite a chave a ser buscada: ").strip()
        mensagem = {
            'chave': chave,
            'origem': f"{self.peer.endereco}:{self.peer.porta}",
            'ttl': self.peer.ttl_padrao,
            'seq_no': 1,
            'metodo': 'FL',
            'visitados': set(),
            'hop' : 1
        }
        resultado,total_hop = self.buscas.flooding(mensagem)
        print(resultado)
        print(f"HOPS totais até a mensagem: {total_hop}")
        return total_hop

    def search_random_walk(self):
        chave = input("Digite a chave a ser buscada: ").strip()
        mensagem = {
            'chave': chave,
            'origem': f"{self.peer.endereco}:{self.peer.porta}",
            'ttl': self.peer.ttl_padrao,
            'seq_no': 1,
            'metodo': 'RW',
            'ultimo_vizinho': None,
            'hop' : 1
        }
        resultado,total_hop = self.buscas.random_walk(mensagem)
        print(resultado)
        return total_hop

    def search_dfs(self):
        chave = input("Digite a chave a ser buscada: ").strip()
        mensagem = {
            'chave': chave,
            'origem': f"{self.peer.endereco}:{self.peer.porta}",
            'ttl': self.peer.ttl_padrao,
            'seq_no': 1,
            'metodo': 'BP',
            'ultimo_vizinho': None,
            'hop' : 1
        }
        resultado,total_hop = self.buscas.busca_em_profundidade(mensagem)
        print(resultado)
        return total_hop

    def show_statistics(self):
        chave = input("Digite a chave a ser buscada: ").strip()

        
        print(f'Total de mensagens de flooding vistas: {self.peer.contadores_busca['FL']}')
        print(f'Total de mensagens de random walk vistas: {self.peer.contadores_busca['RW']}')
        print(f'Total de mensagens de busca em profundidade vistas: {self.peer.contadores_busca['BP']}')
        # Listas para armazenar o número de saltos para cada método de busca
        hops_flooding = []
        hops_random_walk = []
        hops_busca_profundidade = []

        # Executar cada método de busca 5 vezes
        for _ in range(5):
            # Flooding
            mensagem = {
                'chave': chave,
                'origem': f"{self.peer.endereco}:{self.peer.porta}",
                'ttl': self.peer.ttl_padrao,
                'seq_no': 1,
                'metodo': 'FL',
                'visitados': set(),
                'hop' : 1
            }
            resultado, total_hop = self.buscas.flooding(mensagem)
            hops_flooding.append(total_hop)

            # Random Walk
            mensagem = {
                'chave': chave,
                'origem': f"{self.peer.endereco}:{self.peer.porta}",
                'ttl': self.peer.ttl_padrao,
                'seq_no': 1,
                'metodo': 'RW',
                'ultimo_vizinho': None,
                'hop' : 1
            }
            resultado, total_hop = self.buscas.random_walk(mensagem)
            hops_random_walk.append(total_hop)
            
            # Busca em Profundidade
            mensagem = {
                'chave': chave,
                'origem': f"{self.peer.endereco}:{self.peer.porta}",
                'ttl': self.peer.ttl_padrao,
                'seq_no': 1,
                'metodo': 'BP',
                'ultimo_vizinho': None,
                'hop' : 1
            }
            resultado, total_hop = self.buscas.busca_em_profundidade(mensagem)
            hops_busca_profundidade.append(total_hop)

        # Calcular média e desvio padrão
        media_flooding = statistics.mean(hops_flooding)
        desvio_flooding = statistics.stdev(hops_flooding)

        media_random_walk = statistics.mean(hops_random_walk)
        desvio_random_walk = statistics.stdev(hops_random_walk)

        media_busca_profundidade = statistics.mean(hops_busca_profundidade)
        desvio_busca_profundidade = statistics.stdev(hops_busca_profundidade)

        # Imprimir os resultados
        print(f"Media de saltos ate encontrar destino por flooding: {media_flooding}")
        print(f"Desvio padrao de saltos ate encontrar destino por flooding: {desvio_flooding}")
        print(f"Media de saltos ate encontrar destino por random walk: {media_random_walk}")
        print(f"Desvio padrao de saltos ate encontrar destino por random walk: {desvio_random_walk}")
        print(f"Media de saltos ate encontrar destino por busca em profundidade: {media_busca_profundidade}")
        print(f"Desvio padrao de saltos ate encontrar destino por busca em profundidade: {desvio_busca_profundidade}")

    def change_ttl(self):
        novo_ttl = int(input("Digite o novo valor de TTL: ").strip())
        self.peer.ttl_padrao = novo_ttl
        print(f"Novo TTL definido para: {novo_ttl}")

if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 5:
        print("Algo deu errado! Inicie: python programa.py <endereço>:<porta> [<arquivo_vizinhos>] [<arquivo_pares_chave_valor>]")
        sys.exit(1)

    endereco, porta = sys.argv[1].split(':')
    arquivo_vizinhos = sys.argv[2] if len(sys.argv) > 2 else None
    arquivo_chave_valor = sys.argv[3] if len(sys.argv) > 3 else None

    seq_no = 1
    interface = Interface(endereco, int(porta), arquivo_vizinhos, arquivo_chave_valor)
    interface.run()
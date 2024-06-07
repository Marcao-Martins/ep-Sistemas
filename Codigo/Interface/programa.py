import sys
import os
import time
import threading

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Grafo.grafo import Grafo  # Ajuste conforme necessário
from Grafo.buscas import Buscas

class Interface:
    def __init__(self, endereco, porta, arquivo_vizinhos=None, arquivo_chave_valor=None):
        self.running = True
        self.grafo = Grafo()  # Inicializar o grafo
        self.buscas = Buscas(self.grafo, endereco, porta, arquivo_vizinhos, arquivo_chave_valor)
        
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
        print("[9] Sair")

    def exit_program(self):
        print("Saindo...")
        # tem que enviar um 'BYE' aqui
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
        print("Listando vizinhos:")
        for i, vizinho in enumerate(self.buscas.peer.vizinhos):
            print(f"[{i}] {vizinho}")

    def send_hello(self):
        self.list_neighbors()
        choice = int(input("Escolha o vizinho para enviar HELLO: ").strip())
        if 0 <= choice < len(self.buscas.peer.vizinhos):
            vizinho_socket = self.buscas.peer.vizinhos[choice]
            self.buscas.peer.envia_mensagem(vizinho_socket, {'type': 'HELLO'})
        else:
            print("Opção inválida. Tente novamente.")

    def search_flooding(self):
        chave = input("Digite a chave a ser buscada: ").strip()
        mensagem = {
            'chave': chave,
            'origem': f"{self.buscas.peer.endereco}:{self.buscas.peer.porta}",
            'ttl': self.buscas.peer.ttl_padrao,
            'seq_no': 1,
            'metodo': 'FLOODING',
            'visitados': set()
        }
        resultado = self.buscas.flooding(mensagem)
        print(resultado)

    def search_random_walk(self):
        chave = input("Digite a chave a ser buscada: ").strip()
        mensagem = {
            'chave': chave,
            'origem': f"{self.buscas.peer.endereco}:{self.buscas.peer.porta}",
            'ttl': self.buscas.peer.ttl_padrao,
            'seq_no': 1,
            'metodo': 'RANDOM_WALK'
        }
        resultado = self.buscas.random_walk(mensagem)
        print(resultado)

    def search_dfs(self):
        chave = input("Digite a chave a ser buscada: ").strip()
        mensagem = {
            'chave': chave,
            'origem': f"{self.buscas.peer.endereco}:{self.buscas.peer.porta}",
            'ttl': self.buscas.peer.ttl_padrao,
            'seq_no': 1,
            'metodo': 'DFS',
            'visitados': set()
        }
        resultado = self.buscas.busca_em_profundidade(mensagem)
        print(resultado)

    def show_statistics(self):
        print("Estatísticas: Em construção")

    def change_ttl(self):
        novo_ttl = int(input("Digite o novo valor de TTL: ").strip())
        self.buscas.peer.ttl_padrao = novo_ttl
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

    """
        from Codigo.peer import Peer
    from Codigo.conexao import inicia_servidor, conecta_peer
    import threading
    from Codigo.Grafo.buscas import flooding, random_walk, busca_em_profundidade

    def main():
        if len(sys.argv) < 2:
            print("Algo deu errado! Inicie: python main.py <endereço>:<porta> [<arquivo_vizinhos>] [<arquivo_pares_chave_valor>]")
            sys.exit(1)
        
        # Configurações do peer
        endereco_porta = sys.argv[1]
        endereco, porta = endereco_porta.split(':')
        porta = int(porta)

        peer = Peer(endereco, porta)
        inicia_servidor(peer)


        # TODO: rever essa parte aqui, não sei se é isso mesmo de numero de argumentos
        if len(sys.argv) > 2:
            carrega_vizinhos(peer, sys.argv[2])

        if len(sys.argv) > 3:
            carrega_chave_valor(peer, sys.argv[3])
        
        while True:
            print("\nMenu:")
            print("[0] Listar vizinhos")
            print("[1] HELLO")
            print("[2] SEARCH (flooding)")
            print("[3] SEARCH (random walk)")
            print("[4] SEARCH (busca em profundidade)")
            print("[5] Estatisticas")
            print("[6] Alterar valor padrao de TTL")
            print("[9] Sair")

            opcao = input("Escolha uma opção: ")

            if opcao == '0': # lista vizinhos
                vizinhos = peer.listar_vizinhos(peer)
                print("Vizinhos conectados:", vizinhos)
            elif opcao == '1': # TODO: arrumar isso aqui pra ele 1. Contar quantos vizinhos tem 2. Associar cada um a cada numero 3. Permitir que o usuário escolha um para listar
                vizinhos = peer.listar_vizinhos(peer)
                print("Há N vizinhos na tabela:", vizinhos)
                num_vizinho = input('Escolha o vizinho: ')
            # Onde que o self entra?
            elif opcao == '2':
                chave = input("Chave: ")
                ttl = int(input("TTL: "))
                flooding({'Tipo': 'SEARCH', 'origem': (peer.endereco, peer.porta), 'key': chave, 'metodo': 'FLOODING', 'ttl': ttl, 'seq_no': 1, 'visitados': None}, None)
            elif opcao == '3':
                chave = input("Chave: ")
                ttl = int(input("TTL: "))
                random_walk({'Tipo': 'SEARCH', 'origem': (peer.endereco, peer.porta), 'key': chave, 'metodo': 'RANDOM_WALK', 'ttl': ttl, 'seq_no': 1, 'ultimo_vizinho': None}, None)
            elif opcao == '4':
                chave = input("Chave: ")
                ttl = int(input("TTL: "))
                peer.handle_request({'Tipo': 'SEARCH', 'origem': (peer.endereco, peer.porta), 'key': chave, 'metodo': 'DFS', 'ttl': ttl, 'seq_no': 1, 'visitados': None}, None)
            elif opcao == '5':
                # estatisticas
            elif opcao == '6':
                # alterar valor padrão de TTL
            elif opcao == '9': # sair
                print("Saindo...")
                break
            else:
                print("Opção inválida. Tente novamente.")


    if __name__ == '__main__':
        main()

    """
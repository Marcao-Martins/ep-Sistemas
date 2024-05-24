from Codigo.peer import Peer
from Codigo.conexao import inicia_servidor, conecta_peer
import threading

# Carrega vizinhos de um Peer a partir de um txt - OK
def carrega_vizinhos(peer, filename):
    with open(filename, 'r') as file:
        for line in file:
            endereco_vizinho, porta_vizinho = line.strip().split(':')
            print(f'Tentando adicionar vizinho {endereco_vizinho}:{porta_vizinho}')
            conecta_peer(peer, endereco_vizinho, int(porta_vizinho))

# Carrega pares chave-valor de um txt e armazena no array "chave_valor" de um Peer - OK
def carrega_chave_valor(peer, filename):
    with open(filename, 'r') as file:
        for line in file:
            chave, valor = line.strip().split(' ')
            peer.armazena_valor(chave, valor)

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
            print("Há n vizinhos na tabela:", vizinhos)
            num_vizinho = input('Escolha o vizinho: ')
        elif opcao == '2':
            chave = input("Chave: ")
            peer.handle_request({'type': 'SEARCH', 'key': chave, 'method': 'FLOODING', 'origin': (peer.endereco, peer.porta)}, None)
        elif opcao == '3':
            chave = input("Chave: ")
            steps = int(input("Passos: "))
            peer.handle_request({'type': 'SEARCH', 'key': chave, 'method': 'RANDOM_WALK', 'origin': (peer.endereco, peer.porta), 'steps': steps}, None)
        elif opcao == '4':
            chave = input("Chave: ")
            peer.handle_request({'type': 'SEARCH', 'key': chave, 'method': 'DFS', 'origin': (peer.endereco, peer.porta), 'visited': []}, None)
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

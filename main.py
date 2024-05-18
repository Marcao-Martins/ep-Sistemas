from peer import Peer
from conexao import start_server, connect_to_peer
import threading

def main():
    # Configurações do peer
    host = 'localhost'
    port = 5000
    peer = Peer(host, port)
    
    # Iniciar o servidor
    threading.Thread(target=start_server, args=(peer,)).start()

    # Conectar a outro peer (exemplo)
    connect_to_peer(peer, 'localhost', 5001)

    # Exemplo de armazenamento e busca
    peer.store_data('example_key', 'example_value')
    
    # Métodos de busca
    peer.search_key_flooding('example_key', (peer.host, peer.port))
    # peer.search_key_random_walk('example_key', (peer.host, peer.port))
    # peer.search_key_dfs('example_key', (peer.host, peer.port))

if __name__ == '__main__':
    main()

import socket
import threading 

# Inicia o servidor para um peer específico
def inicia_servidor(peer):
    peer.inicia_servidor()

# Conecta um peer a outro peer
def conecta_peer(peer, endereco_peer, porta_peer):
    try:
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_socket.connect((endereco_peer, porta_peer))
        peer.peers.append(peer_socket)
        threading.Thread(target=peer.handle_peer, args=(peer_socket,)).start()
        print(f'Connected to peer {endereco_peer}:{porta_peer}')
        
    except Exception as e:
        print(f'Failed to connect to peer {endereco_peer}:{porta_peer} - {e}')
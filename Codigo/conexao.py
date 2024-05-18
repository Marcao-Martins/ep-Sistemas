import socket
import threading 

# Inicia o servidor para um peer específico
def start_server(peer):
    peer.start_server()

# Conecta um peer a outro peer
def connect_to_peer(peer, peer_host, peer_port):
    try:
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_socket.connect((peer_host, peer_port))
        peer.peers.append(peer_socket)
        threading.Thread(target=peer.handle_peer, args=(peer_socket,)).start()
        print(f'Connected to peer {peer_host}:{peer_port}')
    except Exception as e:
        print(f'Failed to connect to peer {peer_host}:{peer_port} - {e}')
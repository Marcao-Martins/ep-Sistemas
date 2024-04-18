from socket import *

class Server:
    def __init__(self, host, port):
        self.HOST = host
        self.PORT = port

    def run(self):
        with socket(AF_INET, SOCK_STREAM) as s:
            s.bind((self.HOST, self.PORT))
            s.listen(1)
            (conn, addr) = s.accept()  # returns new socket and addr. client
            while True:  # forever
                data = conn.recv(1024)  # receive data from client
                if not data:
                    break  # stop if client stopped
                conn.send(data + b"*")  # return sent data plus an "*"
            conn.close()  # close the connection

if __name__ == "__main__":
    server = Server('localhost', 12345)
    server.run()


## TESTE ISSO É UM CÓDIGO TESTE
import sys
from socket import *

class Node:
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.neighbors = set()

    def load_neighbors(self, filename):
        try:
            with open(filename, 'r') as f:
                for line in f:
                    neighbor_address, neighbor_port = line.strip().split(':')
                    self.neighbors.add((neighbor_address, int(neighbor_port)))
        except FileNotFoundError:
            print("Arquivo de vizinhos não encontrado.")

    def load_key_value_pairs(self, filename):
        # Implemente carregamento de pares chave-valor
        pass

    def run(self):
        with socket(AF_INET, SOCK_STREAM) as s:
            s.bind((self.address, self.port))
            s.listen(5)
            print(f"Node running on {self.address}:{self.port}")
            while True:
                conn, addr = s.accept()
                print(f"Connected to {addr}")
                # Implemente a lógica de comunicação aqui

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: ./ep_distsys <endereco>:<porta> [vizinhos.txt] [lista_chave_valor.txt]")
        sys.exit(1)

    address, port = sys.argv[1].split(':')
    node = Node(address, int(port))

    if len(sys.argv) >= 3:
        node.load_neighbors(sys.argv[2])
    
    if len(sys.argv) >= 4:
        node.load_key_value_pairs(sys.argv[3])

    node.run()

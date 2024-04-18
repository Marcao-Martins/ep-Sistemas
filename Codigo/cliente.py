from socket import *

class Client:
    def __init__(self, host, port):
        self.HOST = host
        self.PORT = port

    def run(self):
        with socket(AF_INET, SOCK_STREAM) as s:
            s.connect((self.HOST, self.PORT))  # connect to server (block until accepted)
            s.send(b"Hello, world")  # send same data
            data = s.recv(1024)  # receive the response
            print(data)  # print what you received
            s.send(b"")  # tell the server to close

if __name__ == "__main__":
    client = Client('localhost', 12345)
    client.run()
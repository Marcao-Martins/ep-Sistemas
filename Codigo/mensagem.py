class Message:
    sequence_number = 0

    def __init__(self, origin, ttl, operacao, argumentos=None):
        self.origin = origin
        self.seqno = Message.sequence_number + 1
        Message.sequence_number += 1
        self.ttl = ttl
        self.operacao = operacao
        self.argumentos = argumentos
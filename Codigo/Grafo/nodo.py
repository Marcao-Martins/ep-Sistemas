class Nodo:
    def __init__(self, endereco, porta):
        self.endereco = endereco
        self.porta = porta
        self.identificador = f"{endereco}:{porta}"
        self.vizinhos = set()  # Conjunto de identificadores de vizinhos (endereço:porta)
        self.pares_chave_valor = {}  # Dicionário para armazenar pares chave-valor

    def adicionar_vizinho(self, vizinho):
        """Adiciona um vizinho ao conjunto de vizinhos do nodo."""
        self.vizinhos.add(vizinho)

    def adiciona_par_chave_valor(self, chave, valor):
        """Adiciona ou atualiza um par chave-valor no nodo."""
        self.pares_chave_valor[chave] = valor

    def obtem_valor(self, chave):
        """Obtém o valor para uma chave especificada, se presente."""
        return self.pares_chave_valor.get(chave)
    
    def busca_local(self, chave):
        """Busca local por uma chave e retorna o valor se encontrado."""
        return self.pares_chave_valor.get(chave)

    def __str__(self):
        """Retorna uma representação em string do nodo, incluindo seu identificador e vizinhos."""
        vizinhos_str = "\n  ".join(self.vizinhos)
        return f"{self.identificador} com {len(self.vizinhos)} vizinhos:\n  {vizinhos_str}"

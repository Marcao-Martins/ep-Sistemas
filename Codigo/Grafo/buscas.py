import random

class Buscas:
    def __init__(self, grafo):
        self.grafo = grafo

# TODO: pegar os argumentos dessa função pra colocar em uma mensagem e aí a partir dela pegar as infos
    def flooding(self, origem, chave, ttl=100, seq_no=1, visitados=None):
        if visitados is None:
            visitados = set()
        nodo_origem = self.grafo.obtem_nodo(*origem.split(':'))
        resultado = nodo_origem.busca_local(chave)
        if resultado:
            return resultado
        if ttl > 0:
            visitados.add(origem)
            for vizinho in nodo_origem.vizinhos:
                if vizinho not in visitados:
                    resultado = self.flooding(vizinho, chave, ttl-1, seq_no+1, visitados)
                    if resultado:
                        return resultado
        return "Chave não encontrada"

    
    def random_walk(self, origem, chave, ttl=100, seq_no=1, ultimo_vizinho=None):
        nodo_origem = self.grafo.obtem_nodo(*origem.split(':'))
        resultado = nodo_origem.busca_local(chave)
        if resultado:
            return f"Chave encontrada: {resultado}"

        if ttl <= 0 or not nodo_origem.vizinhos:
            return "Chave não encontrada"

        # Seleciona um vizinho aleatoriamente, excluindo o último vizinho se possível
        vizinhos_possiveis = list(nodo_origem.vizinhos - {ultimo_vizinho}) if ultimo_vizinho else list(nodo_origem.vizinhos)
        if not vizinhos_possiveis:
            vizinhos_possiveis = list(nodo_origem.vizinhos)  # Se não há outra opção, permite voltar para o último vizinho

        vizinho_escolhido = random.choice(vizinhos_possiveis)
        return self.random_walk(vizinho_escolhido, chave, ttl-1, seq_no+1, origem)
    
    
    def busca_em_profundidade(self, origem, chave, ttl=100, seq_no=1, visitados=None):
        if visitados is None:
            visitados = set()
        nodo_origem = self.grafo.obtem_nodo(*origem.split(':'))
        resultado = nodo_origem.busca_local(chave)
        if resultado:
            return resultado
        if ttl > 0:
            visitados.add(origem)
            for vizinho in nodo_origem.vizinhos:
                if vizinho not in visitados:
                    resultado = self.busca_em_profundidade(vizinho, chave, ttl-1, seq_no+1, visitados)
                    if resultado:
                        return resultado
        return "Chave não encontrada"

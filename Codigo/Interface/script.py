import subprocess
import time
import os

def abrir_terminais():
    endereco = "127.0.0.1"
    base_porta = 5000
    vizinhos = [f"{i}.txt" for i in range(1, 11)]
    chaves_valores = [f"cv{i}.txt" for i in range(1, 11)]
    diretorio = r"E:\ep-Sistemas\Codigo\Interface"

    for i in range(10):
        porta = base_porta + i + 1
        vizinho = vizinhos[i]
        chave_valor = chaves_valores[i]
        comando = f'start cmd /k "cd /d {diretorio} && python programa.py {endereco}:{porta} {vizinho} {chave_valor}"'
        subprocess.Popen(comando, shell=True)
        time.sleep(3)  # Aguarda 1 segundo entre cada abertura para garantir que os processos sejam iniciados corretamente

if __name__ == "__main__":
    abrir_terminais()

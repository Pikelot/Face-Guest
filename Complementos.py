import os
import datetime
import time
def limpar_tela():
    os.system('cls')

def data():
    # Retorna a data atual no formato dd/mm/aaaa
    return datetime.datetime.now().strftime("%d%m%Y-%H%M%S")

def wait(tempo):
    # Pausa a execução do programa por 2 segundos
    time.sleep(tempo)

print(data())

import os
import datetime
def limpar_tela():
    os.system('cls')

def data():
    # Retorna a data atual no formato dd/mm/aaaa
    return datetime.datetime.now().strftime("%d/%m/%Y")

print(data())
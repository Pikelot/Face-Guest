import face_recognition
import numpy as np
import os
import Complementos as comp
from itertools import combinations

def gerar_hash(caminho, ação):

    print(f"Facial.py - Lendo imagem e gerando hash facial: {caminho}")

    #Verifico se a hash vai ser salva nas hashes padrões ou na pasta da hash de verificação.
    if ação == 0:
        pasta = "./Hashes/"
    elif ação == 1:
        pasta = "./Hash_comp/"

    imagem = face_recognition.load_image_file(caminho)
    encodings = face_recognition.face_encodings(imagem)

    comp.remover(caminho)

    if len(encodings) > 0:

        encoding = encodings[0]

        nome_hash = comp.data() + ".txt"

        caminho_hash = f"{pasta}{nome_hash}"

        with open(f"{caminho_hash}", "w") as arquivo_hash:
            arquivo_hash.write(",".join(map(str, encoding)))

        print(f"Facial.py - Hash salvo em: {caminho_hash}")
        print("Facial.py - Hash gerado com sucesso!")

        return True, caminho_hash

    else:
        print("Facial.py - Nenhum rosto detectado na imagem.")
        return False, None

def carregar_hash(caminho):

    with open(caminho, "r") as arquivo:

        valores = arquivo.read().split(",")

    return np.array([float(valor) for valor in valores])

def comparar_hashes(hash_comp):
    hashes = []

    hash_teste = carregar_hash(hash_comp)

    for arquivo in os.listdir("./Hashes"):
        hash = carregar_hash(f"./Hashes/{arquivo}")

        resultado = face_recognition.compare_faces(
            [hash],
            hash_teste
        )

        if resultado[0]:
            hashes.append(arquivo)

    if hashes == []:
        return "Nenhum rosto encontrado."

    else:
        
        for hash in hashes:
            resultado += str(hash)

        else:
            resultado = ", ".join(hashes)

            return f"Foram encontrados hashes nos arquivos: {resultado}"
    
resultado_hash = comparar_hashes("./Hash_comp/teste.txt")
print("Resultado do teste com o arquivo teste.txt:", resultado_hash)
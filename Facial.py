import face_recognition
import numpy as np
import os
import Complementos as comp
from itertools import combinations

def gerar_encoding(caminho, ação):

    print(f"Facial.py - Lendo imagem e gerando encoding facial: {caminho}")

    #Verifico se a encoding vai ser salva nas encoding padrões ou na pasta da encoding de verificação.
    if ação == 0:
        pasta = "./encodings/"
    elif ação == 1:
        pasta = "./encoding_comp/"

    imagem = face_recognition.load_image_file(caminho)
    encodings = face_recognition.face_encodings(imagem)

    comp.remover(caminho)

    if len(encodings) > 0:

        encoding = encodings[0]

        nome_encoding = comp.data() + ".txt"

        caminho_encoding = f"{pasta}{nome_encoding}"

        with open(f"{caminho_encoding}", "w") as arquivo_encoding:
            arquivo_encoding.write(",".join(map(str, encoding)))

        print(f"Facial.py - encoding salvo em: {caminho_encoding}")
        print("Facial.py - encoding gerado com sucesso!")

        return True, caminho_encoding

    else:
        print("Facial.py - Nenhum rosto detectado na imagem.")
        return False, None

def carregar_encoding(caminho):

    with open(caminho, "r") as arquivo:

        valores = arquivo.read().split(",")

    return np.array([float(valor) for valor in valores])

def comparar_encodings(encoding_comp):
    encodings = []

    encoding_teste = carregar_encoding(encoding_comp)

    for arquivo in os.listdir("./Encodings"):
        encoding = carregar_encoding(f"./Encodings/{arquivo}")

        resultado = face_recognition.compare_faces(
            [encoding],
            encoding_teste
        )

        if resultado[0]:
            encodings.append(arquivo)

    if encodings == []:
        return "Nenhum rosto encontrado."

    else:
        
        for encoding in encodings:
            resultado += str(encoding) + ", "

        else:
            resultado = ", ".join(encodings)

            return f"Foram encontrados encodings nos arquivos: {resultado}"
    
resultado_encoding = comparar_encodings("./encoding_comp/teste.txt")
print("Resultado do teste com o arquivo teste.txt:", resultado_encoding)
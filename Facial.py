import face_recognition
import os
from itertools import combinations

from numpy import rint

caminho = r"C:\Users\joao.victor\Documents\Face-Guest\Face-Guest\Faciais\foto1.jpg"

def gerar_hash (caminho):

    #Lê a imagem e gera o hash correspondente usando a biblioteca face_recognition
    
    #Leitura da imagem
    print("Lendo imagem e gerando hash facial...")
    imagem = face_recognition.load_image_file(caminho)

    #Geração do hash facial
    hash = face_recognition.face_encodings(imagem)

    #Retorno dos resultados
    if len(hash) > 0:
        return hash[0]
        print("Retornando hash facial gerado com sucesso!")
    else:
        return hash
        print("Retornando hash facial gerado com sucesso!")

def comparar_hashes(hash1, hash2):

    # Compara os dois hashes e retorna True se forem da mesma pessoa, False caso contrário

    # Compara hash1 com hash2 usando compare_faces
    resultado = face_recognition.compare_faces([hash1], hash2)

    #Retorna resultado em booleano
    return resultado[0]
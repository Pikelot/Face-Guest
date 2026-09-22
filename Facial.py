import face_recognition
import numpy as np
import Complementos as comp
from itertools import combinations

#caminho = r"C:\Users\joao.victor\Documents\Face-Guest\Face-Guest\Faciais\foto1.jpg"

def gerar_hash (caminho):

    #Lê a imagem e gera o hash correspondente usando a biblioteca face_recognition
    
    print(f"Facial.py - Lendo imagem e gerando hash facial: {caminho}")
    imagem = face_recognition.load_image_file(caminho)

    #Geração do hash facial
    hash = face_recognition.face_encodings(imagem)

    comp.remover(caminho)

    #Retorno dos resultados
    if len(hash) > 0:
        nome_hash = comp.data() + ".txt"
                    
        with open(f"./Hashes/{nome_hash}", "w") as arquivo_hash:
            arquivo_hash.write(str(hash))
            print(f"Facial.py - Hash salvo em: ./Hashes/{nome_hash}")

        print(f"Facial.py - Hash gerado com sucesso!")
        return True
    
    else:
        print(f"Facial.py - Nenhum rosto detectado na imagem.")
        return False

def carregar_encoding(caminho_arquivo):
    with open(caminho_arquivo, 'r') as f:
        conteudo = f.read()
    
    # Remove caracteres do texto como '[array(', ']', ')'
    limpo = conteudo.replace('[array(', '').replace('array(', '').replace(']', '').replace(')', '').replace('[', '')
    
    # Converte os números em um array de floats do NumPy
    return np.fromstring(limpo, sep=',') if ',' in limpo else np.fromstring(limpo, sep=' ')

def comparar_hashes(caminho_hash1, caminho_hash2):
    # Carrega os vetores numéricos de cada arquivo
    encoding1 = carregar_encoding(caminho_hash1)
    encoding2 = carregar_encoding(caminho_hash2)
    
    # Compara os dois encodings
    resultado = face_recognition.compare_faces([encoding1], encoding2)
    
    return bool(resultado[0])

print(comparar_hashes("./Hashes/21092026-112055.txt", "./Hashes/21092026-112238.txt"))
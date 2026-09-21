import face_recognition
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

def comparar_hashes(hash1, hash2):

    # Compara os dois hashes e retorna True se forem da mesma pessoa, False caso contrário

    # Compara hash1 com hash2 usando compare_faces
    resultado = face_recognition.compare_faces([hash1], hash2)

    #Retorna resultado em booleano
    return resultado[0]

#print(comparar_hashes("21092026-100707", "21092026-102709"))
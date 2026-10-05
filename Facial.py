import face_recognition
import DB_Chroma as chroma
import DB_SQL as sql
import Complementos as comp

#Propósito> Gera o encoding facial a partir da imagem capturada e salva no banco de dados #Retorno> True e ID da pessoa se sucesso, False e None se falha

def gerar_encoding(caminho):

    print(f"Facial.py - Lendo imagem e gerando encoding facial: {caminho}")

    #Caminho onde a imagem é salva
    imagem = face_recognition.load_image_file(caminho)

    #Encodings faciais encontrados na imagem
    encodings = face_recognition.face_encodings(imagem)

    #Removendo a imagem após gerar o encoding
    comp.remover(caminho)

    #Se enconding for maior que 0 salvo o encoding

    if len(encodings) > 0:

        encoding = encodings[0]

        pessoa_id = chroma.comparar_encoding(encoding)


        if pessoa_id is None:
            pessoa_id = sql.inserir_pessoa()
            chroma.adicionar_encoding(pessoa_id, encoding)
            print("Facial.py - encoding criado e salvo com sucesso!")
            return True, pessoa_id

        print(f"Facial.py - encoding criado salvo com o ID: {pessoa_id}")
        print("Facial.py - encoding gerado com sucesso!")

        return True, pessoa_id

    else:
        print("Facial.py - Nenhum rosto detectado na imagem.")
        return False, None

def gerar_encoding_comparação(caminho):

    print(f"Facial.py - Lendo imagem e gerando encoding facial: {caminho}")

    #Caminho onde a imagem é salva
    imagem = face_recognition.load_image_file(caminho)

    #Encodings faciais encontrados na imagem
    encodings = face_recognition.face_encodings(imagem)

    #Removendo a imagem após gerar o encoding
    comp.remover(caminho)

    #Se enconding for maior que 0 comparo o encoding com os encodings salvos no banco de dados

    if len(encodings) > 0:

        encoding = encodings[0]

        pessoa_id = chroma.comparar_encoding(encoding)

        if pessoa_id is not None:
            print(f"Facial.py - encoding encontrado com o ID: {pessoa_id}")
            print("Facial.py - encoding comparado com sucesso!")
            return True, pessoa_id
        else:
            print("Facial.py - Nenhum encoding correspondente encontrado.")
            return False, None

    else:
        print("Facial.py - Nenhum rosto detectado na imagem.")
        return False, None

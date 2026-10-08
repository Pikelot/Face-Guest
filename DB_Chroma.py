import chromadb

#Configuração do cliente ChromaDB

client = chromadb.PersistentClient(
    path="./chroma_db"
)

#Criação da coleção para armazenar os encodings faciais

collection = client.get_or_create_collection(
    name="face_encodings"
)

#Função para adicionar um encoding facial à coleção

def adicionar_encoding(pessoa_id, encoding):

    collection.add(
        ids=[str(pessoa_id)],
        embeddings=[encoding]
    )

#Função para comparar um encoding facial com os encodings armazenados na coleção e retornar o ID da pessoa correspondente

def comparar_encoding(encoding_comp):

    #Consulta a coleção para encontrar o encoding mais próximo do encoding fornecido
    results = collection.query(
        query_embeddings=[encoding_comp],
        n_results=1
    )

    #Verifica se algum resultado foi encontrado e se a distância é aceitável (menor que 0.6)
    if not results["ids"] or not results["ids"][0]:
        return None

    print("DB_Chroma.py - Resultado da comparação de encodings:", results)
    distancia = results["distances"][0][0]

    print("DB_Chroma.py - Distância:", distancia)

    if distancia > 0.35:
        return None

    return int(results["ids"][0][0])
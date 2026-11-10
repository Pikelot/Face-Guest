import math
import chromadb
 
#Configuração do cliente ChromaDB
 
client = chromadb.PersistentClient(
    path="./chroma_db"
)
 
#Criação da coleção para armazenar os encodings faciais
#A métrica padrão do Chroma é L2, que devolve a distância euclidiana AO QUADRADO
 
collection = client.get_or_create_collection(
    name="face_encodings"
)
 
#Limiar de distância euclidiana (calibrado no Experimento 1, Seção 5.1 do artigo)
 
LIMIAR = 0.49
 
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
 
    #Verifica se algum resultado foi encontrado
    if not results["ids"] or not results["ids"][0]:
        return None
 
    print("DB_Chroma.py - Resultado da comparação de encodings:", results)
 
    #O Chroma (L2) devolve a distância ao quadrado; a raiz dá a distância euclidiana normal
    distancia = math.sqrt(max(results["distances"][0][0], 0.0))
 
    print("DB_Chroma.py - Distância euclidiana:", distancia)
 
    #Aceita apenas se a distância euclidiana for menor ou igual ao limiar (0.49)
    if distancia > LIMIAR:
        return None
 
    return int(results["ids"][0][0])
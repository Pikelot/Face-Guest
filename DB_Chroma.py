import chromadb as chromadb

client = chromadb.Client()

def adicionar_encoding(encoding):

    collection = client.get_or_create_collection(name="face_encodings")

    collection.add(
        ids=["pessoa_123"],
        embeddings=[encoding]
    )

def comparar_encodings(encoding_comp):
    collection = client.get_or_create_collection(name="face_encodings")

    results = collection.query(
        query_embeddings=[encoding_comp],
        n_results=1
    )

    if results['ids'][0]:
        return f"Rosto encontrado: {results['ids'][0][0]}"
    else:
        return "Nenhum rosto encontrado."
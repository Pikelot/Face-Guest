from pathlib import Path
from itertools import combinations

import chromadb
import face_recognition

PASTA = Path(r"C:\Users\jao\Pictures\PESSOAS")
EXTENSOES = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

try:
    limite_distancia = float(
        input("Digite a distância máxima para considerar correspondência: ")
    )
    if limite_distancia < 0:
        raise ValueError
except ValueError:
    print("Digite um número válido, maior ou igual a zero.")
    raise SystemExit

if not PASTA.is_dir():
    print(f"A pasta não existe: {PASTA}")
    raise SystemExit

arquivos = sorted(
    arquivo
    for arquivo in PASTA.iterdir()
    if arquivo.is_file() and arquivo.suffix.lower() in EXTENSOES
)

if not arquivos:
    print(f"Nenhuma imagem encontrada em: {PASTA}")
    raise SystemExit

# Coleção temporária: os dados não são mantidos depois que o programa termina.
client = chromadb.Client()
collection = client.create_collection(
    name="encodings_temporarios",
    metadata={"hnsw:space": "l2"},
)

# Gera e armazena um encoding por imagem.
for arquivo in arquivos:
    try:
        imagem = face_recognition.load_image_file(str(arquivo))
        encodings = face_recognition.face_encodings(imagem)

        if not encodings:
            print(f"AVISO: nenhum rosto encontrado em {arquivo.name}; ignorada.")
            continue

        collection.add(
            ids=[str(arquivo.resolve())],
            embeddings=[encodings[0].tolist()],
            metadatas=[{"arquivo": arquivo.name}],
        )
        print(f"Encoding salvo: {arquivo.name}")

    except Exception as erro:
        print(f"AVISO: não foi possível processar {arquivo.name}: {erro}")

if collection.count() < 2:
    print("São necessárias pelo menos duas imagens com rostos para comparar.")
    raise SystemExit

# Consulta cada imagem e imprime cada par só uma vez.
ids = collection.get(include=["embeddings", "metadatas"])["ids"]

for id_imagem in ids:
    registro = collection.get(
        ids=[id_imagem],
        include=["embeddings", "metadatas"],
    )
    encoding = registro["embeddings"][0]
    nome_imagem = registro["metadatas"][0]["arquivo"]

    resultado = collection.query(
        query_embeddings=[encoding],
        n_results=collection.count(),
        include=["distances", "metadatas"],
    )

    for id_encontrado, metadados, distancia in zip(
        resultado["ids"][0],
        resultado["metadatas"][0],
        resultado["distances"][0],
    ):
        # Ignora a comparação da imagem consigo mesma e pares já impressos.
        if id_encontrado == id_imagem:
            continue
        if id_encontrado < id_imagem:
            continue

        corresponde = distancia <= limite_distancia
        status = "CORRESPONDEM" if corresponde else "NÃO CORRESPONDEM"

        print(
            f"{nome_imagem} x {metadados['arquivo']}: "
            f"distância = {distancia:.4f} -> {status}"
        )
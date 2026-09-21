import Executaveis.Facial as face
import Executaveis.Complementos as comp
from datetime import datetime
#print(time.time())

print("""Seja bem vindo ao Face-Guest""")

menu = True

while menu:

    comp.limpar_tela()

    # Menu simples
    print("""
    1 - Gerar hash facial (Para testes)
    2 - Comparar hashes faciais (Para testes)
    3 - Sair
    """)

    # Input de escolha
    escolha = input("#> Escolha uma opção: ")

    # Gerar hash facial
    if escolha == "1":

        comp.limpar_tela()
        
        hash = face.gerar_hash(".\Faciais\foto_teste.jp")
        with open(rf"C:\Users\Stancz1k\Documents\TCC\Face-Guest\Face-Guest\Hashes\{int(datetime.now().timestamp())}.txt", "w") as arquivo:
            arquivo.write(str(hash))

        print("Hash Facial: ", hash)
        input("Pressione Enter para continuar...")

    # Comparar hashes faciais
    if escolha == "2":

        comp.limpar_tela()

        # Captura nome das imagens
        caminho1 = input("#> Digite o nome da primeira imagem: ")
        caminho2 = input("#> Digite o nome da segunda imagem: ")

        # Captura caminho das imagens
        caminho_completo1 = rf"C:\Users\Stancz1k\Documents\TCC\Face-Guest\Face-Guest\Faciais\{caminho1}"
        caminho_completo2 = rf"C:\Users\Stancz1k\Documents\TCC\Face-Guest\Face-Guest\Faciais\{caminho2}"

        # Gerar hashes das imagens e compara
        hash1 = face.gerar_hash(caminho_completo1)
        hash2 = face.gerar_hash(caminho_completo2)

        # Compara os hashes e retorna resultado
        resultado = face.comparar_hashes(hash1, hash2)

        if resultado:
            print("✅ As imagens são da mesma pessoa!")
        else:
            print("❌ As imagens são de pessoas diferentes.")

        input("Pressione Enter para continuar...")

    # Sair do Programa
    if escolha == "3":

        comp.limpar_tela()
        
        print("Saindo do programa...")
        menu = False
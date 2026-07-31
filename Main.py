import Facial as face
import Complementos as comp

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

        # Captura caminho da imagem
        caminho = input("#> Digite o nome da imagem: ")
        caminho_completo = rf"c:\Users\joao.victor\Documents\Face-Guest\Face-Guest\Faciais\{caminho}"

        # Chama função gerar hash do módulo Facial
        hash = face.gerar_hash(caminho_completo)

        print("Hash Facial: ", hash)
        input("Pressione Enter para continuar...")

    # Comparar hashes faciais
    if escolha == "2":

        comp.limpar_tela()

        # Captura nome das imagens
        caminho1 = input("#> Digite o nome da primeira imagem: ")
        caminho2 = input("#> Digite o nome da segunda imagem: ")

        # Captura caminho das imagens
        caminho_completo1 = rf"c:\Users\joao.victor\Documents\Face-Guest\Face-Guest\Faciais\{caminho1}"
        caminho_completo2 = rf"c:\Users\joao.victor\Documents\Face-Guest\Face-Guest\Faciais\{caminho2}"

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
import sqlite3


def criar_tabela():
    conexao = sqlite3.connect('face_guest.db')
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pessoas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            ip TEXT,
            voucher TEXT
        )
    """)

    conexao.commit()
    conexao.close()

criar_tabela()

def inserir_pessoa(nome, ip, voucher):
    conexao = sqlite3.connect('face_guest.db')
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO pessoas (nome, ip, voucher)
        VALUES (?, ?, ?)
    """, (nome, ip, voucher))

    conexao.commit()
    conexao.close()

nome = input("Digite o nome da pessoa: ")
ip = input("Digite o IP da pessoa: ")
voucher = input("Digite o voucher da pessoa: ")

inserir_pessoa(nome, ip, voucher)

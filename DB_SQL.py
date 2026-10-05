import sqlite3

#Nomenclatura do banco

banco = "face_guest.db"

#Propósito> Função de conexão com o banco de dados SQLite #Retorno> Conexão estabelecida

def conectar():
    return sqlite3.connect(banco)

#Propósito> Criação das tabelas pessoas e conexoes #Retorno> Nenhum

def criar_tabela():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pessoas (
            id INTEGER PRIMARY KEY AUTOINCREMENT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conexoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pessoa_id INTEGER NOT NULL,
            ip TEXT NOT NULL,
            voucher TEXT NOT NULL,
            data_conexao DATETIME DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (pessoa_id)
                REFERENCES pessoas(id)
        )
    """)

    conexao.commit()
    conexao.close()

#Propósito> Insere o usuário e retorna ID #Retorno> ID da pessoa inserida #Retorno> Nenhum

def inserir_pessoa():

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO pessoas DEFAULT VALUES
    """)

    pessoa_id = cursor.lastrowid

    conexao.commit()
    conexao.close()

    return pessoa_id

#Propósito> Registra a conexão do usuário com o IP e voucher gerado #Retorno> Nenhum

def registrar_conexao(pessoa_id, ip, voucher):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO conexoes (pessoa_id, ip, voucher)
        VALUES (?, ?, ?)
    """, (pessoa_id, ip, voucher))

    conexao.commit()
    conexao.close()

#Propósito> Buscar conexões #Retorno> Lista de conexões

def buscar_conexoes(pessoa_id):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT ip, voucher, data_conexao
        FROM conexoes
        WHERE pessoa_id = ?
        ORDER BY data_conexao DESC
    """, (pessoa_id,))

    conexoes = cursor.fetchall()

    conexao.close()

    return conexoes
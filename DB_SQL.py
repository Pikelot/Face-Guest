import sqlite3
from contextlib import closing
from datetime import datetime
from zoneinfo import ZoneInfo

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
            mac TEXT NOT NULL,
            hostname TEXT NOT NULL,
            voucher TEXT NOT NULL,
            data_conexao TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            cpf TEXT NOT NULL,

            FOREIGN KEY (pessoa_id)
                REFERENCES pessoas(id)
        )
    """)

    # Atualiza bancos já existentes, criados antes da coluna CPF.
    cursor.execute("PRAGMA table_info(conexoes)")
    colunas_conexoes = {coluna[1] for coluna in cursor.fetchall()}
    if "cpf" not in colunas_conexoes:
        cursor.execute("ALTER TABLE conexoes ADD COLUMN cpf TEXT NOT NULL DEFAULT ''")

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

def registrar_conexao(pessoa_id, ip, voucher, hostname, mac, cpf):
    data_conexao = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # closing garante que a conexão seja liberada até quando o INSERT falhar.
    with closing(conectar()) as conexao:
        with conexao:
            conexao.execute("""
                INSERT INTO conexoes (pessoa_id, cpf, ip, voucher, hostname, mac, data_conexao)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (pessoa_id, cpf, ip, voucher, hostname, mac, data_conexao))

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

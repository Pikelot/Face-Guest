from flask import json
from pyunifi.controller import Controller

def Conectar():
    # Conexão e Autenticação
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)

    c = Controller(
        host=config['servidor'],
        username=config['usuario'],
        password=config['senha'],
        port=config['porta'],
        version=config['version'],
        site_id=config['site_id'],
        ssl_verify=config['ssl_verify']
    )
    return c

def Gerar_voucher(USER_ID):
    
    c = Conectar()
    vouchers = c.create_voucher(
        expire=60,       # 1 hora de validade
        number=1,            # Gerar 1 voucher
        quota=1,            # 1 = dispositivo único, 0 = multiuso
        note=USER_ID
    )

        # Retorna diretamente o código do voucher criado
    for v in vouchers:
        code_voucher = v.get("code")
        time_voucher = v.get("create_time")

    return code_voucher, time_voucher

def IP(voucher_code):

    c = Conectar()
    # Função para pegar o ip de conexão
    dispositivo = c._api_read("stat/guest", params={"voucher": voucher_code})

    #dados
    ip = dispositivo[0].get("ip")
    hostname = dispositivo[0].get("hostname")
    mac = dispositivo[0].get("mac")

    return ip, hostname, mac

# Por enquanto não tá funcionando, mas futuramente vai ser implementado, houve um problema, não sei se foi ocasionado por esta conexão.
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

def Gerar_voucher(c, user_id):
    vouchers = c.create_voucher(
        expire=60,
        number=1,
        quota=1,
        note=user_id,
    )
    voucher = vouchers[0]
    return voucher["code"], voucher["create_time"]


def IP(c, voucher_code):
    print("Controladora.py - Verificando dispositivos conectados com o voucher:", voucher_code)
    dispositivos = c._api_read("stat/guest", params={"voucher": voucher_code})
    print("Controladora.py - Dispositivos encontrados:", dispositivos)

    if not dispositivos:
        print("Controladora.py - Nenhum dispositivo encontrado.")
        return None

    dispositivo = dispositivos[0]
    ip = dispositivo.get("ip")
    hostname = dispositivo.get("hostname")
    mac = dispositivo.get("mac")

    if not all((ip, hostname, mac)):
        print("Controladora.py - Dispositivo encontrado, mas informações incompletas. Aguardando preenchimento...")
        return None

    return ip, hostname, mac




# Por enquanto não tá funcionando, mas futuramente vai ser implementado, houve um problema, não sei se foi ocasionado por esta conexão.

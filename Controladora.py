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

    if not dispositivos:
        print("Controladora.py - Nenhum dispositivo encontrado.")
        return None

    # stat/guest pode devolver o histórico inteiro; selecione o voucher atual.
    dispositivo = next(
        (
            item for item in dispositivos
            if item.get("voucher_code") == voucher_code
            and not item.get("expired", False)
        ),
        None,
    )
    if dispositivo is None:
        print("Controladora.py - Nenhum dispositivo ativo encontrado para este voucher.")
        return None

    ip = dispositivo.get("ip")
    hostname = dispositivo.get("hostname")
    mac = dispositivo.get("mac")

    # stat/guest pode registrar o voucher antes de preencher o IP.
    if mac and not ip:
        clientes_ativos = c._api_read("stat/sta")
        cliente = next(
            (
                item for item in clientes_ativos
                if (item.get("mac") or "").lower() == mac.lower()
            ),
            None,
        )
        if cliente:
            ip = cliente.get("ip")
            hostname = cliente.get("hostname") or hostname

    if not ip or not mac:
        print("Controladora.py - Voucher ativo encontrado, mas o IP ainda não está disponível.")
        return None

    return ip, hostname or mac, mac




# Por enquanto não tá funcionando, mas futuramente vai ser implementado, houve um problema, não sei se foi ocasionado por esta conexão.

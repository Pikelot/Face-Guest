from pyunifi.controller import Controller

#Conexão e Autenticação
c = Controller(
    host='',
    username=input('Digite seu usuário: '),
    password=input('Digite sua senha: '),
    port=8443,
    version='v5',       # Funciona para versões 5, 6 e 7 do UniFi Controller
    site_id='default',  # Nome do site (padrão: 'default')
    ssl_verify=False
)

def Gerar_voucher(USER_ID):
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
    # Função para pegar o ip de conexão
    dispositivo = c._api_read("stat/guest", params={"voucher": voucher_code})

    #dados
    ip = dispositivo[0].get("ip")
    hostname = dispositivo[0].get("hostname")
    mac = dispositivo[0].get("mac")

    return ip, hostname, mac

Gerar_voucher("teste")

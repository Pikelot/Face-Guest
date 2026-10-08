from pyunifi.controller import Controller

# 1. Conexão e Autenticação
c = Controller(
    host='',
    username=input('Digite seu nome de usuário: '),
    password=input('Digite sua senha: '),
    port=8443,
    version='v5',       # Funciona para versões 5, 6 e 7 do UniFi Controller
    site_id='default',  # Nome do site (padrão: 'default')
    ssl_verify=False
)
    
# 2. Gerar Voucher (Método Nativo)
vouchers = c.create_voucher(
    expire=1440,       # 24 horas de validade (1440 min)
    number=1,            # Gerar 1 voucher
    quota=1,            # 1 = dispositivo único, 0 = multiuso
    note=input('Digite a nota do voucher: ')
)

# Retorna diretamente o código do voucher criado
for v in vouchers:
    print(f"Voucher Gerado: {v.get('code')} | Criado em: {v.get('create_time')}")

print("-" * 40)

# 3. Listar Dispositivos (APs, Switches, Roteadores)
devices = c.get_aps()
for dev in devices:
    nome = dev.get('name') or dev.get('hostname') or 'Sem Nome'
    ip = dev.get('ip', 'N/A')
    mac = dev.get('mac', 'N/A')
    print(f"Dispositivo: {nome} | IP: {ip} | MAC: {mac}")


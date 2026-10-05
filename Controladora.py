import random

def Gerar_voucher():
    # Função para gerar um voucher único
    import string

    # Gera um código aleatório de 5 caracteres
    voucher = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    
    return voucher

def IP():
    # Função para gerar um ip de conexão
    
    ip_base = "192.168.0."
    ip_final = random.randint(1, 254)
    ip = ip_base + str(ip_final)

    return ip
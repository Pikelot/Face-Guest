def Gerar_voucher():
    # Função para gerar um voucher único
    import random
    import string

    # Gera um código aleatório de 5 caracteres
    voucher = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    
    return voucher
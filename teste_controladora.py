import Controladora as ctrl


conec = ctrl.Conectar()

conexão = ctrl.IP(conec, "93524-74941")

print(f"Conexão: {conexão[0]}, Hostname: {conexão[1]}, MAC: {conexão[2]}")
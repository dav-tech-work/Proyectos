import socket

def escanear_puertos(ip, puertos):
    print(f"Iniciando escaneo de puertos en {ip}...")
    for puerto in puertos:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((ip, puerto))

        if result == 0:
            print(f"Puerto {puerto} abierto ")
        else:
            print(f"Puerto {puerto} cerrado ")
        sock.close()

ip_objetivo = input("Ingrese la IP a escanear: ")
puertos_comunes = [21,22,23,25,53,80,110,135,139,443,445,1433,1521,3306,3389,5432,8080,8443]
escanear_puertos(ip_objetivo, puertos_comunes)
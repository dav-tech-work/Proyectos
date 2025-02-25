import socket
import subprocess
import platform
import datetime
import concurrent.futures

def get_local_ip():
    """Obtiene la IP local del equipo."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))  # Se conecta a un servidor externo para obtener la IP local
        ip = s.getsockname()[0]
        print(f"IP local detectada: {ip}")
        return ip
    except Exception:
        print("Error al obtener la IP local, usando 127.0.0.1")
        return "127.0.0.1"  # Retorna localhost en caso de error
    finally:
        s.close()

def ping_ip(ip):
    """Realiza un ping a la IP dada y retorna True si responde."""
    command = ['ping', '-c', '1', '-W', '0.5', ip] if platform.system().lower() != 'windows' else ['ping', '-n', '1', '-w', '500', ip]
    result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
    if result == 0:
        print(f"IP activa detectada: {ip}")  # Muestra en pantalla cada IP activa detectada
    return result == 0

def main():
    local_ip = input("Ingrese la IP local de la red (presione Enter para detectar automáticamente): ")
    if not local_ip:
        local_ip = get_local_ip()
    base = '.'.join(local_ip.split('.')[:3]) + '.'  # Extrae la parte base de la IP para escanear la red local
    ips_to_scan = [base + str(i) for i in range(1, 255)]  # Genera todas las IPs dentro de la subred /24
    
    print("Iniciando escaneo de IPs...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        # Ejecuta múltiples pings en paralelo para mejorar la velocidad de escaneo
        alive_ips = [ip for ip, result in zip(ips_to_scan, executor.map(ping_ip, ips_to_scan)) if result]
    
    print(f"Total de IPs activas encontradas: {len(alive_ips)}")
    if input("¿Desea guardar los resultados en un archivo? (s/n): ").lower() != "s":
        return
    resultado = input("El nombre del archivo para guardar: ") or "escaneo_result.txt"
    
    print(f"Guardando resultados en {resultado}...")
    with open(resultado, "w") as f:
        f.write(f"Escaneo realizado el: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        for ip in alive_ips:
            f.write(f"{ip}\n")  # Escribe solo las IPs activas en el archivo de resultados
    
    print(f"Escaneo completo. Resultado guardado en {resultado}.")

if __name__ == "__main__":
    main()


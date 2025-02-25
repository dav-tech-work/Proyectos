import socket
import subprocess
import platform
import datetime
import concurrent.futures
import asyncio

def get_local_ip(): # Crear una función para obtener la IP local
    """Obtiene la IP local del equipo."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Crea una variable de socket que hace uso de la familia de direcciones IPv4 y del protocolo UDP (SOCK_DGRAM) 
    try: # Intenta obtener la IP local
        s.connect(("8.8.8.8", 80))  # Se conecta a un servidor externo para obtener la IP local
        ip = s.getsockname()[0] # Guarda la IP local en la variable ip 
        #print(f"IP local detectada: {ip}") # Imprime la IP local detectada
        return ip # Retorna la IP local
    except Exception: # En caso de error
        print("Error al obtener la IP local, usando 127.0.0.1") # Imprime un mensaje de error
        return "127.0.0.1"  # Retorna localhost en caso de error 
    finally: # Finalmente
        s.close() # Cierra la conexión del socket

def ping_ip(ip):
    """Realiza un ping a la IP dada y retorna True si responde."""
    command = ['ping', '-c', '1', '-W', '0.5', ip] if platform.system().lower() != 'windows' else ['ping', '-n', '1', '-w', '500', ip] # variable command que almacena el comando para hacer ping a la IP dada según el sistema operativo
    result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode # Ejecuta el comando y guarda el resultado en la variable result
    return result == 0 # Retorna True si el resultado es 0 (respuesta recibida)

async def async_scan_port(ip, port, semaphore):
    """Intenta conectar de forma asíncrona al puerto indicado con timeout aumentado."""
    async with semaphore:
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(ip, port), timeout=0.3  # timeout aumentado a 0.3 seg
            )
            writer.close()
            await writer.wait_closed()
            return port, True
        except Exception:
            return port, False

async def async_scan_ports(ip):
    """Escanea de forma asíncrona los primeros 10,000 puertos en la IP dada en bloques."""
    semaphore = asyncio.Semaphore(500)  # Concurrencia un poco menor para no saturar
    results = []
    batch_size = 100  # Puedes ajustar el tamaño del bloque para lograr balance entre carga y rendimiento
    for start in range(1, 10001, batch_size):
        end = min(start + batch_size, 10001)
        tasks = [asyncio.create_task(async_scan_port(ip, port, semaphore))
                 for port in range(start, end)]
        results.extend(await asyncio.gather(*tasks))
    open_ports = [port for port, is_open in results if is_open]
    return sorted(open_ports)

async def scan_all_ports(alive_ips):
    """Escanea de forma asíncrona los puertos para cada IP viva."""
    ip_ports = {}
    tasks = [asyncio.create_task(async_scan_ports(ip)) for ip in alive_ips]
    results = await asyncio.gather(*tasks)
    for ip, ports in zip(alive_ips, results):
        ip_ports[ip] = ports
    return ip_ports

def get_hostname(ip):
    """Obtiene el nombre del host si es posible."""
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return ip

def main():
    local_ip = get_local_ip()
    base = '.'.join(local_ip.split('.')[:3]) + '.'  # Extrae la parte base de la IP para escanear la red local
    ips_to_scan = [base + str(i) for i in range(1, 255)]  # Genera todas las IPs dentro de la subred /24
    
    print("Iniciando escaneo de IPs...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        alive_ips = [ip for ip, result in zip(ips_to_scan, executor.map(ping_ip, ips_to_scan)) if result]
    
    print(f"Total de IPs activas encontradas: {len(alive_ips)}")
    
    print("Escaneando puertos en las IPs activas... Esto puede tardar un momento.")
    ip_ports = asyncio.run(scan_all_ports(alive_ips))
    
    name = input("Introduce el nombre del archivo donde guardar los resultados (por defecto 'escaneo.txt'): ")
    print(f"Guardando resultados en {name}...")
    with open(name, "w") as f:
        f.write(f"Escaneo realizado el: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        for ip, ports in ip_ports.items():
            hostname = get_hostname(ip)
            f.write(f"{hostname} ({ip}): {', '.join(map(str, ports)) if ports else 'Ninguno'}\n")
    
    print(f"Escaneo completo. Resultado guardado en {name}.")

if __name__ == "__main__":
    main()

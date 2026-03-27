import threading
import queue
import socket

# Cola global de hosts: aquí guardamos los dominios a escanear.
cola_paginas = queue.Queue()

# Lock para evitar que varios hilos impriman al mismo tiempo y se mezclen textos.
print_lock = threading.Lock()


def scan_port(host, cola_puertos):
    """
    Worker de puertos:
    - Toma un puerto de la cola de puertos de ESTE host.
    - Intenta conectarse al host en ese puerto.
    - Si conecta, el puerto está abierto.
    """
    while not cola_puertos.empty():
        try:
            # Tomamos el siguiente puerto sin bloquear el hilo.
            port = cola_puertos.get_nowait()
        except queue.Empty:
            # Si la cola quedó vacía, este hilo termina su trabajo.
            break

        try:
            # Creamos un socket TCP (AF_INET + SOCK_STREAM).
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # Tiempo máximo de espera por intento (en segundos).
                s.settimeout(0.5)

                # connect_ex devuelve 0 si pudo conectar; otro valor si falló.
                result = s.connect_ex((host, port))
                if result == 0:
                    with print_lock:
                        # Mostramos sólo los puertos abiertos para no saturar salida.
                        print(f"[{host}] Puerto {port} ABIERTO")
        except Exception:
            # Si hay error de red/socket, lo ignoramos y seguimos con el siguiente puerto.
            pass
        finally:
            # Marcamos que este puerto ya fue procesado por un hilo.
            cola_puertos.task_done()


def scan_host():
    """
    Worker de hosts:
    - Toma un host de la cola global de hosts.
    - Crea una cola local de puertos para ese host (1..10000).
    - Lanza varios hilos para escanear sus puertos en paralelo.
    """
    while not cola_paginas.empty():
        try:
            # Tomamos un host sin bloquear este hilo.
            host = cola_paginas.get_nowait()
        except queue.Empty:
            # Si no quedan hosts, este hilo termina.
            break

        print(f"\n--- Escaneando {host} (puertos 1-10000) ---")

        # Cola de puertos LOCAL por host (evita mezclar puertos entre hosts).
        cola_puertos = queue.Queue()

        # Cargamos los puertos a escanear.
        for port in range(1, 10001):
            cola_puertos.put(port)

        # Hilos de puertos para este host (segunda capa de paralelización).
        num_threads = 100
        threads = []
        for _ in range(num_threads):
            # Cada hilo ejecuta scan_port sobre el mismo host y la misma cola local.
            t = threading.Thread(target=scan_port, args=(host, cola_puertos))
            t.start()
            threads.append(t)

        # Esperamos a que terminen todos los hilos de puertos de este host.
        for t in threads:
            t.join()

        print(f"--- Escaneo de {host} completado ---\n")

        # Marcamos este host como procesado en la cola global.
        cola_paginas.task_done()


if __name__ == "__main__":
    # Lista de hosts a escanear (pueden ser dominios o IPs).
    pages = [
        "google.com",
        "yahoo.com",
        "github.com",
        "wikipedia.org",
    ]

    # Cargamos todos los hosts en la cola global.
    for page in pages:
        cola_paginas.put(page)

    # Hilos de hosts (primera capa de paralelización).
    # Idea: varios hosts se escanean al mismo tiempo.
    host_threads = []
    for _ in range(len(pages)):
        # Cada hilo toma un host de cola_paginas y ejecuta scan_host().
        t = threading.Thread(target=scan_host)
        t.start()
        host_threads.append(t)

    # Esperamos a que terminen todos los hilos de hosts.
    for t in host_threads:
        t.join()

    # Mensaje final cuando ya no quedan hosts ni puertos pendientes.
    print("Escaneo completo de todas las páginas.")
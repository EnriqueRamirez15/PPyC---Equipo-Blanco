import requests
import multiprocessing as mp
import time


MAX_ITEMS = 50 # Número máximo de chistes a producir
TIME_LIMIT = 5 # Tiempro máximo de ejecución 
QUEUE_SIZE = 20 #Tamaño máximo de la cola
NUM_PRODUCTORES = 2 # Número de procesos productores
NUM_CONSUMIDORES = 3 # Número de procesos consumidores

endpoint = "https://api.chucknorris.io/jokes/random"

# Definimos la ruta en la que se guardarán los chistes
ruta_archivo = r"C:\Users\52563\Documents\Semestre_26-II\PPyC\chistes.txt"

def productor(id, cola, stop_event, contador, lock):
    # Se ejecuta hasta que se active la señal de paro
    while not stop_event.is_set():
        try:
            #Petición HTTP a la API
            r = requests.get(endpoint, timeout=2)
            
            # Extraer el chiste del JSON
            joke = r.json()['value']

            # Agregar el chiste a la cola 
            cola.put(joke)

            with lock:
                # Actualizar el contador compartido
                contador.value += 1

                # Detenerse si hay más de 50 chistes
                if contador.value >= MAX_ITEMS:
                    stop_event.set()

            print(f"[Productor {id}] produjo chiste")

        except Exception as e:
            print(f"[Productor {id}] error:", e)


def consumidor(id, cola, ruta_archivo):
    while True:
        # Obtener elemento de la cola
        item = cola.get()

        # Si recibe un centinela, termina el proceso
        if item is None:
            break
        
        # Escribe el chiste en el archivo
        with open(ruta_archivo, "a", encoding="utf-8") as f:
            f.write(item + "\n\n")

        print(f"[Consumidor {id}] consumió chiste")


if __name__ == "__main__":
    # Cola compratida entre procesos
    cola = mp.Queue(maxsize=QUEUE_SIZE)
    
    # Evento para indicar cuándo detner el sistema
    stop_event = mp.Event()

    # Contador compartido 
    contador = mp.Value('i', 0)

    # Lock para evitar condiciones de carrera
    lock = mp.Lock()

    # Crear procesos productores
    productores = [
        mp.Process(target=productor, args=(i, cola, stop_event, contador, lock))
        for i in range(NUM_PRODUCTORES)
    ]

    # Crear procesos consumidores
    consumidores = [
        mp.Process(target=consumidor, args=(i, cola, ruta_archivo))
        for i in range(NUM_CONSUMIDORES)
    ]

    # Iniciar procesos
    for p in productores + consumidores:
        p.start()

    # Control por tiempo
    start_time = time.time()
    while time.time() - start_time < TIME_LIMIT:
        if stop_event.is_set():
            break
        time.sleep(0.1)

    stop_event.set()

    # Esperar productores
    for p in productores:
        p.join()

    # Enviar centinelas
    for _ in consumidores:
        cola.put(None)

    # Esperar consumidores
    for c in consumidores:
        c.join()

    print("Sistema terminado correctamente.")

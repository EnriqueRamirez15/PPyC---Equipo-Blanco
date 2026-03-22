import requests
import threading
import time
import os
from pathlib import Path

# lista de 5 urls de archivos pequeños públicos
archivos = [
    "https://www.unam.mx/",                                                          
    "https://www.amazon.com/robots.txt",                                             
    "https://www.google.com/robots.txt",                                             
    "https://www.apple.com/business/",                                               
    "https://www.liverpool.com.mx/"                                                  
]

def descargar_archivo(url, ruta_archivo):
    """
    descarga un archivo desde una url y lo guarda de forma local
    """
    try:
        # stream=True: obtiene la respuesta sin descargar el cuerpo completo en memoria
        # timeout=10: establece un límite de 10 segundos para esperar la respuesta
        respuesta = requests.get(url, stream=True, timeout=10)
        # lanza una excepción si el código de estado indica error
        respuesta.raise_for_status()
        
        # abre el archivo en modo wb, escritura binaria 
        # el 'with' cierra automáticamente el archivo al salir del bloque
        with open(ruta_archivo, 'wb') as archivo:
            # iter_content() itera sobre el contenido en "secciones"
            # seccion_size=1024 significa que descarga 1KB a la vez para no saturar memoria
            # esto es más eficiente que descargar todo de una vez a memoria
            for seccion in respuesta.iter_content(seccion_size=1024):
                # verifica que la seccion no esté vacía (puede haber secciones vacías al final)
                if seccion:
                    # escribe la seccion binaria al archivo
                    archivo.write(seccion)
        
        # si todo fue exitoso, regresa True y el nombre del archivo guardado
        return True, ruta_archivo
    except Exception as e:
        return False, f"Error en {ruta_archivo}: {str(e)}"

def descargar_secuencial(lista_urls, directorio="descargas_secuencial"):
    """
    versión secuencial: descarga los archivos uno por uno.
    """
    # crear directorio si no existe
    Path(directorio).mkdir(parents=True, exist_ok=True)
    
    tiempo_inicio = time.time()
    resultados = []
    
    for idx, url in enumerate(lista_urls, 1):
        ejercicio_06 = f"{directorio}/archivo_{idx}.txt"
        print(f"[Secuencial] Descargando archivo {idx}/{len(lista_urls)}: {url}")
        
        exito, mensaje = descargar_archivo(url, ejercicio_06)
        resultados.append((exito, mensaje))
        
        if exito:
            print(f"  ✓ Guardado: {ejercicio_06}")
        else:
            print(f"  ✗ {mensaje}")
    
    tiempo_total = time.time() - tiempo_inicio
    return resultados, tiempo_total

def descargar_concurrente(lista_urls, directorio="descargas_concurrente", num_hilos=5):
    """
    versión con threads: descarga múltiples archivos en paralelo.
    cada hilo descarga una URL y guarda su archivo.
    
    ventaja: mientras un hilo espera a que termine la descarga de red (I/O),
    otros hilos pueden hacer sus descargas. Esto acelera significativamente
    cuando hay múltiples archivos.
    """
    # crear directorio si no existe
    Path(directorio).mkdir(exist_ok=True)
    
    tiempo_inicio = time.time()
    resultados = []
    
    # lock (candado): protege el acceso a variables compartidas entre hilos
    # sin lock, si dos hilos intentan escribir en resultados[] al mismo tiempo,
    # podrían causar corrupción
    lock = threading.Lock()
    
    # función descargador: esta es la función que ejecutará cada hilo
    # recibe la URL y un índice como parámetros
    def descargador(url, idx):
        # cada hilo usa su propio nombre de archivo basado en su índice
        ejercicio_06 = f"{directorio}/archivo_hilo_{idx}.txt"
        print(f"[Hilos] Hilo {idx} descargando: {url}")
        
        # descarga el archivo
        # mientras este hilo espera la red, otros hilos pueden ejecutarse
        exito, mensaje = descargar_archivo(url, ejercicio_06)
        
        # nota: usar lock para acceder a la lista compartida de forma segura
        # "with lock:" espera a adquirir el candado, ejecuta el código,
        # luego libera el candado automáticamente
        with lock:
            # dentro del lock: solo un hilo puede estar aquí a la vez
            resultados.append((exito, mensaje))
            if exito:
                print(f"  ✓ Hilo {idx} guardó: {ejercicio_06}")
            else:
                print(f"  ✗ Hilo {idx}: {mensaje}")
        # salimos del lock: otros hilos ya pueden entrar
    
    # crear hilos
    hilos = []
    for idx, url in enumerate(lista_urls, 1):
        # threading.Thread crea un nuevo hilo
        # target=descargador: especifica qué función ejecutará el hilo
        # args=(url, idx):es una tupla con los argumentos para pasar a descargador()
        hilo = threading.Thread(target=descargador, args=(url, idx))
        hilos.append(hilo)  # guardar referencia del hilo en una lista
        
        # hilo.start(): inicia el hilo (lo pone a ejecutarse en paralelo)
        # NOTA: start() no espera a que termine, sigue inmediatamente
        hilo.start()
    
    # esperar a que terminen los hilos
    # aquí es donde nos aseguramos de que todas las descargas se completen
    # antes de continuar
    for hilo in hilos:
        # hilo.join(): bloquea hasta que el hilo termine su ejecución
        # sin join(), el programa terminaría antes de que terminaran las descargas
        hilo.join()
    
    tiempo_total = time.time() - tiempo_inicio
    return resultados, tiempo_total

def contar_archivos_descargados(directorio):
    """
    cuenta cuántos archivos se descargaron exitosamente.
    """
    if not os.path.exists(directorio):
        return 0
    return len([f for f in os.listdir(directorio) if os.path.isfile(os.path.join(directorio, f))])

if __name__ == "__main__":
    print("=" * 70)
    print("ejercicio 06: descargas secuenciales vs concurrentes con hilos")
    print("=" * 70)
    
    # versión secuencial
    print("\n--- secuencial descarga uno por uno ---")
    resultados_seq, tiempo_seq = descargar_secuencial(archivos)
    existe_seq = contar_archivos_descargados("descargas_secuencial")
    print(f"\nTiempo total (secuencial): {tiempo_seq:.2f} segundos")
    print(f"Archivos descargados: {existe_seq}/{len(archivos)}")
    
    # versión con hilos
    print("\n" + "=" * 70)
    print("\n--- hilos, descarga en paralelo ---")
    resultados_conc, tiempo_conc = descargar_concurrente(archivos)
    existe_conc = contar_archivos_descargados("descargas_concurrente")
    print(f"\nTiempo total concurrente: {tiempo_conc:.2f} segundos")
    print(f"Archivos descargados: {existe_conc}/{len(archivos)}")
    
    # comparación y resultados
    print("\n" + "=" * 70)
    print("--- comparando y analizando ---")
    print(f"Tiempo secuencial:  {tiempo_seq:.2f}s")
    print(f"Tiempo concurrente: {tiempo_conc:.2f}s")
    if tiempo_conc > 0:
        mejora = ((tiempo_seq - tiempo_conc) / tiempo_seq) * 100
        factor = tiempo_seq / tiempo_conc
        print(f"Mejora de velocidad: {mejora:.1f}%")
    print("=" * 70)

import requests
import threading
import os 
from helper_functions.obtener_tamanio import obtener_tamano
from helper_functions.descargar_fragmento import descargar_fragmento

# Archivo de prueba (Instalador de Python)
url_archivo = "https://www.python.org/ftp/python/3.11.5/python-3.11.5.exe"

num_hilos = 4
tamano_total = obtener_tamano(url_archivo)

print(f"Tamaño total: {tamano_total} bytes")

# calcular tamaño de cada fragmento
tamano_fragmento = tamano_total // num_hilos

hilos = []

for i in range(num_hilos):
    inicio = i * tamano_fragmento
    
    # el último fragmento llega hasta el final
    if i == num_hilos - 1:
        fin = tamano_total - 1
    else:
        fin = (inicio + tamano_fragmento - 1)

    hilo = threading.Thread(
        target=descargar_fragmento,
        args=(url_archivo, inicio, fin, i)
    )

    hilos.append(hilo)
    hilo.start()

# esperar a que todos los hilos terminen
for hilo in hilos:
    hilo.join()

print("Descarga completa. Uniendo fragmentos...")

# unir fragmentos
nombre_final = "python_descargado.exe"

with open(nombre_final, 'wb') as archivo_final:
    for i in range(num_hilos):
        nombre_part = f"parte_{i}.tmp"
        with open(nombre_part, 'rb') as f:
            archivo_final.write(f.read())

        os.remove(nombre_part)

print("Archivo unido correctamente.")
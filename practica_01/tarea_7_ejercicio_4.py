import urllib.request
from collections import Counter
import re
import concurrent.futures

#Lista de libros
libros = [
    ("https://www.gutenberg.org/cache/epub/1342/pg1342.txt", "Orgullo y Prejuicio"),
    ("https://www.gutenberg.org/cache/epub/84/pg84.txt", "Frankenstein"),
    ("https://www.gutenberg.org/cache/epub/11/pg11.txt", "Alicia en el pais de las maravillas")
]

#funcion base (FASE MAP)
def contar_palabras(url):
    """Descarga el texto, lo limpia y cuenta las palabras retornando un Counter."""
    respuesta = urllib.request.urlopen(url)
    texto = respuesta.read().decode('utf-8').lower()
    lista_palabras = re.findall(r'\b\w+\b', texto)
    return Counter(lista_palabras)


def main():
    #lista compartida para guardar conteoss parciales
    conteos_parciales = [] #recolecta los tres objetos conforme los hilos terminan
     
    #FASE MAP: lanza las descargas al mismo tiempo, en lugar de esperar a que cargen una por una
    print("Iniciando Fase Map: descargando y procesando libros en hilos paralelos...")
    
    #un hilo para cada libro
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(libros)) as executor:
       tareas = {executor.submit(contar_palabras, url) : titulo for url, titulo in libros}

    #a medida que los hilos van terminando, guardamos su counter
    for tarea in concurrent.futures.as_completed(tareas):
       titulo = tareas[tarea]
       try: 
          #obtiene el counter qye devuelve la funcion
          resultado_contador = tarea.result()
          #se agrega a lista compartida
          conteos_parciales.append(resultado_contador)
          print(f"[+]Terminado: {titulo}")
       except Exception as e:
          print(f"[-]Error al procesar '{titulo}': {e}")
    
    #Fase reduce
    print("\nIniciando fase reduce: uniendo todos los conteos...")
    contador_final = Counter() #usamos un bucle para el metodo update

    #lista de cointers parciales y union de ellos
    for contador_parcial in conteos_parciales:
       contador_final.update(contador_parcial)
    
    print("\n=== 20 PALABRAS MAS FRECUENTES ===")
    for palabra, frecuencia in contador_final.most_common(20):
       print(f"{palabra} : {frecuencia}")

if __name__ == "__main__":
   main()

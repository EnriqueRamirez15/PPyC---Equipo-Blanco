import requests
from PIL import Image
import io
import matplotlib.pyplot as plt 
import threading
import numpy as np
from helper_functions.escala_grises_secuencial import escala_grises_secuencial
from helper_functions.mostrar_imagenes import show_images
from helper_functions.procesar_franja import procesar_franja


url_image = (
    "https://images.unsplash.com/"
    "photo-1506748686214-e9df14d4d9d0?w=1080"
)

response = requests.get(url_image)
# Para mostrar la imagen antes de convertir a escala de grises.
img = Image.open(io.BytesIO(response.content))
show_images(img, 5)

print("-----------------------")
print("Matriz de la imagen original")
matriz = np.array(img)
print(matriz)

matriz_escala_grises = escala_grises_secuencial(matriz)
print("-------------------------")
print("Matriz de la imagen en escala de grises")
print(matriz_escala_grises)

# Se convierte la matriz a imagen solo para verificar que ahora esta en escala de grises
img_final = Image.fromarray(matriz_escala_grises)
show_images(img_final, 5)

# Ahora se hara el mismo proceso pero usando programacion paralela ( hilos )

# Esta funcion se define aqui y no en helper_functions ya que esta es la funcion principal para 
# trabajar con hilos
def escala_grises_con_hilos(matriz, num_hilos=4):
  alto = matriz.shape[0]            # numero total de filas
  bloque = alto // num_hilos        # Calcula cuantas filas le toca a cada hilo
  hilos = []

  # Creacion de hilos
  for i in range(num_hilos):
    inicio = i * bloque
    fin = alto if i == num_hilos - 1 else (i + 1) * bloque
    hilo = threading.Thread(target=procesar_franja, args=(matriz, inicio, fin))
    hilos.append(hilo)
    hilo.start()
  for hilo in hilos:
    hilo.join()
  return matriz

print("-------------------------")
print("Matriz en escala de grises usando hilos")
matriz_escala_grises_con_hilos = escala_grises_con_hilos(matriz)
print(matriz_escala_grises)

img_final = Image.fromarray(matriz_escala_grises_con_hilos)
show_images(img_final,5)

# Este mismo ejercicio se encuentra en el siguiente link de colab edit, donde igual se puede
# ejecutar para ir viendo como la imagen se convierte en escala de grises
# https://colab.research.google.com/drive/1NEO-o5v-nQy-5aAI7vcbJ37UqtPSWkC6?usp=sharing#scrollTo=-wh18XerTTKB
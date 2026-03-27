import requests

def obtener_tamano(url):
    respuesta = requests.head(url)
    return int(respuesta.headers.get('content-length',0))
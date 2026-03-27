import requests

def descargar_fragmento(url, inicio, fin, id_fragmento):
    headers = {'Range': f'bytes={inicio}-{fin}'}
    respuesta = requests.get(url, headers=headers, stream=True)

    nombre_part = f"parte_{id_fragmento}.tmp"
    with open(nombre_part, 'wb') as f:
        for chunk in respuesta.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

    print(f"Fragmento {id_fragmento} descargado.")
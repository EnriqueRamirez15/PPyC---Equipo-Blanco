import time
import random
import requests
import threading
from bs4 import BeautifulSoup
import queue
from sqlalchemy import create_engine, text

user = "postgres"
password = "supersecret"
host = "localhost"
port = "5432"
database = "postgres"

def get_connection(user, password, host, port, database):
    return create_engine(
        url="postgresql+psycopg2://{0}:{1}@{2}:{3}/{4}".format(
            user, password, host, port, database
        )
    )

engine = get_connection(user, password, host, port, database)

# Cola de símbolos
cola_procesos = queue.Queue()

def obtener_e_insertar():
    """
    Cada hilo:
    1. Toma un símbolo
    2. Obtiene su precio desde Yahoo Finance
    3. Inserta directamente en la base de datos
    """

    while not cola_procesos.empty():
        try:
            symbol = cola_procesos.get_nowait()
        except queue.Empty:
            break

        # URL del símbolo
        URL = f"https://finance.yahoo.com/quote/{symbol}"
        headers = {"User-Agent": "MiProyecto/1.0"}

        # Intentamos hasta obtener respuesta válida
        while True:
            time.sleep(30 * random.random())
            response = requests.get(URL, headers=headers)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                valor = soup.find("span", {"data-testid": "qsp-price"})
                precio = valor.text.strip() if valor else "Privado"
                break

        print(f"[SCRAPER+BD] {symbol}: {precio}")

        # Insertar en la BD (MISMO HILO)
        with engine.connect() as connector:
            connector.execute(
                text("""
                    INSERT INTO inversiones (symbol, precio)
                    VALUES (:symbol, :precio)
                """),
                {"symbol": symbol, "precio": precio}
            )
            connector.commit()

        cola_procesos.task_done()

if __name__ == "__main__":

    with open("Clase 3/data/lista_sp500.txt", "r") as f:
        lista_symbolos = eval(f.read())

    for symbol in lista_symbolos:
        cola_procesos.put(symbol)

    threads = []
    for _ in range(8):
        t = threading.Thread(target=obtener_e_insertar)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

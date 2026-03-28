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

# COLAS
cola_scraping = queue.Queue()  # símbolos
cola_bd = queue.Queue()        # resultados finales

# FASE 1: SOLO SCRAPING
def obtener_precio():
    """
    Esta función SOLO obtiene precios.
    NO escribe en la base de datos.
    """
    while not cola_scraping.empty():
        try:
            symbol = cola_scraping.get_nowait()
        except queue.Empty:
            break

        URL = f"https://finance.yahoo.com/quote/{symbol}"
        headers = {"User-Agent": "MiProyecto/1.0"}

        while True:
            time.sleep(30 * random.random())
            response = requests.get(URL, headers=headers)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                valor = soup.find("span", {"data-testid": "qsp-price"})
                precio = valor.text.strip() if valor else "Privado"
                break

        print(f"[SCRAPER] {symbol}: {precio}")

        # Guardamos resultado en cola de BD
        cola_bd.put((symbol, precio))

        cola_scraping.task_done()

# FASE 2: SOLO INSERCIÓN BD
def insertar_bd():
    """
    Esta función SOLO inserta datos en la BD.
    NO hace scraping.
    """
    while not cola_bd.empty():
        try:
            symbol, precio = cola_bd.get_nowait()
        except queue.Empty:
            break

        with engine.connect() as connector:
            connector.execute(
                text("""
                    INSERT INTO inversiones (symbol, precio)
                    VALUES (:symbol, :precio)
                """),
                {"symbol": symbol, "precio": precio}
            )
            connector.commit()

        print(f"[BD] Insertado {symbol}")

        cola_bd.task_done()

if __name__ == "__main__":

    with open("Clase 3/data/lista_sp500.txt", "r") as f:
        lista_symbolos = eval(f.read())

    # FASE 1: SCRAPING
    for symbol in lista_symbolos:
        cola_scraping.put(symbol)

    scrapers = []
    for _ in range(8):
        t = threading.Thread(target=obtener_precio)
        t.start()
        scrapers.append(t)

    # Esperamos a que termine todo el scraping
    for t in scrapers:
        t.join()

    print("\n--- FIN DE SCRAPING ---\n")

    # FASE 2: INSERCIÓN
    writers = []
    for _ in range(4):
        t = threading.Thread(target=insertar_bd)
        t.start()
        writers.append(t)

    for t in writers:
        t.join()

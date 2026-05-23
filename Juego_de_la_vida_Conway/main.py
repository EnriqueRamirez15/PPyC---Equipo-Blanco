import numpy as np
import time
from multiprocessing import Pool
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN ---
FILAS, COLS = 1000, 1000
SEMILLA = 42
MAX_GENS = 10

def obtener_vecinos(tablero, f, c):
    vivos = 0
    f_inicio, f_fin = max(0, f - 1), min(FILAS - 1, f + 1)
    c_inicio, c_fin = max(0, c - 1), min(COLS - 1, c + 1)
    for i in range(f_inicio, f_fin + 1):
        for j in range(c_inicio, c_fin + 1):
            if i == f and j == c: continue
            if tablero[i, j] == 1: vivos += 1
    return vivos

def procesar_bloque(args):
    f_idx_inicio, f_idx_fin, c_idx_inicio, c_idx_fin, tablero = args
    alto, ancho = f_idx_fin - f_idx_inicio, c_idx_fin - c_idx_inicio
    resultado_bloque = np.zeros((alto, ancho), dtype=int)
    for f in range(f_idx_inicio, f_idx_fin):
        for c in range(c_idx_inicio, c_idx_fin):
            vecinos = obtener_vecinos(tablero, f, c)
            if (tablero[f, c] == 1 and vecinos in [2, 3]) or (tablero[f, c] == 0 and vecinos == 3):
                resultado_bloque[f - f_idx_inicio, c - c_idx_inicio] = 1
    return (f_idx_inicio, f_idx_fin, c_idx_inicio, c_idx_fin, resultado_bloque)



def crear_tareas(num_procesos, tablero):
    if num_procesos == 1: return [(0, 1000, 0, 1000, tablero)]
    if num_procesos == 2: return [(0, 1000, 0, 500, tablero), (0, 1000, 500, 1000, tablero)]
    if num_procesos == 4: return [(i, i+500, j, j+500, tablero) for i in [0, 500] for j in [0, 500]]
    if num_procesos == 8: return [(i, i+250, j, j+500, tablero) for i in range(0, 1000, 250) for j in [0, 500]]



def ejecutar_prueba(n_procesos):
    np.random.seed(SEMILLA)
    tablero = np.random.choice([0, 1], size=(FILAS, COLS), p=[0.95, 0.05])
    tiempos = []
    
    print(f"\n>>> INICIANDO PRUEBA CON {n_procesos} PROCESO(S) <<<")
    
    with Pool(processes=n_procesos) as pool:
        for g in range(MAX_GENS):
            inicio = time.perf_counter()
            
            tareas = crear_tareas(n_procesos, tablero)
            resultados = pool.map(procesar_bloque, tareas)
            
            nuevo_tablero = np.zeros_like(tablero)
            for f_s, f_e, c_s, c_e, bloque in resultados:
                nuevo_tablero[f_s:f_e, c_s:c_e] = bloque
            
            t_gen = time.perf_counter() - inicio
            tiempos.append(t_gen)
            tablero = nuevo_tablero
            
            poblacion = np.sum(tablero)
            print(f"  [Gen {g+1}] Células vivas: {poblacion} | Tiempo: {t_gen:.4f}s")
            
    return sum(tiempos)

if __name__ == "__main__":
    configs = [1, 2, 4, 8]
    tiempos_finales = []

    for p in configs:
        t_total = ejecutar_prueba(p)
        tiempos_finales.append(t_total)
        print(f"TOTAL PARA {p} PROCESOS: {t_total:.2f}s")

    # --- GENERAR Y MOSTRAR GRÁFICA ---
    plt.figure(figsize=(10, 6))
    plt.plot(configs, tiempos_finales, marker='o', linestyle='-', color='blue', linewidth=2)
    plt.title(f"Juego de la vida de Conway para una matriz de tamaño {FILAS}x{COLS}")
    plt.xlabel("Número de Procesos (Núcleos)")
    plt.ylabel("Tiempo Total Acumulado (segundos)")
    plt.xticks(configs)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Añadir etiquetas de tiempo sobre los puntos
    for i, txt in enumerate(tiempos_finales):
        plt.annotate(f"{txt:.2f}s", (configs[i], tiempos_finales[i]), 
                     textcoords="offset points", xytext=(0,10), ha='center')

    print("\nCerrando simulación. Mostrando gráfica de rendimiento...")
    plt.show()
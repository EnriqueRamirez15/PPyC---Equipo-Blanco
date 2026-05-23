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

def procesar_franja(matriz, inicio, fin):
  for i in range(inicio, fin):
    for j in range (matriz.shape[1]):
      r, g, b = matriz[i, j]
      gris = int(0.299*r + 0.587*g + 0.114*b)
      matriz[i, j] = [gris, gris, gris]
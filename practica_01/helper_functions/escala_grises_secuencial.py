def escala_grises_secuencial(matriz):
  alto, ancho, canales = matriz.shape
  for i in range(alto):
    for j in range(ancho):
      r, g, b = matriz[i, j]
      # Fórmula estándar de luminosidad
      gris = int(0.299*r + 0.587*g + 0.114*b)
      matriz[i, j] = [gris, gris, gris]
  return matriz
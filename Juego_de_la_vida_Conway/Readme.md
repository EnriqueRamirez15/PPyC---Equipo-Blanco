# Implementación paralela del juego de la vida de Conway

- Fajardo Ana Paloma
- Falcón Diaz Ricardo
- Monroy Alarcón Omar Ulises
- Perez Lopez Zaira Cecilia
- Ramírez Rodríguez Enrique

Este repositorio contiene una implementación del Juego de la Vida de John Conway, desarrollada como parte del curso MAC-PPyC-2026-2. El enfoque principal de este proyecto es la aplicación de técnicas de computación paralela y concurrente para optimizar la evolución del autómata celular.

## 🚀 Descripción del Proyecto
El objetivo es demostrar la mejora en el tiempo de ejecución mediante la descomposición de dominio. El tablero se divide en múltiples segmentos que son procesados simultáneamente por distintos hilos/procesos, permitiendo manejar configuraciones más complejas y tableros de mayor escala que una implementación secuencial estándar.

## Estructura Principal
main.py: Es el núcleo del proyecto. Aquí se encuentra consolidado todo el trabajo de lógica, gestión de paralelismo y la interfaz gráfica final. Este archivo integra las funciones de evolución distribuida y la visualización en tiempo real.

sequential_pygame.py: Este archivo contiene la versión base secuencial. Se mantiene en el repositorio no solo como punto de referencia para el benchmarking, sino también como una propuesta para el trabajo futuro, enfocada en optimizaciones de renderizado gráfico y manejo de eventos.

## 👥 Colaboración
Este proyecto es el resultado de un esfuerzo conjunto. Todos los participantes contribuyeron activamente en las etapas de:

- Diseño de la estrategia de paralelización.
- Implementación de la lógica de vecindad de Moore.
- Pruebas de rendimiento y depuración de condiciones de carrera.
- Documentación técnica.

## 🛠️ Tecnologías Utilizadas

- Python 3
- Pygame: Para la visualización y renderizado del tablero.
- Multiprocessing / Threading: Para la ejecución paralela de las reglas de transición.
- NumPy: Para la manipulación eficiente de matrices.

**Nota sobre el Trabajo Futuro**: Se planea expandir la funcionalidad del proyecto integrando las mejoras sugeridas en sequential_pygame.py, buscando una mayor eficiencia en la comunicación entre procesos y la implementación de patrones de vida predefinidos más complejos.

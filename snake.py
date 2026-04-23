"""
Juego de Snake en Python básico.

Conceptos que se practican:
  - Variables y constantes
  - Listas y tuplas
  - Funciones
  - Bucles: while, for
  - Condicionales: if / elif / else
  - Módulos: pygame, random, sys
"""

import pygame
import random
import sys

# ─── Constantes del tablero ───────────────────────────────────────────────────

ANCHO = 600  # píxeles de ancho de la ventana
ALTO = 600  # píxeles de alto de la ventana
CELDA = 20  # tamaño de cada cuadro en píxeles
COLUMNAS = ANCHO // CELDA
FILAS = ALTO // CELDA
FPS = 10  # fotogramas por segundo (velocidad de la serpiente)

# ─── Colores (tuplas R, G, B) ─────────────────────────────────────────────────

NEGRO = (0, 0, 0)
GRIS = (40, 40, 40)
VERDE = (0, 200, 0)
VERDE_OSCURO = (0, 140, 0)
ROJO = (220, 30, 30)
BLANCO = (255, 255, 255)

# ─── Direcciones (desplazamiento en x, y por turno) ──────────────────────────

ARRIBA = (0, -1)
ABAJO = (0, 1)
IZQUIERDA = (-1, 0)
DERECHA = (1, 0)

# ─── Funciones del juego ──────────────────────────────────────────────────────


def crear_serpiente():
    """Devuelve la lista de posiciones iniciales de la serpiente."""
    cx = COLUMNAS // 2
    cy = FILAS // 2
    # Cada elemento es una tupla (columna, fila)
    return [(cx, cy), (cx - 1, cy), (cx - 2, cy)]


def crear_comida(serpiente):
    """Devuelve una posición aleatoria que no esté ocupada por la serpiente."""
    while True:
        x = random.randint(0, COLUMNAS - 1)
        y = random.randint(0, FILAS - 1)
        if (x, y) not in serpiente:
            return (x, y)


def mover(serpiente, direccion):
    """Desplaza la serpiente: nueva cabeza al frente, elimina la cola."""
    cabeza_x, cabeza_y = serpiente[0]
    dx, dy = direccion
    nueva_cabeza = (cabeza_x + dx, cabeza_y + dy)
    # [nueva cabeza] + [todo el cuerpo excepto el último segmento]
    return [nueva_cabeza] + serpiente[:-1]


def crecer(serpiente, direccion):
    """Como mover(), pero conserva la cola (la serpiente crece)."""
    cabeza_x, cabeza_y = serpiente[0]
    dx, dy = direccion
    nueva_cabeza = (cabeza_x + dx, cabeza_y + dy)
    return [nueva_cabeza] + serpiente


def colision(serpiente):
    """Devuelve True si la cabeza choca con una pared o con el cuerpo."""
    cx, cy = serpiente[0]

    fuera_de_limite = cx < 0 or cx >= COLUMNAS or cy < 0 or cy >= FILAS
    if fuera_de_limite:
        return True

    # La cabeza está en la lista [1:] si se mordió a sí misma
    if serpiente[0] in serpiente[1:]:
        return True

    return False


def nueva_direccion(tecla, direccion_actual):
    """
    Devuelve la dirección correspondiente a la tecla presionada.
    Ignora la dirección opuesta para no ir en reversa.
    """
    if tecla == pygame.K_UP and direccion_actual != ABAJO:
        return ARRIBA
    if tecla == pygame.K_DOWN and direccion_actual != ARRIBA:
        return ABAJO
    if tecla == pygame.K_LEFT and direccion_actual != DERECHA:
        return IZQUIERDA
    if tecla == pygame.K_RIGHT and direccion_actual != IZQUIERDA:
        return DERECHA
    return direccion_actual  # cualquier otra tecla: sin cambio


# ─── Funciones de dibujo ──────────────────────────────────────────────────────


def dibujar_cuadricula(pantalla):
    for x in range(0, ANCHO, CELDA):
        pygame.draw.line(pantalla, GRIS, (x, 0), (x, ALTO))
    for y in range(0, ALTO, CELDA):
        pygame.draw.line(pantalla, GRIS, (0, y), (ANCHO, y))


def dibujar_serpiente(pantalla, serpiente):
    for i, (x, y) in enumerate(serpiente):
        rect = pygame.Rect(x * CELDA + 1, y * CELDA + 1, CELDA - 2, CELDA - 2)
        color = VERDE if i == 0 else VERDE_OSCURO  # cabeza más brillante
        pygame.draw.rect(pantalla, color, rect)


def dibujar_comida(pantalla, posicion):
    x, y = posicion
    rect = pygame.Rect(x * CELDA + 3, y * CELDA + 3, CELDA - 6, CELDA - 6)
    pygame.draw.rect(pantalla, ROJO, rect)


def dibujar_puntaje(pantalla, fuente, puntaje):
    texto = fuente.render(f"Puntaje: {puntaje}", True, BLANCO)
    pantalla.blit(texto, (10, 10))


def pantalla_game_over(pantalla, fuente_grande, fuente, puntaje):
    pantalla.fill(NEGRO)

    titulo = fuente_grande.render("¡GAME OVER!", True, ROJO)
    pts = fuente.render(f"Puntaje final: {puntaje}", True, BLANCO)
    reinicio = fuente.render("R = reiniciar    Q = salir", True, BLANCO)

    pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, ALTO // 2 - 90))
    pantalla.blit(pts, (ANCHO // 2 - pts.get_width() // 2, ALTO // 2))
    pantalla.blit(reinicio, (ANCHO // 2 - reinicio.get_width() // 2, ALTO // 2 + 60))
    pygame.display.flip()


# ─── Bucle de espera en Game Over ────────────────────────────────────────────


def esperar_decision():
    """Espera R (reiniciar) o Q (salir) y devuelve True si se elige reiniciar."""
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    return True
                if evento.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()


# ─── Bucle principal ─────────────────────────────────────────────────────────


def jugar():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Snake — Python Básico")
    reloj = pygame.time.Clock()

    fuente = pygame.font.SysFont("monospace", 24)
    fuente_grande = pygame.font.SysFont("monospace", 52, bold=True)

    # Estado inicial
    serpiente = crear_serpiente()
    direccion = DERECHA
    comida = crear_comida(serpiente)
    puntaje = 0
    acaba_de_comer = False

    # Bucle del juego
    while True:

        # 1. Leer eventos del teclado
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                direccion = nueva_direccion(evento.key, direccion)

        # 2. Actualizar posición de la serpiente
        if acaba_de_comer:
            serpiente = crecer(serpiente, direccion)
            acaba_de_comer = False
        else:
            serpiente = mover(serpiente, direccion)

        # 3. Detectar colisión → game over
        if colision(serpiente):
            pantalla_game_over(pantalla, fuente_grande, fuente, puntaje)
            if esperar_decision():
                jugar()  # reinicia el juego desde cero
                return

        # 4. Detectar si comió
        if serpiente[0] == comida:
            acaba_de_comer = True
            puntaje += 10
            comida = crear_comida(serpiente)

        # 5. Dibujar frame
        pantalla.fill(NEGRO)
        dibujar_cuadricula(pantalla)
        dibujar_comida(pantalla, comida)
        dibujar_serpiente(pantalla, serpiente)
        dibujar_puntaje(pantalla, fuente, puntaje)
        pygame.display.flip()

        # 6. Limitar velocidad
        reloj.tick(FPS)


# ─── Punto de entrada ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    jugar()

"""
Juego de Snake — versión Orientada a Objetos.

Comparar con snake.py (versión procedural) para ver la diferencia.

Conceptos de POO que se practican:
  - Clase y objeto (instancia)
  - Constructor __init__
  - Atributos de instancia  (self.algo)
  - Métodos de instancia    (def hacer(self, ...))
  - Encapsulamiento         (cada clase gestiona su propio estado)
  - Composición             (Juego contiene Serpiente, Comida y Pantalla)
"""

import pygame
import random
import sys

# ─── Constantes globales (igual que en la versión procedural) ─────────────────

ANCHO = 1200
ALTO = 1200
CELDA = 20
COLUMNAS = ANCHO // CELDA
FILAS = ALTO // CELDA
FPS = 100

NEGRO = (0, 0, 0)
GRIS = (40, 40, 40)
VERDE = (0, 200, 0)
VERDE_OSCURO = (0, 140, 0)
ROJO = (220, 30, 30)
BLANCO = (255, 255, 255)

ARRIBA = (0, -1)
ABAJO = (0, 1)
IZQUIERDA = (-1, 0)
DERECHA = (1, 0)


# ══════════════════════════════════════════════════════════════════════════════
# CLASE Serpiente
# Responsabilidad: guardar y actualizar el estado de la serpiente.
# ══════════════════════════════════════════════════════════════════════════════


class Serpiente:
    """Representa la serpiente: su cuerpo y su lógica de movimiento."""

    # __init__ es el CONSTRUCTOR: se ejecuta al crear un objeto con Serpiente()
    def __init__(self):
        cx = COLUMNAS // 2
        cy = FILAS // 2
        # self.cuerpo es un ATRIBUTO DE INSTANCIA: pertenece a este objeto
        self.cuerpo = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direccion = DERECHA
        self.creciendo = False  # True cuando acaba de comer

    # ── Métodos ───────────────────────────────────────────────────────────────

    def cambiar_direccion(self, tecla):
        """Actualiza la dirección según la tecla presionada (sin reversa)."""
        if tecla == pygame.K_UP and self.direccion != ABAJO:
            self.direccion = ARRIBA
        elif tecla == pygame.K_DOWN and self.direccion != ARRIBA:
            self.direccion = ABAJO
        elif tecla == pygame.K_LEFT and self.direccion != DERECHA:
            self.direccion = IZQUIERDA
        elif tecla == pygame.K_RIGHT and self.direccion != IZQUIERDA:
            self.direccion = DERECHA

    def avanzar(self):
        """Mueve la serpiente un paso en la dirección actual."""
        cabeza_x, cabeza_y = self.cuerpo[0]
        dx, dy = self.direccion
        nueva_cabeza = (cabeza_x + dx, cabeza_y + dy)

        if self.creciendo:
            self.cuerpo = [nueva_cabeza] + self.cuerpo  # crece: no elimina cola
            self.creciendo = False
        else:
            self.cuerpo = [nueva_cabeza] + self.cuerpo[:-1]  # mueve: elimina cola

    def comer(self):
        """Indica que en el próximo avance la serpiente debe crecer."""
        self.creciendo = True

    def choco(self):
        """Devuelve True si la cabeza colisiona con pared o con el cuerpo."""
        cx, cy = self.cuerpo[0]
        if cx < 0 or cx >= COLUMNAS or cy < 0 or cy >= FILAS:
            return True
        if self.cuerpo[0] in self.cuerpo[1:]:
            return True
        return False

    @property
    def cabeza(self):
        """Acceso conveniente a la posición de la cabeza."""
        return self.cuerpo[0]


# ══════════════════════════════════════════════════════════════════════════════
# CLASE Comida
# Responsabilidad: guardar la posición de la comida y regenerarla.
# ══════════════════════════════════════════════════════════════════════════════


class Comida:
    """Representa la comida en el tablero."""

    def __init__(self, cuerpo_serpiente):
        self.posicion = self._posicion_libre(cuerpo_serpiente)

    def reubicar(self, cuerpo_serpiente):
        """Genera una nueva posición libre tras ser comida."""
        self.posicion = self._posicion_libre(cuerpo_serpiente)

    def _posicion_libre(self, cuerpo_serpiente):
        """Método privado (convención: _ al inicio) — uso interno."""
        while True:
            x = random.randint(0, COLUMNAS - 1)
            y = random.randint(0, FILAS - 1)
            if (x, y) not in cuerpo_serpiente:
                return (x, y)


# ══════════════════════════════════════════════════════════════════════════════
# CLASE Pantalla
# Responsabilidad: todo lo relacionado con dibujar en pantalla.
# ══════════════════════════════════════════════════════════════════════════════


class Pantalla:
    """Encapsula pygame y todas las operaciones de dibujo."""

    def __init__(self):
        pygame.init()
        self.superficie = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Snake — Python OO")
        self.fuente = pygame.font.SysFont("monospace", 24)
        self.fuente_grande = pygame.font.SysFont("monospace", 52, bold=True)

    def limpiar(self):
        self.superficie.fill(NEGRO)

    def mostrar(self):
        pygame.display.flip()

    def dibujar_cuadricula(self):
        for x in range(0, ANCHO, CELDA):
            pygame.draw.line(self.superficie, GRIS, (x, 0), (x, ALTO))
        for y in range(0, ALTO, CELDA):
            pygame.draw.line(self.superficie, GRIS, (0, y), (ANCHO, y))

    def dibujar_serpiente(self, serpiente):
        for i, (x, y) in enumerate(serpiente.cuerpo):
            rect = pygame.Rect(x * CELDA + 1, y * CELDA + 1, CELDA - 2, CELDA - 2)
            color = VERDE if i == 0 else VERDE_OSCURO
            pygame.draw.rect(self.superficie, color, rect)

    def dibujar_comida(self, comida):
        x, y = comida.posicion
        rect = pygame.Rect(x * CELDA + 3, y * CELDA + 3, CELDA - 6, CELDA - 6)
        pygame.draw.rect(self.superficie, ROJO, rect)

    def dibujar_puntaje(self, puntaje):
        texto = self.fuente.render(f"Puntaje: {puntaje}", True, BLANCO)
        self.superficie.blit(texto, (10, 10))

    def mostrar_game_over(self, puntaje):
        self.superficie.fill(NEGRO)
        titulo = self.fuente_grande.render("¡GAME OVER!", True, ROJO)
        pts = self.fuente.render(f"Puntaje final: {puntaje}", True, BLANCO)
        reinicio = self.fuente.render("R = reiniciar    Q = salir", True, BLANCO)
        self.superficie.blit(
            titulo, (ANCHO // 2 - titulo.get_width() // 2, ALTO // 2 - 90)
        )
        self.superficie.blit(pts, (ANCHO // 2 - pts.get_width() // 2, ALTO // 2))
        self.superficie.blit(
            reinicio, (ANCHO // 2 - reinicio.get_width() // 2, ALTO // 2 + 60)
        )
        self.mostrar()


# ══════════════════════════════════════════════════════════════════════════════
# CLASE Juego
# Responsabilidad: coordinar todos los objetos y ejecutar el bucle principal.
# Esto es COMPOSICIÓN: Juego "tiene" una Serpiente, una Comida y una Pantalla.
# ══════════════════════════════════════════════════════════════════════════════


class Juego:
    """Orquesta el estado del juego y el bucle principal."""

    def __init__(self):
        # Composición: creamos instancias de otras clases como atributos
        self.pantalla = Pantalla()
        self.reloj = pygame.time.Clock()
        self._reiniciar()

    def _reiniciar(self):
        """Resetea el estado para una partida nueva."""
        self.serpiente = Serpiente()
        self.comida = Comida(self.serpiente.cuerpo)
        self.puntaje = 0

    def _procesar_eventos(self):
        """Lee la cola de eventos de pygame."""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                self.serpiente.cambiar_direccion(evento.key)

    def _esperar_decision(self):
        """Pausa en Game Over hasta que el jugador elige R o Q."""
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

    def ejecutar(self):
        """Bucle principal: entrada → lógica → dibujo → repetir."""
        while True:
            # 1. Entrada
            self._procesar_eventos()

            # 2. Lógica
            self.serpiente.avanzar()

            if self.serpiente.choco():
                self.pantalla.mostrar_game_over(self.puntaje)
                if self._esperar_decision():
                    self._reiniciar()
                    continue

            if self.serpiente.cabeza == self.comida.posicion:
                self.serpiente.comer()
                self.puntaje += 10
                self.comida.reubicar(self.serpiente.cuerpo)

            # 3. Dibujo
            self.pantalla.limpiar()
            self.pantalla.dibujar_cuadricula()
            self.pantalla.dibujar_comida(self.comida)
            self.pantalla.dibujar_serpiente(self.serpiente)
            self.pantalla.dibujar_puntaje(self.puntaje)
            self.pantalla.mostrar()

            # 4. Velocidad
            self.reloj.tick(FPS)


# ─── Punto de entrada ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    juego = Juego()  # crea el objeto → llama a Juego.__init__()
    juego.ejecutar()  # arranca el bucle principal

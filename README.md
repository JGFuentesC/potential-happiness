# Potential Happiness 🐍

Material de apoyo para un curso introductorio de Python, usando el juego **Snake** como hilo conductor. El mismo juego se implementa dos veces: primero con Python básico (procedural) y luego con Programación Orientada a Objetos, para que los estudiantes puedan comparar ambos enfoques lado a lado.

## Archivos

| Archivo | Descripción |
|---|---|
| `snake.py` | Snake procedural — sin clases, solo funciones, listas y bucles |
| `snake_oo.py` | Snake orientado a objetos — clases, atributos, métodos, composición |

## Requisitos

- Python 3.8 o superior
- pygame

```bash
pip install -r requirements.txt
```

## Cómo ejecutar

```bash
python snake.py      # versión procedural
python snake_oo.py   # versión orientada a objetos
```

**Controles:** flechas del teclado para mover · `R` para reiniciar · `Q` para salir.

---

## Conceptos que se cubren

### `snake.py` — Python básico

| Concepto | Ejemplo en el código |
|---|---|
| Variables y constantes | `ANCHO`, `FPS`, `puntaje` |
| Tuplas | Colores `(R, G, B)`, posiciones `(x, y)` |
| Listas | El cuerpo de la serpiente `[(x,y), ...]` |
| Funciones | Una función por responsabilidad |
| `while` / `for` | Bucle principal y recorrido del cuerpo |
| `if` / `elif` / `else` | Cambio de dirección, detección de colisión |
| Slicing | `serpiente[:-1]`, `serpiente[1:]` |
| Operador `in` | Verificar si la cabeza toca el cuerpo |
| Módulos | `pygame`, `random`, `sys` |

### `snake_oo.py` — Orientado a Objetos

| Concepto | Dónde verlo |
|---|---|
| `class` e instancia | `class Serpiente:` → `Serpiente()` |
| Constructor `__init__` | Cada clase define el suyo |
| `self` | Primer parámetro de todo método de instancia |
| Atributos de instancia | `self.cuerpo`, `self.direccion`, `self.puntaje` |
| Métodos | `avanzar()`, `choco()`, `reubicar()` |
| Método "privado" (`_`) | `_posicion_libre()`, `_reiniciar()` |
| `@property` | `serpiente.cabeza` — parece atributo, es método |
| Encapsulamiento | Cada clase gestiona únicamente su propio estado |
| Composición | `Juego` contiene `Serpiente`, `Comida` y `Pantalla` |

### Comparación clave

```python
# Procedural (snake.py): los datos y las funciones están separados
serpiente = crear_serpiente()
serpiente = mover(serpiente, direccion)

# Orientado a objetos (snake_oo.py): los datos y el comportamiento viven juntos
serpiente = Serpiente()
serpiente.avanzar()
```

---

## Estructura de clases (`snake_oo.py`)

```
Juego
├── Pantalla   → inicializa pygame y dibuja todo
├── Serpiente  → posición, dirección, movimiento, colisión
└── Comida     → posición y reubicación
```

## Licencia

Consulta el archivo [LICENSE](LICENSE).

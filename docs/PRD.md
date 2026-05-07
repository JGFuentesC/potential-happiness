# PRD: Quiniela Mundial Norteamérica 2026 ⚽️

**Versión:** 1.1
**Status:** Ready for Development
**Stack:** FastAPI (Python), shadcn/ui (TypeScript), SQLite.
**Changelog v1.1:** Auditoría socrática — se agregan flujo de aprobación de cuentas, corrección de resultados con recálculo, fases eliminatorias con placeholder, y aclaraciones de bloqueo de bonus.

---

## 1. Resumen Ejecutivo
Plataforma web para gestionar una quiniela entre un grupo cerrado de amigos para el Mundial 2026. La aplicación permitirá predecir resultados de 104 partidos, gestionar rondas eliminatorias dinámicas y premiar el conocimiento futbolístico con un sistema de puntos por acierto y bonos por marcador exacto.

---

## 2. Definición de Roles

* **Participante (Aprobado):** Usuario que predice resultados, visualiza el ranking y consulta los resultados de sus amigos una vez bloqueados los partidos.
* **Participante (Pendiente):** Usuario registrado aún no aprobado por el Admin. Ve únicamente una pantalla de espera. No puede navegar ni predecir.
* **Administrador:** Único usuario con permisos para aprobar/rechazar cuentas, crear/editar partidos, cargar resultados reales, corregir resultados y validar las preguntas bonus.

---

## 3. Lógica de Negocio y Sistema de Puntos

### 3.1. Sistema de Puntuación
| Acción | Puntos | Descripción |
| :--- | :--- | :--- |
| **Acierto Tendencia (1X2)** | +3 pts | Acertar si gana local, empate o gana visitante. |
| **Acierto Exacto (Bonus)** | +2 pts | Adicional al anterior si se acierta el marcador exacto (Total 5 pts). |
| **Acierto Campeón** | +20 pts | Predicción realizada antes del inicio del mundial. |
| **Acierto Bota de Oro** | +15 pts | Predicción realizada antes del inicio del mundial. |

### 3.2. Reglas de Bloqueo
* **Partidos de grupos:** Las predicciones se cierran automáticamente **15 minutos antes** de la hora de inicio registrada en el sistema.
* **Partidos eliminatorios:** Las predicciones se habilitan solo cuando el Admin asigna los equipos reales al partido. El cierre sigue la misma regla de 15 minutos.
* **Preguntas Bonus:** Se bloquean automáticamente a la **hora programada** del partido inaugural del Mundial (no al pitazo real — se acepta el margen de retraso).
* **Visibilidad:** Un usuario **no puede ver** las predicciones de otros hasta que el partido esté `Locked`.

### 3.3. Criterio de Desempate en el Ranking
Cuando dos o más usuarios tienen los mismos `total_points`, el criterio de desempate es:
1. Mayor número de **marcadores exactos acertados** (`exact_scores`).
2. Si persiste el empate: orden **alfabético ascendente** por `username`.

---

## 4. Requisitos Funcionales

### 4.1. Módulo de Registro y Acceso
* **Registro abierto:** Cualquier persona puede registrarse con usuario y contraseña.
* **Aprobación manual:** La cuenta queda en estado `Pending` hasta que el Admin la aprueba. El usuario pendiente ve solo una pantalla: *"Tu cuenta está pendiente de aprobación. Avisa al administrador."*
* **Sin acceso parcial:** Un usuario pendiente no puede navegar ni interactuar con la app en ninguna forma.
* **Badge para el Admin:** El Admin Panel muestra un contador de usuarios pendientes. No se envían notificaciones automáticas — el flujo de aviso es manual (WhatsApp, etc.).

### 4.2. Módulo de Usuario (Participante Aprobado)
* Inicio de sesión (User/Password).
* Dashboard con lista de partidos agrupados por fase con filtros por fase y jornada.
* Input de predicciones (Goles Local / Goles Visitante) para partidos en estado `Open`.
* Partidos eliminatorios sin equipos definidos son visibles en estado `Pending Teams` (gris/bloqueado) desde el día 1 del torneo.
* Sección "Bonus": Selección de Campeón y Bota de Oro (disponible hasta el inicio del primer partido).
* Ranking en tiempo real con posiciones de todos los amigos aprobados.

### 4.3. Módulo de Administración

#### Gestión de Usuarios
* Vista de usuarios con filtro por estado: `Pending` / `Active` / `Rejected`.
* Badge con conteo de usuarios pendientes visible en todo el panel.
* Acciones: **Aprobar** (pasa a `Active`) o **Rechazar** (pasa a `Rejected`, no puede reintentar con el mismo username).

#### Gestión de Partidos
* Crear y editar fecha/hora de los 104 partidos.
* Para partidos eliminatorios: asignar equipos reales cuando clasifican (esto habilita las predicciones automáticamente).

#### Carga y Corrección de Resultados
* **Carga:** Input manual de marcadores finales. Al guardar, el sistema dispara el recálculo de puntos de todos los usuarios.
* **Corrección:** El Admin puede modificar un resultado ya cargado. El sistema muestra una advertencia de confirmación: *"Esto recalculará los puntos de N participantes para este partido. ¿Confirmar?"* Si el Admin confirma, el sistema recalcula y actualiza `total_points` y `exact_scores` de todos los usuarios afectados.

#### Validación de Bonus
* El Admin valida manualmente los resultados de Campeón y Bota de Oro al finalizar el torneo y asigna los puntos.

### 4.4. Feature Especial: "Time Travel"
Para propósitos de Testing E2E, todos los endpoints críticos que involucren validación de tiempo (`POST /predictions`, `GET /matches`) aceptarán un parámetro opcional `simulated_time`.
> Si el parámetro está presente, el backend usará esa fecha para validar si el partido está bloqueado o no, ignorando la hora real del servidor.

---

## 5. Estados de un Partido

| Estado | Condición | Puede predecir | Predicciones visibles |
| :--- | :--- | :--- | :--- |
| **Pending Teams** | Fase eliminatoria, sin equipos asignados | No | No |
| **Open** | `now < start_time - 15min` | Sí | No |
| **Locked** | `start_time - 15min ≤ now` y no Finished | No | Sí |
| **Finished** | Admin cargó resultado | No | Sí |

> `Pending Teams`, `Open` y `Locked` son estados **derivados** (calculados en tiempo real). Solo `Scheduled` y `Finished` se persisten en la base de datos.

---

## 6. Arquitectura de API REST (Endpoints Clave)

### Auth & Users
* `POST /auth/register` - Registro de usuarios (crea cuenta en estado `Pending`).
* `POST /auth/login` - Obtención de JWT (solo para usuarios `Active`).
* `GET /users/me` - Perfil y estadísticas personales.
* `GET /users/ranking` - Ranking de todos los usuarios activos.

### Matches & Predictions
* `GET /matches?phase=&group_name=&simulated_time=` - Lista partidos con estado derivado (Open/Locked/Finished/Pending Teams).
* `POST /predictions` - Enviar/Actualizar predicción (valida estado `Open`).
* `GET /predictions/match/{match_id}` - Ver predicciones de amigos (solo si `Locked` o `Finished`).

### Bonus
* `GET /bonus-questions` - Lista de preguntas especiales con estado de bloqueo.
* `POST /bonus-predictions` - Guardar respuestas (solo antes del inicio del mundial).

### Admin Only
* `GET /admin/users?status=Pending` - Lista de usuarios por estado.
* `POST /admin/users/{user_id}/approve` - Aprobar cuenta.
* `POST /admin/users/{user_id}/reject` - Rechazar cuenta.
* `POST /admin/matches` - Crear partido.
* `PUT /admin/matches/{match_id}` - Editar partido (fecha, equipos, etc.).
* `POST /admin/matches/{match_id}/result` - Cargar resultado (dispara recálculo).
* `PUT /admin/matches/{match_id}/result` - Corregir resultado (dispara recálculo con confirmación previa en frontend).
* `POST /admin/bonus-predictions/{user_id}/{question_type}/validate` - Validar bonus.

---

## 7. Modelo de Datos (SQLite)

### Tabla: `users`
* `id`, `username`, `password_hash`, `is_admin`, `status` (`Pending`/`Active`/`Rejected`), `total_points`, `exact_scores`.

### Tabla: `matches`
* `id`, `home_team` (nullable), `away_team` (nullable), `home_team_code`, `away_team_code`, `home_team_placeholder`, `away_team_placeholder`, `start_time`, `phase` (`Groups`/`R32`/`R16`/`QF`/`SF`/`ThirdPlace`/`Final`), `group_name`, `matchday`, `venue`, `home_score_final` (nullable), `away_score_final` (nullable), `status` (`Scheduled`/`Finished`).

### Tabla: `predictions`
* `id`, `user_id`, `match_id`, `home_score_guess`, `away_score_guess`, `points_earned` (nullable hasta resultado).

### Tabla: `bonus_predictions`
* `id`, `user_id`, `question_type` (`Champion`/`TopScorer`), `prediction_text`, `points_earned` (nullable).

---

## 8. UI/UX (Frontend con shadcn — Design System "Neon Tokyo")
* **Layout:** Sidebar fija para navegación (Partidos, Ranking, Bonus, Admin).
* **Match Card:** Banderas via `flagcdn.com`, inputs numéricos para goles, badge de estado (Open/Locked/Finished/Pending Teams). Partidos `Pending Teams` se muestran en gris con texto placeholder.
* **Leaderboard:** Tabla con `total_points` y `exact_scores` visibles. El 1° lugar con acento "Grandmaster" dorado.
* **Admin Panel:**
  * Badge de usuarios pendientes siempre visible.
  * Vista de gestión de usuarios (Aprobar/Rechazar).
  * Tabla de carga rápida de resultados.
  * Modal de confirmación antes de corregir un resultado ya cargado.

---

## 9. Consideraciones Técnicas
1. **Cálculo de Puntos:** No es dinámico en el `GET`. Los puntos se calculan y guardan en la DB cuando el Admin carga o corrige un resultado.
2. **Seguridad:** El backend valida que un usuario `Active` no pueda enviar una predicción si faltan menos de 15 minutos, incluso si el frontend no ha refrescado.
3. **Time Travel en Prod:** Protegido por variable de entorno `ENABLE_TIME_TRAVEL=True/False`.
4. **Bloqueo de Bonus:** Calculado comparando la hora actual con el `start_time` del partido con `id` más bajo (o el primer partido en la tabla por `start_time ASC`). No requiere campo especial.
5. **Corrección de Resultados:** Al recalcular, se recomputan `points_earned` en todas las `predictions` del partido y se recalculan `total_points` y `exact_scores` en todos los `users` afectados desde cero (suma de todos sus `predictions` con `points_earned NOT NULL`).

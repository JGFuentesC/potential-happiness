# Quiniela Mundial 2026

Aplicación de pronósticos para el Mundial de Fútbol Norteamérica 2026.
Los participantes predicen resultados, acumulan puntos y compiten en una tabla de posiciones en tiempo real.

---

## Stack

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.10+ · FastAPI · SQLAlchemy · SQLite |
| Autenticación | JWT (python-jose) · bcrypt |
| Frontend | TypeScript · React 18 · Vite · shadcn/ui · Tailwind CSS |
| Estado cliente | Zustand (persist) |
| Tests backend | pytest (95 tests) |
| Tests E2E | Playwright (11 tests) |

---

## Inicio rápido

```bash
# Levantar backend (puerto 8000) + frontend (puerto 5173)
./ctl.sh start

# Ver estado
./ctl.sh status

# Detener todo
./ctl.sh stop
```

| Servicio | URL |
|----------|-----|
| App | http://localhost:5173 |
| API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |

---

## Configuración

Copiar y completar las variables de entorno del backend:

```bash
cp backend/.env.example backend/.env
```

| Variable | Descripción | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Clave secreta para firmar JWT | — |
| `ALGORITHM` | Algoritmo JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiración del token | `10080` (7 días) |
| `DATABASE_URL` | Ruta de la base de datos SQLite | `sqlite:///./quiniela.db` |
| `ENABLE_TIME_TRAVEL` | Habilitar simulación temporal para E2E | `False` |
| `TOURNAMENT_KICKOFF` | Datetime del partido inaugural (ISO 8601) | `2026-06-11T20:00:00` |
| `ADMIN_USERNAME` | Username del admin inicial | — |
| `ADMIN_PASSWORD` | Password del admin inicial | — |

### Seed inicial

```bash
cd backend
source .venv/bin/activate
python seed_matches.py   # Carga los 72 partidos de la fase de grupos
python seed_admin.py     # Crea el usuario admin desde ADMIN_USERNAME/ADMIN_PASSWORD
```

---

## Documentación

| Documento | Descripción |
|-----------|-------------|
| [docs/api/openapi.yaml](docs/api/openapi.yaml) | Especificación OpenAPI 3.0 completa |
| [docs/architecture/diagrams.md](docs/architecture/diagrams.md) | Diagramas de arquitectura, flujos y estados (Mermaid) |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Arquitectura detallada, esquema de DB y contratos de API |
| [docs/DESIGN.md](docs/DESIGN.md) | Sistema de diseño visual (paleta Neon Tokyo, tipografía) |
| [docs/PRD.md](docs/PRD.md) | Product Requirements Document |
| [docs/plan.md](docs/plan.md) | Plan de implementación por fases |
| [docs/system-heartbeat.md](docs/system-heartbeat.md) | Estado actual del proyecto y decisiones técnicas |
| [docs/test-evidence.md](docs/test-evidence.md) | Evidencia de QA (pytest + Playwright) |
| [docs/er-diagram.mmd](docs/er-diagram.mmd) | Diagrama entidad-relación de la base de datos |

---

## Reglas de Negocio

### Puntuación

| Resultado | Puntos |
|-----------|--------|
| Tendencia correcta (1X2) | +3 |
| Bono marcador exacto | +2 |
| **Total máximo por partido** | **5** |

El desempate en el ranking se resuelve por: `total_points DESC → exact_scores DESC → username ASC`.

### Bloqueo de predicciones

Las predicciones se cierran **15 minutos antes** del `start_time` del partido.
El estado `Locked` se calcula en runtime — no se persiste en la base de datos.

### Privacidad

Las predicciones de otros jugadores solo son visibles cuando el partido está en estado `Locked` o `Finished`.

### Bonus

Dos preguntas con respuesta de texto libre:
- **Campeón del Mundial** → 20 puntos (validación manual por Admin)
- **Bota de Oro** → 15 puntos (validación manual por Admin)

Se bloquean al inicio del partido inaugural (`TOURNAMENT_KICKOFF`).

### Flujo de usuarios

```
Registro → Pending → (Admin aprueba) → Active
                   → (Admin rechaza) → Rejected
```

Los usuarios `Pending` no pueden iniciar sesión.

---

## Desarrollo

### Backend

```bash
cd backend
uv venv .venv && uv pip install -e ".[dev]"
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Tests
pytest -v

# Linting
flake8 app/ && black app/
```

### Frontend

```bash
cd frontend
npm install
npm run dev      # Desarrollo (HMR)
npm run build    # Build de producción
npm run lint     # ESLint + TypeScript check
```

### Tests E2E (Playwright)

Requiere backend + frontend corriendo:

```bash
# Desde /frontend
npx playwright test

# O desde la raíz con ctl.sh
./qa.sh
```

---

## Estado del proyecto

Ver [docs/system-heartbeat.md](docs/system-heartbeat.md) para el estado actualizado de cada fase y las decisiones técnicas tomadas.

**Suite pytest:** 95/95 tests pasando
**Suite Playwright E2E:** 11/11 tests pasando

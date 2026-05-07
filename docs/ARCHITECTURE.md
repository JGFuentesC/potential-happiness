# Architecture — Quiniela Mundial 2026

**Generado por:** Skill `architect` (con correcciones de `research.md`)  
**Fecha:** 2026-04-29  
**Stack:** FastAPI (Python 3.10+) · SQLite · React/Vite/shadcn/ui

> **Nota de corrección aplicada:** El skill `architect` tiene hardcodeado Go+GCP como stack por defecto.
> Este documento usa el stack autorizado en `CLAUDE.md`: FastAPI + SQLite.

---

## 1. Topología del Sistema

```
┌─────────────────────────────────────────────────────┐
│  Browser                                             │
│  React (Vite) · shadcn/ui · Tailwind · Zustand      │
│  Puerto: 5173 (dev) / build estático (prod)          │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP/JSON (JWT en header)
                       │ localhost:8000
┌──────────────────────▼──────────────────────────────┐
│  FastAPI (Python 3.10+)                              │
│  uvicorn · JWT (python-jose) · bcrypt                │
│  Puerto: 8000                                        │
└──────────────────────┬──────────────────────────────┘
                       │ SQLAlchemy ORM
┌──────────────────────▼──────────────────────────────┐
│  SQLite                                              │
│  quiniela.db (local) / quiniela_test.db (tests)      │
└─────────────────────────────────────────────────────┘
```

---

## 2. Estructura de Carpetas

```
/backend
├── app/
│   ├── main.py              # FastAPI app, CORS, montaje de routers
│   ├── database.py          # Engine SQLite, SessionLocal, Base, get_db()
│   ├── models.py            # ORM: User, Match, Prediction, BonusPrediction
│   ├── schemas.py           # Pydantic: request/response por entidad
│   ├── auth.py              # Hash bcrypt, crear/verificar JWT
│   ├── time_utils.py        # get_reference_time(), compute_match_status()
│   ├── scoring.py           # calculate_points(), recalculate_user_totals()
│   └── routers/
│       ├── auth.py          # POST /auth/register · POST /auth/login
│       ├── users.py         # GET /users/me · GET /users/ranking
│       ├── matches.py       # GET /matches · GET /matches/{id}
│       ├── predictions.py   # POST /predictions · GET /predictions/match/{id}
│       ├── bonus.py         # GET /bonus-questions · POST /bonus-predictions
│       └── admin.py         # Rutas admin-only (requires_admin dependency)
├── tests/
│   ├── conftest.py          # Fixtures: DB en memoria, cliente test, usuarios
│   ├── test_auth.py
│   ├── test_matches.py
│   ├── test_predictions.py  # Incluye tests de Time Travel
│   ├── test_scoring.py      # Unit tests del algoritmo de puntos (sin DB)
│   └── test_admin.py
├── pyproject.toml           # Dependencias con uv
└── .env.example

/frontend
├── src/
│   ├── main.tsx
│   ├── App.tsx              # React Router: rutas protegidas + layout
│   ├── api/
│   │   └── client.ts        # Axios instance; adjunta JWT; maneja 401
│   ├── types/
│   │   └── index.ts         # Interfaces: Match, Prediction, User, BonusQuestion
│   ├── store/
│   │   └── authStore.ts     # Zustand: { user, token, login(), logout() }
│   ├── components/
│   │   ├── ui/              # Componentes shadcn (Button, Input, Badge, etc.)
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx
│   │   │   └── AppHeader.tsx
│   │   ├── MatchCard.tsx    # Card de partido con inputs de predicción
│   │   ├── StatusBadge.tsx  # Badge Open/Locked/Finished
│   │   └── FlagAvatar.tsx   # Avatar de bandera vía flagcdn.com
│   └── pages/
│       ├── Login.tsx
│       ├── Matches.tsx      # Dashboard principal
│       ├── Leaderboard.tsx
│       ├── Bonus.tsx
│       └── Admin.tsx
├── package.json
├── vite.config.ts
└── tailwind.config.ts       # Paleta "Neon Tokyo" + fuentes Sora/Space Grotesk
```

---

## 3. Esquema de Base de Datos (SQLite)

### Decisiones de diseño aplicadas desde `research.md`

**§6.4 — Estado `Locked`:** No se almacena en DB. Se calcula dinámicamente en `time_utils.py` comparando `reference_time >= start_time - 15min`. La DB solo persiste `Scheduled` y `Finished`. Evita jobs periódicos.

**§6.5 — Equipos dinámicos en eliminatoria:** Columnas `*_team` son nullable. Se agregan columnas `*_team_placeholder` para mostrar texto ("1° Grupo A") mientras los equipos no están definidos.

**§6.6 — Desempate en ranking:** Se agrega `exact_scores` a `users`. Criterio de ordenamiento: `total_points DESC, exact_scores DESC, username ASC`.

```sql
-- Tabla: users
CREATE TABLE users (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    username         TEXT    NOT NULL UNIQUE,
    password_hash    TEXT    NOT NULL,
    is_admin         INTEGER NOT NULL DEFAULT 0,  -- 0=participante, 1=admin
    total_points     INTEGER NOT NULL DEFAULT 0,
    exact_scores     INTEGER NOT NULL DEFAULT 0,  -- desempate visual
    created_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: matches
-- Phase values: 'Groups' | 'R32' | 'R16' | 'QF' | 'SF' | 'ThirdPlace' | 'Final'
-- Status values: 'Scheduled' | 'Finished'  (Locked es derivado, no almacenado)
-- Distribución: 72 grupos + 16 R32 + 8 R16 + 4 QF + 2 SF + 1 ThirdPlace + 1 Final = 104
CREATE TABLE matches (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    home_team               TEXT,        -- nullable en fases eliminatorias
    away_team               TEXT,        -- nullable en fases eliminatorias
    home_team_code          TEXT,        -- ISO 3166-1 alpha-2, ej. "us", "mx"
    away_team_code          TEXT,        -- para construir URL de bandera
    home_team_placeholder   TEXT,        -- ej. "1° Grupo A" cuando team es null
    away_team_placeholder   TEXT,
    start_time              DATETIME NOT NULL,
    phase                   TEXT NOT NULL,
    group_name              TEXT,        -- 'A'–'L' solo en fase de Grupos
    matchday                INTEGER,     -- 1, 2, 3 solo en fase de Grupos
    venue                   TEXT,
    home_score_final        INTEGER,     -- null hasta que Admin cargue resultado
    away_score_final        INTEGER,
    status                  TEXT NOT NULL DEFAULT 'Scheduled',
    created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: predictions
CREATE TABLE predictions (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id           INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    match_id          INTEGER NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    home_score_guess  INTEGER NOT NULL,
    away_score_guess  INTEGER NOT NULL,
    points_earned     INTEGER,          -- null hasta que Admin cargue resultado
    created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, match_id)
);

-- Tabla: bonus_predictions
-- question_type values: 'Champion' | 'TopScorer'
CREATE TABLE bonus_predictions (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    question_type    TEXT NOT NULL,
    prediction_text  TEXT NOT NULL,
    points_earned    INTEGER,           -- null hasta validación manual del Admin
    created_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, question_type)
);
```

---

## 4. Contratos de API REST

### Base URL: `http://localhost:8000`
### Auth: `Authorization: Bearer <JWT>` en todos los endpoints protegidos

---

### 4.1 Auth

#### `POST /auth/register`
```json
// Request
{ "username": "gus", "password": "secret123" }

// Response 201
{ "id": 1, "username": "gus" }

// Error 400 si username ya existe
{ "detail": "Username already registered" }
```

#### `POST /auth/login`
```json
// Request
{ "username": "gus", "password": "secret123" }

// Response 200
{ "access_token": "eyJ...", "token_type": "bearer" }

// Error 401
{ "detail": "Incorrect username or password" }
```

---

### 4.2 Usuarios

#### `GET /users/me` — Auth requerida
```json
// Response 200
{
  "id": 1,
  "username": "gus",
  "is_admin": false,
  "total_points": 47,
  "exact_scores": 3,
  "rank": 2
}
```

#### `GET /users/ranking` — Auth requerida
```json
// Response 200 — ordenado: total_points DESC, exact_scores DESC, username ASC
[
  { "rank": 1, "user_id": 2, "username": "ale", "total_points": 52, "exact_scores": 4 },
  { "rank": 2, "user_id": 1, "username": "gus", "total_points": 47, "exact_scores": 3 }
]
```

---

### 4.3 Partidos

#### `GET /matches` — Auth requerida
```
Query params:
  phase         string  opcional  filtrar por fase ('Groups', 'R32', etc.)
  group_name    string  opcional  filtrar por grupo ('A'–'L')
  simulated_time string  opcional  ISO 8601, Time Travel (requiere ENABLE_TIME_TRAVEL=true)
```
```json
// Response 200 — status es COMPUTADO, no almacenado
[
  {
    "id": 1,
    "home_team": "USA",
    "away_team": "Mexico",
    "home_team_code": "us",
    "away_team_code": "mx",
    "home_team_placeholder": null,
    "away_team_placeholder": null,
    "start_time": "2026-06-11T20:00:00Z",
    "phase": "Groups",
    "group_name": "A",
    "matchday": 1,
    "venue": "SoFi Stadium",
    "status": "Open",
    "home_score_final": null,
    "away_score_final": null,
    "my_prediction": {
      "home_score_guess": 2,
      "away_score_guess": 1,
      "points_earned": null
    }
  },
  {
    "id": 49,
    "home_team": null,
    "away_team": null,
    "home_team_code": null,
    "away_team_code": null,
    "home_team_placeholder": "1° Grupo A",
    "away_team_placeholder": "2° Grupo B",
    "start_time": "2026-07-02T20:00:00Z",
    "phase": "R32",
    "group_name": null,
    "matchday": null,
    "status": "Open",
    "home_score_final": null,
    "away_score_final": null,
    "my_prediction": null
  }
]
```

---

### 4.4 Predicciones

#### `POST /predictions` — Auth requerida
```json
// Request
{
  "match_id": 1,
  "home_score_guess": 2,
  "away_score_guess": 1,
  "simulated_time": "2026-06-11T19:00:00"  // opcional, Time Travel
}

// Response 200 (crea o actualiza — upsert por user_id+match_id)
{
  "id": 42,
  "match_id": 1,
  "home_score_guess": 2,
  "away_score_guess": 1,
  "points_earned": null,
  "created_at": "2026-04-29T14:00:00Z",
  "updated_at": "2026-04-29T14:00:00Z"
}

// Error 403 si el partido ya está Locked o Finished
{ "detail": "Match is locked. Predictions closed." }
```

#### `GET /predictions/match/{match_id}` — Auth requerida
```json
// Solo accesible si match.status == 'Locked' o 'Finished'

// Response 200
[
  { "username": "gus", "home_score_guess": 2, "away_score_guess": 1, "points_earned": 5 },
  { "username": "ale", "home_score_guess": 1, "away_score_guess": 0, "points_earned": 0 }
]

// Error 403 si el partido aún está Open
{ "detail": "Predictions are only visible after the match is locked." }
```

---

### 4.5 Bonus

#### `GET /bonus-questions` — Auth requerida
```json
// Response 200
[
  {
    "question_type": "Champion",
    "question_text": "¿Quién será el Campeón del Mundial 2026?",
    "points_reward": 20,
    "is_locked": false,
    "my_prediction": "Argentina"  // null si no ha predicho
  },
  {
    "question_type": "TopScorer",
    "question_text": "¿Quién ganará la Bota de Oro?",
    "points_reward": 15,
    "is_locked": false,
    "my_prediction": null
  }
]
```

#### `POST /bonus-predictions` — Auth requerida
```json
// Request
{ "question_type": "Champion", "prediction_text": "Argentina" }

// Response 200
{ "question_type": "Champion", "prediction_text": "Argentina", "points_earned": null }

// Error 403 si bonus está bloqueado (inicio del mundial)
{ "detail": "Bonus predictions are locked." }
```

---

### 4.6 Admin (requiere is_admin=true en JWT)

#### `POST /admin/matches` — Crear partido
```json
// Request
{
  "home_team": "USA", "away_team": "Mexico",
  "home_team_code": "us", "away_team_code": "mx",
  "home_team_placeholder": null, "away_team_placeholder": null,
  "start_time": "2026-06-11T20:00:00Z",
  "phase": "Groups", "group_name": "A", "matchday": 1,
  "venue": "SoFi Stadium"
}
// Response 201: objeto Match completo
```

#### `PUT /admin/matches/{match_id}` — Editar partido (fecha/hora, equipos)
```json
// Request: campos a actualizar (parcial)
{ "start_time": "2026-06-11T21:00:00Z" }
// Response 200: objeto Match actualizado
```

#### `POST /admin/matches/{match_id}/result` — Cargar resultado ⚡ dispara recálculo
```json
// Request
{ "home_score_final": 2, "away_score_final": 1 }

// Lógica ejecutada sincrónicamente:
// 1. UPDATE matches SET home_score_final, away_score_final, status='Finished'
// 2. Para cada prediction del partido: calcular points_earned, UPDATE
// 3. Recalcular total_points y exact_scores de todos los users afectados

// Response 200
{
  "match_id": 1,
  "home_score_final": 2,
  "away_score_final": 1,
  "predictions_updated": 8
}
```

#### `POST /admin/bonus-predictions/{user_id}/{question_type}/validate`
```json
// Request
{ "points_earned": 20 }
// Response 200: objeto bonus_prediction actualizado
```

---

## 5. Lógica Crítica de Negocio

### 5.1 `time_utils.py` — Time Travel

```python
from datetime import datetime
import os

LOCK_WINDOW_MINUTES = 15

def get_reference_time(simulated_time: str | None = None) -> datetime:
    if simulated_time and os.getenv("ENABLE_TIME_TRAVEL") == "True":
        return datetime.fromisoformat(simulated_time)
    return datetime.utcnow()

def compute_match_status(match_start: datetime, db_status: str, ref_time: datetime) -> str:
    if db_status == "Finished":
        return "Finished"
    lock_threshold = match_start - timedelta(minutes=LOCK_WINDOW_MINUTES)
    if ref_time >= lock_threshold:
        return "Locked"
    return "Open"

def is_prediction_allowed(match_start: datetime, db_status: str, ref_time: datetime) -> bool:
    return compute_match_status(match_start, db_status, ref_time) == "Open"
```

### 5.2 `scoring.py` — Algoritmo de Puntos

```python
def calculate_prediction_points(
    home_guess: int, away_guess: int,
    home_final: int, away_final: int
) -> int:
    def tendency(h: int, a: int) -> str:
        if h > a: return "home"
        if h < a: return "away"
        return "draw"

    if tendency(home_guess, away_guess) != tendency(home_final, away_final):
        return 0

    points = 3  # acierto de tendencia
    if home_guess == home_final and away_guess == away_final:
        points += 2  # bono marcador exacto
    return points

def recalculate_user_totals(db: Session, user_id: int) -> None:
    result = db.execute(
        "SELECT COALESCE(SUM(points_earned), 0), "
        "COUNT(*) FILTER (WHERE points_earned = 5) "
        "FROM predictions WHERE user_id = :uid AND points_earned IS NOT NULL",
        {"uid": user_id}
    ).fetchone()
    db.execute(
        "UPDATE users SET total_points = :pts, exact_scores = :ex WHERE id = :uid",
        {"pts": result[0], "ex": result[1], "uid": user_id}
    )
```

### 5.3 Bloqueo de Bonus

Las bonus questions se bloquean en el pitazo inicial del partido inaugural. El backend debe tener configurada la `datetime` del primer partido. Implementación: el Admin puede crear un registro especial en `matches` con `phase='Opening'`, o bien configurar una variable de entorno `TOURNAMENT_KICKOFF=2026-06-11T20:00:00Z`.

**Decisión elegida:** usar `TOURNAMENT_KICKOFF` como env var — más simple que un registro especial en DB.

---

## 6. Flags de Banderas

**Estrategia:** `https://flagcdn.com/w80/{code}.png` donde `code` es el campo `home_team_code` / `away_team_code` (ISO 3166-1 alpha-2).

```tsx
// FlagAvatar.tsx
const FlagAvatar = ({ code, name }: { code: string | null; name: string | null }) => {
  if (!code) return <div className="w-16 h-16 rounded-full bg-surface-variant" />;
  return (
    <img
      src={`https://flagcdn.com/w80/${code}.png`}
      alt={name ?? "TBD"}
      className="w-16 h-16 rounded-full object-cover border-2 border-outline-variant"
    />
  );
};
```

---

## 7. Variables de Entorno

### `/backend/.env.example`
```env
SECRET_KEY=changeme-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
DATABASE_URL=sqlite:///./quiniela.db
ENABLE_TIME_TRAVEL=False
TOURNAMENT_KICKOFF=2026-06-11T20:00:00
```

---

## 8. Dependencias

### Backend (`pyproject.toml`)
```toml
[project]
name = "quiniela-backend"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.111",
    "uvicorn[standard]>=0.29",
    "sqlalchemy>=2.0",
    "pydantic>=2.0",
    "python-jose[cryptography]>=3.3",
    "passlib[bcrypt]>=1.7",
    "python-multipart>=0.0.9",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "httpx>=0.27",
    "pytest-asyncio>=0.23",
]
```

### Frontend (`package.json` clave)
```json
{
  "dependencies": {
    "react": "^18",
    "react-dom": "^18",
    "react-router-dom": "^6",
    "axios": "^1.6",
    "zustand": "^4",
    "@radix-ui/react-*": "latest"
  },
  "devDependencies": {
    "vite": "^5",
    "@vitejs/plugin-react": "^4",
    "typescript": "^5",
    "tailwindcss": "^3",
    "@playwright/test": "^1.44"
  }
}
```

---

## 9. `.gitignore` Completo

El `.gitignore` actual solo ignora `.env` y `.envrc`. Debe expandirse:

```gitignore
# Env
.env
.envrc

# Python
__pycache__/
*.pyc
*.pyo
.venv/
*.egg-info/

# DB
*.db
*.sqlite
*.sqlite3

# Frontend
node_modules/
dist/
.vite/

# Tests
.pytest_cache/
htmlcov/
.coverage

# Claude Code
.claude/settings.local.json

# OS
.DS_Store
```

---

## 10. Puntos Abiertos para el Tech Lead

1. **Seed de los 104 partidos:** ¿El Admin los crea desde el panel uno a uno, o existe un script de seed inicial con los partidos de grupos (los únicos conocidos hoy)? **Recomendación:** script de seed en `backend/seed_matches.py` para los 72 de grupos; Admin crea eliminatorias dinámicamente.

2. **Usuario Admin inicial:** ¿Se crea via seed o hay un endpoint de bootstrap protegido? **Recomendación:** seed script que crea un usuario admin desde `ADMIN_USERNAME` / `ADMIN_PASSWORD` env vars.

3. **Paginación en `/matches`:** 104 partidos pueden volver pesado el listado. Para MVP no es bloqueante, pero el `tech-lead` debe decidir si incluir paginación en la primera fase.

4. **CORS en producción:** Si backend y frontend se sirven desde el mismo origen en prod (static build servido por FastAPI), CORS puede eliminarse. Para dev local es necesario.

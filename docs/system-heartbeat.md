# System Heartbeat — Quiniela Mundial 2026

**Última actualización:** 2026-05-06  
**Rama activa:** `quiniela`  
**Estado general:** ✅ Todas las fases completadas — pendiente visto bueno final del usuario

---

## 1. Resumen de Estado

| Fase | Descripción | Estado |
|---|---|---|
| Fase 0 | Setup backend + frontend scaffold | ✅ Completada |
| Fase 1 | Backend cimientos (models, auth, time_utils, scoring) | ✅ Completada |
| Fase 2 | Backend endpoints (todos los routers) | ✅ Completada |
| Fase 3 | Seed scripts (partidos + admin) | ✅ Completada |
| Fase 4 | Frontend cimientos (auth flow, layout, types) | ✅ Completada |
| Fase 5 | Frontend features (Matches, Leaderboard, Bonus, Admin) | ✅ Completada |
| Fase 6 | QA Final (pytest completo + Playwright E2E) | ✅ Completada |

---

## 2. Árbol de Archivos Actual

```
potential-happiness/
├── ctl.sh                   ✅ Control de servidores
├── qa.sh                    ✅ QA completo (pytest + Playwright + test-evidence.md)
├── backend/
│   ├── app/
│   │   ├── main.py              ✅ FastAPI app + CORS + routers montados
│   │   ├── database.py          ✅ SQLAlchemy engine SQLite + get_db()
│   │   ├── models.py            ✅ User, Match, Prediction, BonusPrediction
│   │   ├── schemas.py           ✅ Todos los schemas Pydantic (request/response)
│   │   ├── auth.py              ✅ bcrypt directo (sin passlib), JWT python-jose
│   │   ├── time_utils.py        ✅ Time Travel + compute_match_status()
│   │   ├── scoring.py           ✅ calculate_prediction_points() + recalculate_*()
│   │   └── routers/
│   │       ├── auth.py          ✅ POST /auth/register, /auth/login
│   │       ├── users.py         ✅ GET /users/me, /users/ranking
│   │       ├── matches.py       ✅ GET /matches, /matches/{id}
│   │       ├── predictions.py   ✅ POST /predictions, GET /predictions/match/{id}
│   │       ├── bonus.py         ✅ GET /bonus-questions, POST /bonus-predictions
│   │       └── admin.py         ✅ Todos los endpoints admin
│   ├── tests/
│   │   ├── conftest.py          ✅
│   │   ├── test_models.py       ✅ 6 tests
│   │   ├── test_auth.py         ✅ 12 tests
│   │   ├── test_time_utils.py   ✅ 15 tests
│   │   ├── test_scoring.py      ✅ 13 tests
│   │   ├── test_matches.py      ✅ 12 tests
│   │   ├── test_predictions.py  ✅ 12 tests
│   │   ├── test_bonus.py        ✅ 9 tests
│   │   └── test_admin.py        ✅ 15 tests
│   ├── seed_matches.py          ✅ 72 partidos de grupos (idempotente)
│   ├── seed_admin.py            ✅ Usuario admin desde env vars (idempotente)
│   ├── pyproject.toml           ✅
│   └── .env.example             ✅
├── frontend/
│   ├── src/
│   │   ├── App.tsx              ✅ BrowserRouter + Routes (login + protected layout)
│   │   ├── main.tsx             ✅
│   │   ├── index.css            ✅ @import antes de @tailwind (fix PostCSS)
│   │   ├── types/
│   │   │   └── index.ts         ✅ Match, User, Prediction, Bonus, Admin interfaces
│   │   ├── api/
│   │   │   └── client.ts        ✅ axios + interceptors JWT + todas las funciones API
│   │   ├── store/
│   │   │   └── authStore.ts     ✅ Zustand persist: user, token, login(), logout()
│   │   ├── pages/
│   │   │   ├── Login.tsx        ✅ Login + Register + pantalla Pending
│   │   │   ├── Matches.tsx      ✅ Grid bento, 4 estados, banderas, save animation
│   │   │   ├── Leaderboard.tsx  ✅ Tabla ranking, Grandmaster gold, usuario resaltado
│   │   │   ├── Bonus.tsx        ✅ 2 cards Champion/TopScorer, locked state
│   │   │   └── Admin.tsx        ✅ Tab Usuarios + Tab Partidos + modal confirmación
│   │   └── components/
│   │       ├── layout/
│   │       │   ├── ProtectedLayout.tsx ✅ Guard → /login + Outlet context
│   │       │   ├── Sidebar.tsx         ✅ w-64 fixed, nav items, active #ff2d78, mobile drawer
│   │       │   └── AppHeader.tsx       ✅ Time Travel toggle (admin), user chip
│   │       └── ui/              ✅ shadcn components
│   ├── tailwind.config.js       ✅ Paleta Neon Tokyo
│   ├── tsconfig.app.json        ✅ path alias @/*
│   ├── vite.config.ts           ✅ path alias @/*
│   ├── playwright.config.ts     ✅ Config E2E (chromium, screenshots en docs/screenshots/)
│   ├── e2e/
│   │   └── quiniela.spec.ts      ✅ 11 tests E2E (T1–T11): auth, predicciones, admin, logout
├── docs/
│   ├── PRD.md                   ✅
│   ├── ARCHITECTURE.md          ✅
│   ├── DESIGN.md                ✅
│   ├── plan.md                  ✅
│   └── system-heartbeat.md      ✅ (este archivo)
├── ui-inspo/                    ✅ Mockups HTML para las 4 vistas principales
├── .skills/                     ✅
├── .gitignore                   ✅
└── CLAUDE.md                    ✅
```

---

## 3. Evidencia de Tests

### Suite pytest — 95/95 ✅
```
tests/test_models.py        6 passed
tests/test_auth.py         12 passed
tests/test_time_utils.py   15 passed
tests/test_scoring.py      13 passed
tests/test_matches.py      12 passed
tests/test_predictions.py  12 passed
tests/test_bonus.py         9 passed
tests/test_admin.py        15 passed
─────────────────────────────────────
TOTAL                      95 passed, 271 warnings in 52.79s
```

### Suite Playwright E2E — 11/11 ✅
```
T1  – Redirect a /login sin autenticación           ✓  1.1s
T2  – Registro + pantalla Pending                   ✓  1.7s
T3  – Admin login UI → /matches                     ✓  3.0s
T4  – Admin aprueba usuario Pending                 ✓  3.6s
T5  – Matches page: tabs, cards, grupos             ✓  5.8s
T6  – Guardar predicción en partido Open            ✓  5.5s
T7  – Leaderboard page                              ✓  3.1s
T8  – Bonus page: cards y save                      ✓  5.2s
T9  – Time Travel toggle (solo admin)               ✓  3.9s
T10 – Admin carga resultado de partido              ✓  7.2s
T11 – Logout y redirect a /login                    ✓  2.6s
─────────────────────────────────────────────────────────────
11 passed (44.6s) | 20 screenshots en docs/screenshots/
```

Evidencia completa: `docs/test-evidence.md`

---

## 4. Cómo Levantar el Sistema

### Con ctl.sh (recomendado)
```bash
./ctl.sh start          # Levanta backend (puerto 8000) + frontend (puerto 5173)
./ctl.sh status         # Ver estado de ambos
./ctl.sh logs back      # Logs del backend en tiempo real
./ctl.sh logs front     # Logs del frontend en tiempo real
./ctl.sh restart back   # Reiniciar solo el backend
./ctl.sh stop           # Detener todo
```
PIDs y logs en `.run/`

### Comandos manuales (alternativa)
```bash
# Backend
cd backend && source .venv/bin/activate
.venv/bin/uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm run dev
```
API: `http://localhost:8000` | Swagger: `http://localhost:8000/docs` | App: `http://localhost:5173`

---

## 5. Decisiones Técnicas Críticas Tomadas

| Decisión | Resolución | Archivo |
|---|---|---|
| Estado `Locked` | Derivado en runtime, no persistido en DB | `app/time_utils.py` |
| bcrypt | `bcrypt` directo (sin `passlib`) | `app/auth.py` |
| SQLite in-memory en tests | `StaticPool` | `tests/conftest.py` |
| Estado `Pending` users | Registro abierto → Admin aprueba | `app/routers/auth.py` |
| Equipos knockout | `home_team`/`away_team` nullable | `app/models.py` |
| Desempate ranking | `total_points DESC, exact_scores DESC, username ASC` | `app/routers/users.py` |
| Tailwind + shadcn | Tailwind v3 (v4 incompatible con shadcn) | `tailwind.config.js` |
| Zustand persist | `partialize` (v5 API) — no `partialState` | `store/authStore.ts` |
| CSS import order | `@import` antes de `@tailwind` — requerido por PostCSS | `index.css` |
| simulatedTime | Vive en `ProtectedLayout` y se pasa via Outlet context | `ProtectedLayout.tsx` |

---

## 6. Variables de Entorno Requeridas

```env
SECRET_KEY=<string-largo-aleatorio>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
DATABASE_URL=sqlite:///./quiniela.db
ENABLE_TIME_TRAVEL=False
TOURNAMENT_KICKOFF=2026-06-11T20:00:00
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<password-seguro>
```

---

## 7. Próximos Pasos

**El proyecto está completo.** Toda la evidencia de QA está en `docs/test-evidence.md`.

Pendiente únicamente: visto bueno final del usuario para marcar el proyecto como DONE.

Si se necesitan ajustes post-QA (deploy, variables de producción, etc.), definirlos como Fase 7.

---

## 8. Advertencias Conocidas

1. **`DeprecationWarning: datetime.utcnow()`** en Python 3.13 — no bloqueante.
2. **IDE warnings** en backend — el IDE no apunta al `.venv` del proyecto.
3. **Grupos del Mundial** en `seed_matches.py` — verificar equipos antes del torneo.
4. **CORS** — habilitado para `localhost:5173`. Revisar antes de deploy.
5. **`dist/`** — generado por `npm run build`, ignorado por `.gitignore`.
6. **Admin page** — solo muestra partidos de Groups en el tab Partidos.
7. **CORS** — `allow_origins` incluye `localhost:5173`, `127.0.0.1:5173`, `localhost:4173`, `127.0.0.1:4173`. El `vite preview` usa la variante `127.0.0.1`.
8. **Password admin** — definido en `backend/.env` como `ADMIN_PASSWORD=changeme-admin`. El `.env` se creó a partir de `.env.example`; ejecutar `seed_admin.py` antes del primer uso.
9. **`ctl.sh` frontend** — usa `npm run build` + `vite preview --port 5173` (prod build). Limpia puertos 8000/5173 automáticamente al iniciar.
10. **`.venv` backend** — creado con `uv venv .venv && uv pip install -e ".[dev]"` en `/backend`.

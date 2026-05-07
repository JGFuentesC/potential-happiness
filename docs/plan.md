# Implementation Plan — Quiniela Mundial 2026

## Estado del Proyecto
- [ ] Planning (En discusión)
- [ ] Approved (Listo para código)
- [ ] In Progress
- [ ] Done

---

## Arquitectura Refinada

**Stack autorizado:** FastAPI (Python 3.10+) · SQLite · React/Vite/shadcn/ui · Tailwind

### Decisiones Técnicas Críticas

| Decisión | Resolución |
|---|---|
| Estado `Locked` | Derivado en runtime por `time_utils.py`. DB solo persiste `Scheduled`/`Finished`. |
| Equipos eliminatorios | Columnas `*_team` nullable + `*_team_placeholder`. Predicciones abren cuando Admin asigna equipos. |
| Desempate ranking | `total_points DESC, exact_scores DESC, username ASC` |
| Bloqueo bonus | Automático al `start_time` del partido con `start_time` más bajo en DB. |
| Banderas | `flagcdn.com/w80/{code}.png` via campo `*_team_code` (ISO 3166-1 alpha-2). |
| Corrección de resultados | Admin puede corregir con confirmación → recalcular `points_earned` de predictions + `total_points`/`exact_scores` de users. |
| Registro y acceso | Registro abierto → estado `Pending` → Admin aprueba desde panel (badge sin email). |
| Paginación `/matches` | No para MVP. Los 104 partidos se retornan completos con filtros por `phase`/`group_name`. |
| Admin inicial | Seed script lee `ADMIN_USERNAME`/`ADMIN_PASSWORD` de env vars. |
| Seed partidos | Script `backend/seed_matches.py` para 72 partidos de grupos. Admin crea eliminatorias dinámicamente. |
| CORS | Habilitado en desarrollo (localhost:5173 → localhost:8000). Evaluar en producción. |
| Time Travel en prod | Protegido por `ENABLE_TIME_TRAVEL=False`. Solo activar en entorno de testing. |

### Referencias de Diseño Frontend

| Artefacto | Ruta | Uso |
|---|---|---|
| Design System "Neon Tokyo" | `docs/DESIGN.md` | Paleta, tipografía, principios visuales |
| Mockup Matches Dashboard | `ui-inspo/matches_dashboard/` | Layout sidebar + match cards + inputs |
| Mockup Admin Panel | `ui-inspo/admin_panel/` | Tabla de resultados + Time Travel toggle |
| Mockup Leaderboard | `ui-inspo/leaderboard/` | Tabla de ranking + acento Grandmaster |
| Mockup Bonus | `ui-inspo/bonus_predictions/` | Cards de Campeón y Bota de Oro |
| Tokens Tailwind extraídos | `ui-inspo/matches_dashboard/code.html` | Paleta de colores exacta lista para `tailwind.config.ts` |

> **Regla de fidelidad:** Cada componente React debe ser visualmente fiel al mockup correspondiente. El ingeniero frontend debe abrir el HTML de referencia en el browser antes de implementar cada componente.

---

## Protocolo de Gates por Fase

> **REGLA DE ORO:** Ninguna fase se inicia hasta que:
> 1. El usuario da **visto bueno explícito** ("aprobado", "ok", "adelante") a la fase anterior.
> 2. Existe **evidencia factual** en `docs/test-evidence.md`: output real de terminal (pytest/playwright), screenshots reales de UI. No se acepta "funciona en mi máquina" sin evidencia adjunta.
> 3. El Tech Lead verifica la evidencia antes de desbloquear la siguiente fase.

---

## Roadmap & Checklist

### Fase 0: Setup del Proyecto [Status: 0%]
> **Gate de entrada:** Ninguno — es la primera fase.
> **Gate de salida:** Usuario aprueba + evidencia en `test-evidence.md`.

- [ ] **T0.1 — Backend scaffold**
  - [ ] Implementación: `uv venv` en `/backend`, activar entorno, `uv pip install` con `pyproject.toml` (dependencias de ARCHITECTURE.md §8), estructura de carpetas completa según ARCHITECTURE.md §2, `.env.example`
  - [ ] **Verificación:** output de `uvicorn app.main:app --reload` arrancando en puerto 8000 · captura en `test-evidence.md`

- [ ] **T0.2 — Frontend scaffold**
  - [ ] Implementación: `npm create vite@latest frontend -- --template react-ts`, instalar shadcn/ui, configurar `tailwind.config.ts` con paleta "Neon Tokyo" completa extraída de `ui-inspo/matches_dashboard/code.html` (colores, border-radius, fuentes Sora/Space Grotesk/Inter via Google Fonts), instalar todas las dependencias de `package.json`
  - [ ] **Verificación:** screenshot de `npm run dev` en puerto 5173 con página base sin errores de consola · `npm run lint` sin errores · captura en `test-evidence.md`

- [ ] **T0.3 — .gitignore verificado**
  - [ ] Implementación: `.gitignore` ya actualizado (Python cache, `.venv`, SQLite, `node_modules`, `dist`, `.claude/settings.local.json`)
  - [ ] **Verificación:** output de `git status` confirmando que ningún archivo ignorable aparece como untracked · captura en `test-evidence.md`

**→ STOP: Presentar evidencia de Fase 0 al usuario para aprobación antes de continuar.**

---

### Fase 1: Backend — Cimientos [Status: 0%]
> **Gate de entrada:** Fase 0 aprobada con evidencia.

- [ ] **T1.1 — `database.py` + `models.py`**
  - [ ] Implementación: SQLAlchemy engine SQLite, `SessionLocal`, `Base`, `get_db()`, modelos ORM `User`, `Match`, `Prediction`, `BonusPrediction` con todas las columnas del esquema SQL de ARCHITECTURE.md §3
  - [ ] **Verificación (Unit Test):** output real de `pytest tests/test_auth.py -v` — tablas se crean en DB en memoria, constraints UNIQUE funcionan · captura en `test-evidence.md`

- [ ] **T1.2 — `auth.py`** (bcrypt + JWT)
  - [ ] Implementación: `hash_password()`, `verify_password()`, `create_access_token()`, `get_current_user()` dependency, `requires_admin` dependency
  - [ ] **Verificación (Unit Test):** output real de `pytest tests/test_auth.py -v` — hash/verify roundtrip, JWT expira correctamente, 401 para token inválido · captura en `test-evidence.md`

- [ ] **T1.3 — `time_utils.py`**
  - [ ] Implementación: `get_reference_time(simulated_time)`, `compute_match_status(match, ref_time)` → `"Open"/"Locked"/"Finished"/"Pending Teams"`, `is_prediction_allowed()`
  - [ ] **Verificación (Unit Test):** output real de `pytest tests/test_predictions.py -k time -v` — Time Travel retorna estado correcto, sin `ENABLE_TIME_TRAVEL` el parámetro es ignorado · captura en `test-evidence.md`

- [ ] **T1.4 — `scoring.py`**
  - [ ] Implementación: `calculate_prediction_points(home_guess, away_guess, home_final, away_final) -> int`, `recalculate_user_totals(db, user_id)`, `recalculate_match_predictions(db, match_id)`
  - [ ] **Verificación (Unit Test):** output real de `pytest tests/test_scoring.py -v` — casos: tendencia correcta (+3), marcador exacto (+5), tendencia incorrecta (0), local/empate/visitante · captura en `test-evidence.md`

**→ STOP: Presentar evidencia de Fase 1 al usuario para aprobación antes de continuar.**

---

### Fase 2: Backend — Endpoints [Status: 0%]
> **Gate de entrada:** Fase 1 aprobada con evidencia.

- [ ] **T2.1 — Router `auth.py`** (`POST /auth/register`, `POST /auth/login`)
  - [ ] Implementación: register crea usuario con `status='Pending'`; login retorna JWT solo para `status='Active'`; schemas Pydantic completos
  - [ ] **Verificación (Integration Test):** output real de `pytest tests/test_auth.py -v` — register 201, login 401 si Pending, login 200 si Active, 400 en username duplicado · captura en `test-evidence.md`

- [ ] **T2.2 — Router `users.py`** (`GET /users/me`, `GET /users/ranking`)
  - [ ] Implementación: `me` retorna perfil + rank calculado; `ranking` retorna usuarios `Active` ordenados `total_points DESC, exact_scores DESC, username ASC`
  - [ ] **Verificación (Integration Test):** output real de `pytest tests/test_auth.py -v` — rank se actualiza al cambiar puntos, solo usuarios Active aparecen · captura en `test-evidence.md`

- [ ] **T2.3 — Router `matches.py`** (`GET /matches`, `GET /matches/{id}`)
  - [ ] Implementación: filtros `phase`/`group_name`/`simulated_time`; estado derivado via `compute_match_status()`; incluye `my_prediction` del usuario autenticado
  - [ ] **Verificación (Integration Test):** output real de `pytest tests/test_matches.py -v` — Time Travel: partido futuro aparece `Locked` con `simulated_time` pasado, partido sin equipos aparece `Pending Teams` · captura en `test-evidence.md`

- [ ] **T2.4 — Router `predictions.py`** (`POST /predictions`, `GET /predictions/match/{id}`)
  - [ ] Implementación: upsert por `(user_id, match_id)`; valida estado `Open`; soporta `simulated_time`; GET bloquea con 403 si partido `Open`
  - [ ] **Verificación (Integration Test):** output real de `pytest tests/test_predictions.py -v` — 403 si Locked, upsert no duplica, predicciones ocultas hasta Locked · captura en `test-evidence.md`

- [ ] **T2.5 — Router `bonus.py`** (`GET /bonus-questions`, `POST /bonus-predictions`)
  - [ ] Implementación: `is_locked` = `ref_time >= MIN(start_time) FROM matches`; upsert por `(user_id, question_type)`; 403 si bloqueado
  - [ ] **Verificación (Integration Test):** output real de `pytest tests/test_auth.py -v` — bonus bloqueado después del kickoff, upsert funciona, 403 si ya bloqueado · captura en `test-evidence.md`

- [ ] **T2.6 — Router `admin.py`**
  - [ ] Implementación: `GET /admin/users?status=`, `POST /admin/users/{id}/approve`, `POST /admin/users/{id}/reject`, `POST /admin/matches`, `PUT /admin/matches/{id}`, `POST /admin/matches/{id}/result` (dispara recálculo), `PUT /admin/matches/{id}/result` (corrige + recalcula), `POST /admin/bonus-predictions/{user_id}/{type}/validate` — todas protegidas por `requires_admin`
  - [ ] **Verificación (Integration Test):** output real de `pytest tests/test_admin.py -v` — 403 para no-admin, aprobación cambia estado, resultado dispara recálculo, corrección recalcula correctamente · captura en `test-evidence.md`

**→ STOP: Presentar evidencia de Fase 2 al usuario para aprobación antes de continuar.**

---

### Fase 3: Backend — Seed [Status: 0%]
> **Gate de entrada:** Fase 2 aprobada con evidencia.

- [ ] **T3.1 — `backend/seed_matches.py`** (72 partidos de grupos)
  - [ ] Implementación: script standalone — 12 grupos × 6 partidos, fechas reales del Mundial 2026, equipos, códigos ISO alpha-2, venues; lee `DATABASE_URL` del env; idempotente
  - [ ] **Verificación:** output real de `python seed_matches.py` + `curl http://localhost:8000/matches?phase=Groups | python -m json.tool | head -20` mostrando 72 partidos · captura en `test-evidence.md`

- [ ] **T3.2 — `backend/seed_admin.py`** (usuario admin inicial)
  - [ ] Implementación: crea usuario admin desde `ADMIN_USERNAME`/`ADMIN_PASSWORD` env vars; idempotente; `is_admin=1`, `status='Active'`
  - [ ] **Verificación:** output real de `python seed_admin.py` + `curl POST /auth/login` con credenciales admin retornando JWT + `curl GET /admin/users` con ese JWT retornando 200 · captura en `test-evidence.md`

**→ STOP: Presentar evidencia de Fase 3 al usuario para aprobación antes de continuar.**

---

### Fase 4: Frontend — Cimientos [Status: 0%]
> **Gate de entrada:** Fase 3 aprobada con evidencia.

- [ ] **T4.1 — Auth flow** (Login + Register + Pending screen)
  - [ ] Referencia visual: no aplica mockup específico — pantalla funcional limpia
  - [ ] Implementación: `pages/Login.tsx` con form usuario/contraseña; `store/authStore.ts` (Zustand: `{ user, token, login(), logout() }`); `api/client.ts` (axios, adjunta JWT, interceptor 401 → logout); ruta protegida → redirect `/login`; pantalla "Cuenta pendiente" si `status='Pending'`
  - [ ] **Verificación (Visual QA):** screenshots reales en browser: Login, pantalla Pending, redirect sin token · captura en `test-evidence.md`

- [ ] **T4.2 — Layout: Sidebar + AppHeader**
  - [ ] Referencia visual: `ui-inspo/matches_dashboard/code.html` (sidebar, header, nav items, active state, responsive)
  - [ ] Implementación: `Sidebar.tsx` — fija w-64, nav items (Matches/Leaderboard/Bonus/Admin), borde activo `#ff2d78`, oculta en mobile; `AppHeader.tsx` — logo, iconos, toggle Time Travel solo si admin; hamburger en mobile
  - [ ] **Verificación (Visual QA):** screenshot desktop vs mockup `ui-inspo/matches_dashboard/screen.png` · screenshot mobile · captura en `test-evidence.md`

- [ ] **T4.3 — `types/index.ts` + `api/client.ts`**
  - [ ] Implementación: interfaces TypeScript completas para `Match`, `MatchStatus`, `Prediction`, `User`, `BonusQuestion`, `BonusPrediction`, `RankingEntry`; funciones API tipadas para todos los endpoints
  - [ ] **Verificación:** output real de `npm run build` sin errores TypeScript · captura en `test-evidence.md`

**→ STOP: Presentar evidencia de Fase 4 al usuario para aprobación antes de continuar.**

---

### Fase 5: Frontend — Features [Status: 0%]
> **Gate de entrada:** Fase 4 aprobada con evidencia.

- [ ] **T5.1 — `pages/Matches.tsx` + `components/MatchCard.tsx`**
  - [ ] Referencia visual: `ui-inspo/matches_dashboard/code.html` + `screen.png`; `docs/DESIGN.md` §4 (Match Cards)
  - [ ] Implementación: lista agrupada por fase; tabs Matchday 1/2/3 para grupos; `MatchCard.tsx` con `FlagAvatar.tsx` (flagcdn.com), inputs numéricos sin spinners (CSS webkit), `StatusBadge.tsx`; estados visuales: Open (borde `#ff2d78`), Locked (semitransparente + lock icon), Finished (borde teal/pink según resultado), Pending Teams (gris); animación "Data Transmitted" (teal glow pulse) al guardar; botón Save por card
  - [ ] **Verificación (Visual QA + E2E):** screenshots de los 4 estados de card comparados con mockup · Playwright: login → predecir partido Open → guardar → recargar → verificar persistencia · output en `test-evidence.md`

- [ ] **T5.2 — `pages/Leaderboard.tsx`**
  - [ ] Referencia visual: `ui-inspo/leaderboard/code.html` + `screen.png`; `docs/DESIGN.md` §4 (Leaderboard)
  - [ ] Implementación: tabla rank/nombre/puntos/exactos; 1° lugar con acento "Grandmaster" dorado; usuario autenticado resaltado; polling o refetch automático
  - [ ] **Verificación (Visual QA):** screenshot real con mínimo 3 usuarios en ranking comparado con mockup · captura en `test-evidence.md`

- [ ] **T5.3 — `pages/Bonus.tsx`**
  - [ ] Referencia visual: `ui-inspo/bonus_predictions/code.html` + `screen.png`
  - [ ] Implementación: 2 cards (Campeón +20pts, Bota de Oro +15pts); input texto libre; estado bloqueado visual (`is_locked=true`); predicción guardada visible
  - [ ] **Verificación (Visual QA):** screenshot estado Open · screenshot estado Locked comparados con mockup · captura en `test-evidence.md`

- [ ] **T5.4 — `pages/Admin.tsx`**
  - [ ] Referencia visual: `ui-inspo/admin_panel/code.html` + `screen.png`; `docs/DESIGN.md` §5 (Time Travel UI)
  - [ ] Implementación:
    - Tab "Usuarios": tabla Pending/Active/Rejected; badge count Pending siempre visible; botones Aprobar/Rechazar
    - Tab "Partidos": tabla resultados; inputs por fila; botón "Guardar Resultado"
    - Modal de confirmación antes de corregir resultado ya cargado: "Esto recalculará los puntos de N participantes. ¿Confirmar?"
    - Toggle Time Travel: cuando activo, acento completo cambia a purple `#7b2ffb` (warning visual de modo simulado)
  - [ ] **Verificación (E2E Playwright):** admin login → aprobar usuario pendiente → cargar resultado → verificar recálculo en ranking · output real en `test-evidence.md`

**→ STOP: Presentar evidencia de Fase 5 al usuario para aprobación antes de continuar.**

---

### Fase 6: QA Final & Hardening [Status: 0%]
> **Gate de entrada:** Fase 5 aprobada con evidencia.

- [ ] **T6.1 — Suite pytest completa**
  - [ ] Implementación: `tests/conftest.py` con fixtures (DB en memoria, `TestClient`, usuarios admin/participant/pending); cobertura completa de: Time Travel, bloqueo 15min, upsert predicciones, recálculo al corregir resultado, acceso denegado Pending/Rejected
  - [ ] **Verificación:** output real de `pytest -v` — todos los tests pasan, cero skipped · captura en `test-evidence.md`

- [ ] **T6.2 — Suite Playwright E2E**
  - [ ] Implementación: flujo completo: registro → pending screen → admin aprueba → login → predecir partido → partido se bloquea (Time Travel) → admin carga resultado → ranking actualizado
  - [ ] **Verificación:** output real de `npx playwright test --reporter=list` — todos los tests pasan · screenshots en `test-evidence.md`

- [ ] **T6.3 — `docs/test-evidence.md` consolidado**
  - [ ] Implementación: documento con todo el output acumulado de pytest/playwright y screenshots de todas las fases
  - [ ] **QA Gate:** Tech Lead no marca Fase 6 como completa hasta que `test-evidence.md` tenga evidencia de T5.x y T6.x completa y verificada

**→ STOP: Presentar evidencia de Fase 6 al usuario para aprobación. Proyecto completo.**

---

## Puntos Abiertos (Resueltos en este Plan)

| # | Punto | Resolución |
|---|---|---|
| 1 | Seed de 104 partidos | `seed_matches.py` para 72 grupos. Admin crea los 32 eliminatorios dinámicamente. |
| 2 | Admin inicial | `seed_admin.py` desde env vars `ADMIN_USERNAME`/`ADMIN_PASSWORD`. |
| 3 | Paginación `/matches` | No para MVP. Retorno completo con filtros. |
| 4 | CORS | Habilitado en dev. Evaluar en producción según deploy. |
| 5 | Banderas | `flagcdn.com/w80/{code}.png` via `*_team_code` ISO alpha-2. |

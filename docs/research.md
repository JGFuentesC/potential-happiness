# Research Report — Quiniela Mundial 2026

**Generado por:** Skill `researcher`  
**Fecha:** 2026-04-29  
**Estado del repo:** Greenfield — cero código de producción escrito.

---

## 1. Arquitectura Actual (Descubierta)

El repositorio **no contiene código**. Todo el trabajo existente es documentación, diseño y configuración del entorno de desarrollo. El árbol completo:

```
potential-happiness/
├── .claude/
│   └── settings.json          # Permisos pre-aprobados para CLI
├── .skills/
│   ├── architect/SKILL.md
│   ├── product-manager/SKILL.md
│   ├── python-ai-engineer/SKILL.md
│   ├── react-ui-engineer/SKILL.md
│   ├── researcher/SKILL.md
│   └── tech-lead/SKILL.md
├── docs/
│   ├── DESIGN.md              # Design system "Neon Tokyo"
│   └── PRD.md                 # Product Requirements Document v1.0
├── ui-inspo/
│   ├── admin_panel/           # HTML estático + screenshot
│   ├── bonus_predictions/     # HTML estático + screenshot
│   ├── leaderboard/           # HTML estático + screenshot
│   ├── matches_dashboard/     # HTML estático + screenshot
│   └── neon_tokyo/DESIGN.md  # Referencia de identidad visual
├── .gitignore                 # Solo ignora .env y .envrc (incompleto)
├── CLAUDE.md                  # Guía maestra del proyecto
└── stitch_world_cup_2026_predictor_app.zip  # Archivo sin desempacar
```

No existen carpetas `/backend` ni `/frontend`. El repo está en estado pre-código.

---

## 2. Stack Tecnológico Definido

### Stack en CLAUDE.md (fuente autorizada para este proyecto)
| Capa | Tecnología |
|---|---|
| Backend | Python 3.10+ / FastAPI |
| Frontend | TypeScript / React (Vite) / shadcn/ui / Tailwind CSS |
| Base de Datos | SQLite |
| Auth | JWT (User/Password) |
| Tests Backend | pytest |
| Linting Backend | flake8 + black |
| Tests Frontend | Playwright (definido en skill `react-ui-engineer`) |
| Gestión de deps Python | `uv` |

### Conflicto de Stack detectado ⚠️
El skill `architect` especifica un stack distinto: **Go (net/http)** para backend e infra en **GCP (Cloud Run, Firestore)**. Esto contradice el `CLAUDE.md` que define FastAPI + SQLite.

**Punto ciego crítico:** Antes de invocar el skill `architect`, el Tech Lead debe confirmar explícitamente que el stack aplicable es el de `CLAUDE.md` (FastAPI + SQLite), no el stack genérico de la fábrica definido en el skill.

---

## 3. Documentación Existente

### PRD.md — Completo y detallado
- **104 partidos** distribuidos en fases: Grupos (48), R32 (32), Cuartos (8), Semis (4), Final (1) + Tercer lugar (1). El PRD dice "Dieciseisavos a Final" — implica 32 equipos en eliminatoria directa.
- **Sistema de puntos:** +3 tendencia, +2 exacto (total 5), +20 campeón, +15 bota de oro.
- **Regla de bloqueo:** 15 minutos antes del `start_time`.
- **Privacidad:** predicciones de otros usuarios ocultas hasta que el partido esté `Locked`.
- **Feature Time Travel:** parámetro `simulated_time` en endpoints críticos, protegido por `ENABLE_TIME_TRAVEL` env var.
- **4 tablas SQLite:** `users`, `matches`, `predictions`, `bonus_predictions`.
- **Endpoints clave definidos:** 9 rutas REST documentadas.

### DESIGN.md — Design System "Neon Tokyo"
- **Paleta primaria:** Deep Space `#0a0a12` (fondo), Cyber Pink `#ff2d78` (primario), Neon Teal `#00ffcc` (secundario), Glitch Purple `#7b2ffb` (Time Travel), Warning Amber `#ffb800`.
- **Tipografía:** `Sora` (headlines), `Space Grotesk` (body/datos), `Inter` (body general).
- **Iconos:** Material Symbols Outlined (thin-stroke).
- La paleta está completamente implementada en los mockups HTML como tokens Tailwind personalizados — lista para transcribir a shadcn/Tailwind config.

---

## 4. UI Mockups — Análisis Técnico

Los 4 mockups son **HTML estático** con Tailwind CDN. No son componentes React. Sirven como referencia visual precisa para el frontend.

### Tecnología usada en mockups (NO es la del proyecto final)
- Tailwind via CDN (`https://cdn.tailwindcss.com`)
- Fonts via Google Fonts CDN
- Material Symbols via Google CDN
- Sin build step, sin componentes, sin estado

### matches_dashboard — Observaciones
- Layout: Sidebar fija (w-64) + main content con `md:ml-64`
- Match Card: Horizontal con dos inputs `type="number"` (sin spinners via CSS), flags como `<img>`, badge de grupo.
- Estados de card: borde `primary` (con predicción guardada) vs borde `outline-variant` (sin predicción).
- Tabs de Matchday como filtro visual (Matchday 1/2/3).
- Responsive: sidebar oculta en mobile, header simplificado con hamburger.

### admin_panel — Observaciones
- **Time Travel toggle** visible en el header (checkbox + label "Time Travel Sim") — ya maquetado.
- Tabla de partidos con 3 estados de fila: Live (pulsing red dot), Pending (fecha/hora), Finished (`FT` badge, inputs disabled).
- Stats cards: "Pending Matches" y "Last Update" en columna lateral.
- Botón "Calculate Points" en header con icono `calculate`.
- Filtros por grupo (Group A, Group B) en el header de la tabla.

### Elementos UI consistentes entre mockups
- Clase CSS personalizada `.neon-glow-primary`, `.neon-glow-btn`, `.neon-border-primary`
- Grid pattern en fondo via CSS `background-image: linear-gradient`
- `backdrop-blur-md` en header/sidebar
- Animaciones: `hover:translate-x-1` en nav items, `animate-pulse` en estado Live

---

## 5. Ecosistema de Skills

El proyecto define 6 skills especializados que mapean directamente a los roles del ciclo de desarrollo:

| Skill | Rol | Artefacto que produce |
|---|---|---|
| `researcher` | Análisis de código | `research.md` (este archivo) |
| `product-manager` | Requisitos | `PRD.md` (ya completado) |
| `architect` | Diseño técnico | `ARCHITECTURE.md` (pendiente) |
| `tech-lead` | Orquestación + QA | `plan.md` (pendiente) |
| `python-ai-engineer` | Backend FastAPI | Código + `test-evidence.md` |
| `react-ui-engineer` | Frontend React | Código + screenshots + Playwright |

**Orden de invocación recomendado por el propio ecosistema:**
`researcher` → `architect` → `tech-lead` (genera plan) → `python-ai-engineer` + `react-ui-engineer` (paralelo) → `tech-lead` (QA enforcement)

---

## 6. Deuda Técnica y Puntos Ciegos

### 6.1 `.gitignore` incompleto
El `.gitignore` actual solo ignora `.env` y `.envrc`. Cuando se agregue código faltará ignorar:
- `__pycache__/`, `*.pyc`, `.venv/` (backend Python)
- `node_modules/`, `dist/`, `.next/` si aplica (frontend)
- `*.db`, `*.sqlite` (base de datos local)
- `.claude/settings.local.json` (config personal)

### 6.2 Archivo ZIP sin analizar
`stitch_world_cup_2026_predictor_app.zip` en la raíz del repo no ha sido inspeccionado. Podría contener un scaffold previo, datos de partidos, o activos de referencia. **Riesgo:** si contiene código, ignorarlo puede llevar a trabajo duplicado.

### 6.3 Conflicto de stack en skill `architect`
Documentado en §2. Si el `architect` se invoca sin instrucción explícita, podría generar un `ARCHITECTURE.md` basado en Go/GCP en lugar de FastAPI/SQLite.

### 6.4 Modelo de datos: `status` en `matches` no explicitado
El PRD define `status` como `(Scheduled, Finished)` pero la lógica de negocio requiere un tercer estado `Locked` (partido bloqueado, predicciones cerradas, predicciones visibles). El estado `Locked` debe derivarse del `start_time - 15min` o almacenarse explícitamente — decisión pendiente para el Arquitecto.

### 6.5 Fases eliminatorias y equipos dinámicos
El PRD indica que el Admin debe "habilitar los partidos de rondas eliminatorias a medida que los equipos clasifican". Los `home_team`/`away_team` en R32-Final no se conocen hasta que avanza el torneo. El esquema de `matches` necesita soporte para valores null o placeholder en esos campos — no modelado en el PRD.

### 6.6 Criterion de desempate en leaderboard
El PRD menciona "número de marcadores exactos acertados" como criterio visual de desempate, pero no define qué sucede cuando dos jugadores tienen los mismos puntos Y los mismos exactos. Ambigüedad menor pero real.

### 6.7 Imágenes de banderas
Los mockups usan imágenes externas (Google CDN con URLs de `lh3.googleusercontent.com`). Para el producto final se necesita una estrategia de banderas: emoji, CDN de banderas (flagcdn.com), o assets locales.

---

## 7. Flujo de Datos (Diseñado en PRD)

```
Usuario → POST /predictions
    → Backend valida: ahora < start_time - 15min
    → Si válido: INSERT/UPDATE predictions (home_score_guess, away_score_guess)
    → Si inválido: 403

Admin → POST /admin/matches/{id}/result
    → Backend guarda home_score_final, away_score_final
    → Dispara recálculo: para cada prediction del match
        → +3 si tendencia correcta (local/empate/visitante)
        → +2 si marcador exacto
        → UPDATE predictions.points_earned
        → UPDATE users.total_points (suma)
    → UPDATE matches.status = 'Finished'

GET /matches (cualquier usuario)
    → Si simulated_time presente Y ENABLE_TIME_TRAVEL=True: usar simulated_time
    → Para cada match: calcular estado (Open/Locked/Finished)
    → Retornar lista con estado calculado

GET /predictions/match/{id}
    → Si match.status != Locked/Finished: 403
    → Si Locked/Finished: retornar predicciones de todos los usuarios
```

---

## 8. Conclusión

El repo está perfectamente preparado para comenzar desarrollo. Los artefactos de diseño (PRD, design system, mockups) están completos y son de alta calidad. El siguiente paso en el flujo de skills es invocar al **`architect`** con la instrucción explícita de usar **FastAPI + SQLite** (no Go/GCP), para generar el `ARCHITECTURE.md` y luego el `tech-lead` pueda crear el `plan.md`.

El punto más crítico a resolver antes de escribir código es el **estado `Locked`** del modelo de datos (§6.4) y confirmar qué contiene el **archivo ZIP** (§6.2).

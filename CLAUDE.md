# Guía del Proyecto: Quiniela Mundial 2026

Guía de desarrollo para la aplicación de Quiniela (Mundial Norteamérica 2026).

## Stack Tecnológico
- **Backend:** Python 3.10+ / FastAPI
- **Frontend:** TypeScript / React (Vite) / shadcn/ui / Tailwind CSS
- **Base de Datos:** SQLite
- **Autenticación:** JWT con User/Password

## Comandos Principales

### Backend (Python/FastAPI)
- **Instalar dependencias:** : `uv pip install` 
- **Ejecutar en desarrollo:** `uvicorn app.main:app --reload`
- **Tests:** `pytest`
- **Linting:** `flake8` / `black .`

### Frontend (TypeScript/React)
- **Instalar dependencias:** `npm install`
- **Ejecutar en desarrollo:** `npm run dev`
- **Build:** `npm run build`
- **Linting:** `npm run lint`

## Estándares de Código
- **Backend:** Seguir PEP 8. Uso de **Type Hints** en todos los parámetros y retornos de FastAPI.
- **Frontend:** Componentes funcionales con React. Uso estricto de **Types/Interfaces** para todas las props y respuestas de API.
- **API:** Arquitectura RESTful. Respuestas consistentes en JSON.
- **Naming:** - Python: `snake_case` para variables y funciones.
  - TypeScript: `camelCase` para variables/funciones, `PascalCase` para componentes/tipos.

## Lógica Crítica (Business Rules)
1. **Regla de Bloqueo:** Las predicciones se cierran 15 minutos antes del `start_time` del partido.
2. **Privacidad:** Las predicciones de otros usuarios NO se exponen en la API hasta que el partido esté bloqueado (`Locked`).
3. **Puntuación:** - +3 pts: Ganador/Empate (1X2).
   - +2 pts: Bono por Marcador Exacto (Total 5).
   - Bonus Especiales: Definidos antes del inicio del mundial.
4. **Time Travel:** Todos los endpoints de lectura/escritura que dependan del tiempo deben aceptar un parámetro opcional `simulated_time` (ISO 8601) para facilitar pruebas E2E.

## Estructura de Carpetas
- `/backend`: Lógica de FastAPI, modelos de DB (SQLAlchemy/SQLModel), esquemas Pydantic y rutas.
- `/frontend`: Código fuente de React, componentes de shadcn en `/components/ui`.
- `/docs`: Documentación adicional y el PRD.

## Protocolo System Heartbeat

**Archivo:** `docs/system-heartbeat.md`

Este archivo es la **fuente de verdad del estado de desarrollo** y debe mantenerse actualizado en todo momento. Cualquier agente que retome el trabajo debe leerlo antes de actuar.

### Cuándo actualizar el heartbeat
- Al completar cada fase del plan (`docs/plan.md`)
- Al tomar una decisión técnica no obvia (workaround, cambio de librería, etc.)
- Al detectar una advertencia conocida o deuda técnica nueva
- Al inicio de cada sesión de desarrollo, si ha habido cambios desde la última

### Qué debe contener siempre
1. **Estado por fase** — tabla semáforo (✅ Completada / ⏳ Pendiente / 🔒 Bloqueada)
2. **Árbol de archivos** — con estado de cada archivo relevante
3. **Evidencia de tests** — output real del último `pytest -v` y cualquier suite E2E
4. **Cómo levantar el sistema** — comandos exactos y actualizados
5. **Decisiones técnicas críticas** — especialmente las no derivables del código
6. **Variables de entorno requeridas** — lista completa
7. **Próximos pasos** — la siguiente fase con tareas concretas
8. **Advertencias conocidas** — para que el siguiente agente no tropiece dos veces

### Regla de oro
> Un agente que llega frío al proyecto debe poder leer solo `CLAUDE.md` + `docs/system-heartbeat.md` y saber exactamente qué hacer a continuación, sin necesidad de leer el historial de conversación.
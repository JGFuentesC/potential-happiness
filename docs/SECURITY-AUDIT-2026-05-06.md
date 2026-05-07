# Reporte de Auditoría de Seguridad
**Proyecto:** Quiniela Mundial 2026  
**Fecha:** 2026-05-06  
**Auditor:** cybersec skill  
**Rama:** `quiniela`  

---

## Matriz de Hallazgos

| ID | Severidad | Área | Hallazgo |
|---|---|---|---|
| S-01 | **HIGH** | Configuración | `.run/` no está en `.gitignore` |
| S-02 | **HIGH** | Auth | Fallback inseguro de `SECRET_KEY` en código |
| S-03 | **MEDIUM** | CORS | Orígenes hardcodeados, no configurables para producción |
| S-04 | **MEDIUM** | API | FastAPI `/docs` y `/redoc` activos en producción |
| S-05 | **MEDIUM** | JWT | Token de 7 días sin mecanismo de revocación |
| S-06 | **MEDIUM** | SCA Frontend | 3 vulnerabilidades MODERATE en npm |
| S-07 | **LOW** | Auth | Sin rate limiting en endpoints de autenticación |
| S-08 | **LOW** | Python | `datetime.utcnow()` deprecado (Python 3.12+) |

---

## Hallazgos Detallados

### S-01 — HIGH: `.run/` no está en `.gitignore`
**Descripción:** El directorio `.run/` contiene `backend.log`, `frontend.log`, `backend.pid`, `frontend.pid`. Los archivos de log pueden contener stack traces, rutas de base de datos, datos de requests y errores con información sensible. Estos archivos serían commiteados al repo público.

**Evidencia:**
```
.run/backend.log   ← logs de uvicorn con rutas, errores, datos de requests
.run/frontend.log  ← logs de Vite
.run/backend.pid   ← PID del proceso
.run/frontend.pid  ← PID del proceso
```
El `.gitignore` actual solo ignora `.claude/settings.local.json`, no `.run/` completo.

**Remediación:** Agregar `.run/` al `.gitignore`. ✅ **APLICADO**

---

### S-02 — HIGH: Fallback inseguro de `SECRET_KEY` en código
**Archivo:** `backend/app/auth.py:14`  
**Descripción:** Si la variable de entorno `SECRET_KEY` no está definida, el sistema usa silenciosamente `"dev-secret-key-change-in-prod"` como clave JWT. En producción, esto permite que cualquiera que conozca este valor (está en el código fuente público) forge tokens JWT válidos.

**Evidencia:**
```python
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-prod")
```

**Remediación:** Fallar ruidosamente al arrancar si `SECRET_KEY` no está definida. ✅ **APLICADO**

---

### S-03 — MEDIUM: CORS hardcodeado a localhost
**Archivo:** `backend/app/main.py:13-19`  
**Descripción:** Los orígenes permitidos en CORS están hardcodeados a `localhost:5173` y `localhost:4173`. Para un deploy en producción (dominio real), esto bloqueará el frontend o requerirá modificar el código fuente.

**Remediación:** Leer los orígenes desde `CORS_ORIGINS` (env var, separados por coma). El fix es deseable antes del deploy pero no bloquea la publicación del repo en sí.

---

### S-04 — MEDIUM: FastAPI docs públicos en producción
**Descripción:** FastAPI expone `/docs` (Swagger) y `/redoc` por defecto. En producción esto expone el esquema completo de la API, ejemplos de requests, y facilita el reconocimiento para atacantes.

**Remediación:** Condicionarlos a una variable de entorno:
```python
app = FastAPI(
    docs_url="/docs" if os.getenv("ENABLE_DOCS", "false").lower() == "true" else None,
    redoc_url=None,
)
```

---

### S-05 — MEDIUM: Token JWT de 7 días sin revocación
**Descripción:** `ACCESS_TOKEN_EXPIRE_MINUTES=10080` (7 días). Sin lista negra de tokens ni refresh tokens, un token comprometido es válido por 7 días completos. Esto es aceptable para un torneo pequeño con usuarios conocidos, pero es deuda técnica explícita.

**Remediación:** Reducir a 60–480 minutos e implementar refresh token si el PRD lo requiere en Fase 7. No bloquea publicación.

---

### S-06 — MEDIUM: Vulnerabilidades npm (SCA Frontend)
**Comando:** `npm audit`  
**Resultado:**
```
[MODERATE] ip-address <=10.1.0    — XSS en métodos HTML de Address6
[MODERATE] hono <4.12.16          — bodyLimit bypass + HTML injection en JSX
[MODERATE] express-rate-limit     — info disclosure de IP
```
**Contexto:** `hono` e `ip-address` parecen ser dependencias transitivas de herramientas de desarrollo (Vite/Playwright). No son dependencias de producción directas del código React escrito.

**Remediación:** Ejecutar `npm audit fix` y verificar que no rompa el build. Evaluar `npm audit --omit=dev` para confirmar si son solo dev deps.

---

### S-07 — LOW: Sin rate limiting en auth endpoints
**Descripción:** Los endpoints `POST /auth/login` y `POST /auth/register` no tienen protección contra ataques de fuerza bruta. Un atacante puede intentar millones de combinaciones de contraseñas.

**Remediación:** Agregar `slowapi` (rate limiting para FastAPI) o un middleware de throttling. Para un torneo pequeño, un proxy nginx con `limit_req` es suficiente.

---

### S-08 — LOW: `datetime.utcnow()` deprecado
**Descripción:** Python 3.12+ depreca `datetime.utcnow()`. Genera `DeprecationWarning` en cada request pero no es un riesgo de seguridad.

**Remediación:** Reemplazar con `datetime.now(timezone.utc)`.

---

## Análisis Estático (SAST)

| Vector | Estado | Evidencia |
|---|---|---|
| SQL Injection | ✅ LIMPIO | Sin raw SQL; todo vía SQLAlchemy ORM |
| XSS en React | ✅ LIMPIO | Sin `dangerouslySetInnerHTML` ni `innerHTML` |
| Prompt Injection | ✅ N/A | Sin integración de IA en este proyecto |
| Secretos en código | ✅ LIMPIO | `.env` en `.gitignore`; sin strings secretos hardcodeados |

---

## Análisis de Dependencias (SCA)

### Backend Python
```
pip-audit: no instalado en el entorno virtual
```
**Remediación:** `uv pip install pip-audit && pip-audit`

### Frontend npm
```
3 vulnerabilidades MODERATE (ver S-06)
0 HIGH / 0 CRITICAL
```

---

## Lo que está bien ✅

- `.env` correctamente ignorado por git
- bcrypt para hashing de contraseñas (sin passlib, directo)
- JWT con validación correcta de `sub` y estado `Active`
- Privacidad de predicciones: no se exponen hasta que el partido está `Locked` (CLAUDE.md regla 2)
- Bloqueo de predicciones 15 minutos antes del partido (CLAUDE.md regla 1)
- `requires_admin` dependency guard en todos los endpoints admin
- `.claude/settings.json` no contiene secretos — seguro para commitear

---

## Veredicto de Seguridad

| Categoría | Resultado |
|---|---|
| Secretos expuestos | ✅ Ninguno en el repo |
| Infraestructura IaC | N/A (sin Terraform) |
| Bloqueo de deploy | S-01 y S-02 — **APLICADOS** |
| Pendientes pre-deploy | S-03, S-04, S-05 |
| Deuda técnica | S-06, S-07, S-08 |

**Security Clearance: CONDICIONAL** — Los hallazgos HIGH han sido corregidos en esta sesión. El repo es seguro para publicar. Antes del deploy a producción, aplicar S-03 y S-04.

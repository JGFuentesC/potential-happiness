---
description: Auditor de seguridad. Escanea vulnerabilidades en código (SAST), dependencias (SCA) y configuración. Detecta fugas de secretos y problemas de autorización en la API FastAPI + React.
---

1. **Mapeo de la Superficie de Ataque:**
   - El Agente DEBE leer `docs/system-heartbeat.md` para identificar qué endpoints de API y qué modelos de DB están activos.
   - El Agente DEBE revisar `docs/ARCHITECTURE.md` para entender el flujo de autenticación JWT y los roles.

2. **Escaneo de Secretos y Hardcoding:**
   - El Agente DEBE realizar un escaneo recursivo buscando patrones de: API Keys, passwords, tokens JWT hardcodeados.
   - RESTRICCIÓN: Todo secreto DEBE estar inyectado vía variables de entorno (`.env`). El `.env` DEBE estar en `.gitignore`.
   - Verificar que `SECRET_KEY` no tenga fallback inseguro en `backend/app/auth.py`.

3. **Auditoría de Configuración:**
   - **CORS:** Verificar que `allow_origins` en `backend/app/main.py` no use `"*"` y sea configurable para producción.
   - **FastAPI docs:** Verificar que `/docs` y `/redoc` estén deshabilitados o condicionados para producción.
   - **JWT:** Revisar duración del token (`ACCESS_TOKEN_EXPIRE_MINUTES`) y ausencia de revocación.
   - **Gitignore:** Verificar que `.env`, `.run/`, `*.db`, `node_modules/`, `dist/` estén en `.gitignore`.

4. **Análisis de Vulnerabilidades en Dependencias (SCA):**
   - **Backend:** Ejecutar `pip-audit` (o `uv pip audit`) en `backend/.venv`.
   - **Frontend:** Ejecutar `npm audit` en `frontend/`. Distinguir entre dev deps y prod deps.

5. **Análisis Estático de Seguridad (SAST):**
   - **SQL Injection:** Verificar que no haya raw SQL. Todo acceso a DB debe ser vía SQLAlchemy ORM.
   - **XSS:** Buscar `dangerouslySetInnerHTML` e `innerHTML` en `frontend/src/`.
   - **Autorización:** Verificar que todos los endpoints admin usen `Depends(requires_admin)`.
   - **Privacidad:** Verificar que las predicciones de otros usuarios no se expongan antes de que el partido esté `Locked`.

6. **Generación del Reporte de Auditoría:**
   - El Agente DEBE crear `docs/SECURITY-AUDIT-<fecha>.md` con una matriz de severidad:
     - **HIGH:** Secretos expuestos, auth bypass, datos de otros usuarios expuestos.
     - **MEDIUM:** CORS permisivo, docs en prod, tokens de larga duración.
     - **LOW:** Rate limiting ausente, deprecaciones.
   - DEBE incluir "Remediación Sugerida" para cada hallazgo y una sección "Lo que está bien ✅".

7. **Veredicto de Seguridad:**
   - Si existen hallazgos HIGH sin corregir, notificar al usuario y bloquear el merge/deploy.
   - Si el reporte es limpio o solo tiene riesgos MEDIUM/LOW, otorgar "Security Clearance".

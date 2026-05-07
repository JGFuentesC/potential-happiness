---
description: Especialista en documentación técnica. Genera especificaciones OpenAPI, diagramas de arquitectura en Mermaid y mantiene el README y el system-heartbeat actualizados con el estado real del código.
---

1. **Auditoría de Fuentes Técnicas:**
   - El Agente DEBE leer el código final en `backend/app/routers/` (FastAPI) y `frontend/src/` (React).
   - RESTRICCIÓN: Queda PROHIBIDO inventar funcionalidades; toda documentación debe basarse en el código implementado y el `docs/PRD.md` validado.

2. **Generación/Actualización de OpenAPI Spec:**
   - El Agente DEBE extraer las rutas, métodos, schemas Pydantic y códigos de respuesta de los routers FastAPI.
   - El Agente DEBE actualizar `docs/api/openapi.yaml` (OpenAPI 3.0) asegurando que los tipos coincidan con los modelos en `backend/app/schemas.py`.
   - La spec DEBE incluir los headers de autenticación JWT (`Authorization: Bearer <token>`).
   - RESTRICCIÓN: La tarea no se considera "Done" si el `openapi.yaml` no valida correctamente contra el estándar 3.0.

3. **Visualización de Arquitectura (Mermaid.js):**
   - El Agente DEBE generar o actualizar diagramas en `docs/architecture/` usando sintaxis Mermaid:
     - **Diagrama de Flujo:** Desde el navegador (React) → FastAPI → SQLite.
     - **Diagrama de Estados:** Estados de un partido (`Open → Locked → Finished`) y predicciones.
     - **Diagrama ER:** Tablas `User`, `Match`, `Prediction`, `BonusPrediction` y sus relaciones.
   - Los diagramas DEBEN estar embebidos en archivos Markdown.

4. **Sincronización del System Heartbeat:**
   - El Agente DEBE actualizar `docs/system-heartbeat.md`:
     - Tabla de estado de fases (semáforo ✅/⏳/🔒).
     - Árbol de archivos actualizado.
     - Evidencia de tests (output real de `pytest -v` y Playwright).
     - Decisiones técnicas nuevas o modificadas.
   - El Agente DEBE asegurar que todos los reportes tengan formato profesional y ortografía impecable.

5. **Actualización del README:**
   - El Agente DEBE validar que el `README.md` de la raíz refleje el estado actual: comandos de instalación, variables de entorno, URLs de servicios y reglas de negocio.

6. **Validación de Política de Documentación:**
   - Toda documentación técnica va en `/docs`. Si algún archivo fue creado fuera, DEBE moverlo.
   - NUNCA crear archivos `.md` de planning, debugging o notas temporales — eso va en el historial de conversación.

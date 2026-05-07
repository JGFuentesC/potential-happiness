# Diagramas de Arquitectura — Quiniela Mundial 2026

**Generado por:** skill `technical-writer`
**Fecha:** 2026-05-06
**Stack:** FastAPI (Python 3.10+) · SQLite · React 18 / Vite / shadcn/ui

---

## 1. Diagrama de Flujo — Request completo de predicción

Flujo desde el navegador hasta la base de datos para el caso más crítico: guardar una predicción.

```mermaid
sequenceDiagram
    actor Usuario
    participant Browser as React App<br/>(puerto 5173)
    participant Axios as axios + interceptor JWT
    participant FastAPI as FastAPI<br/>(puerto 8000)
    participant Auth as auth.py<br/>get_current_user()
    participant TimeUtils as time_utils.py<br/>compute_match_status()
    participant DB as SQLite<br/>quiniela.db

    Usuario->>Browser: Ingresa marcador y hace clic en "Guardar"
    Browser->>Axios: savePrediction(matchId, home, away)
    Axios->>FastAPI: POST /predictions<br/>Authorization: Bearer <JWT>

    FastAPI->>Auth: Verificar JWT
    Auth->>DB: SELECT user WHERE id=sub
    DB-->>Auth: User (Active)
    Auth-->>FastAPI: current_user

    FastAPI->>DB: SELECT match WHERE id=match_id
    DB-->>FastAPI: Match (start_time, status)

    FastAPI->>TimeUtils: compute_match_status(...)
    TimeUtils-->>FastAPI: "Open" ✅

    FastAPI->>DB: UPSERT predictions<br/>(user_id, match_id, home_score_guess, away_score_guess)
    DB-->>FastAPI: Prediction guardada

    FastAPI-->>Axios: 200 PredictionOut
    Axios-->>Browser: { id, match_id, home_score_guess, ... }
    Browser-->>Usuario: Animación de guardado ✓
```

---

## 2. Diagrama de Flujo — Carga de resultado y recálculo de puntos

Flujo del Admin al cargar el resultado de un partido (desencadena scoring sincrónico).

```mermaid
sequenceDiagram
    actor Admin
    participant Browser as React App (Admin)
    participant FastAPI as FastAPI
    participant AdminRouter as admin.py<br/>set_result()
    participant Scoring as scoring.py<br/>recalculate_match_predictions()
    participant DB as SQLite

    Admin->>Browser: Ingresa 2-1 y confirma resultado
    Browser->>FastAPI: POST /admin/matches/{id}/result<br/>{ home_score_final: 2, away_score_final: 1 }

    FastAPI->>AdminRouter: requires_admin ✅
    AdminRouter->>DB: UPDATE matches<br/>SET score=2-1, status=Finished

    AdminRouter->>Scoring: recalculate_match_predictions(match_id, 2, 1)

    loop Para cada prediction del partido
        Scoring->>DB: SELECT prediction
        Scoring->>Scoring: calculate_prediction_points()<br/>→ tendencia + bono exacto
        Scoring->>DB: UPDATE prediction SET points_earned=X
        Scoring->>DB: UPDATE user SET total_points, exact_scores
    end

    Scoring-->>AdminRouter: predictions_updated = 8
    AdminRouter-->>Browser: 200 ResultResponse
    Browser-->>Admin: "8 predicciones actualizadas"
```

---

## 3. Diagrama de Capas — Arquitectura Hexagonal simplificada

```mermaid
graph TB
    subgraph "Capa de Presentación (Frontend)"
        UI[React / Vite / shadcn-ui]
        Store[Zustand authStore]
        APIClient[axios client.ts<br/>+ interceptor JWT]
    end

    subgraph "Capa de Entrada (FastAPI Routers)"
        AuthR[/auth/register<br/>/auth/login]
        UsersR[/users/me<br/>/users/ranking]
        MatchesR[/matches<br/>/matches/:id]
        PredR[/predictions<br/>/predictions/match/:id]
        BonusR[/bonus-questions<br/>/bonus-predictions]
        AdminR[/admin/** requires_admin]
    end

    subgraph "Capa de Aplicación (Lógica de Negocio)"
        AuthMod[auth.py<br/>JWT · bcrypt]
        TimeUtils[time_utils.py<br/>Time Travel · Lock Window]
        Scoring[scoring.py<br/>+3 tendencia · +2 exacto]
    end

    subgraph "Capa de Dominio (Modelos)"
        Models[models.py<br/>User · Match<br/>Prediction · BonusPrediction]
        Schemas[schemas.py<br/>Pydantic v2 request/response]
    end

    subgraph "Capa de Infraestructura"
        DB[(SQLite<br/>quiniela.db)]
        SQLAlchemy[SQLAlchemy ORM<br/>database.py]
        Seed[seed_matches.py<br/>seed_admin.py]
    end

    UI <--> Store
    UI <--> APIClient
    APIClient -->|HTTP/JSON Bearer JWT| AuthR & UsersR & MatchesR & PredR & BonusR & AdminR

    AuthR --> AuthMod
    MatchesR --> TimeUtils
    PredR --> TimeUtils
    AdminR --> Scoring

    AuthMod --> Models
    TimeUtils --> Models
    Scoring --> Models

    Models --> SQLAlchemy
    Schemas -.-> AuthR & UsersR & MatchesR & PredR & BonusR & AdminR
    SQLAlchemy --> DB
    Seed --> DB
```

---

## 4. Diagrama de Estados — Ciclo de vida de un partido

```mermaid
stateDiagram-v2
    [*] --> Scheduled : Admin crea partido<br/>(seed_matches.py)

    Scheduled --> Open : Usuario consulta<br/>ref_time < start_time - 15min
    Open --> Locked : ref_time >= start_time - 15min<br/>(calculado en runtime)
    Locked --> Finished : Admin carga resultado<br/>POST /admin/matches/:id/result

    note right of Open
        Predicciones: permitidas
        Ver otros: NO
    end note

    note right of Locked
        Predicciones: bloqueadas (403)
        Ver otros: SÍ
    end note

    note right of Finished
        Predicciones: bloqueadas (403)
        Ver otros: SÍ + puntos calculados
    end note

    note left of Scheduled
        status en DB = "Scheduled"
        Open/Locked/Finished son
        calculados por time_utils.py
        (no se almacenan)
    end note
```

---

## 5. Diagrama de Estados — Ciclo de vida de un usuario

```mermaid
stateDiagram-v2
    [*] --> Pending : POST /auth/register

    Pending --> Active : POST /admin/users/:id/approve
    Pending --> Rejected : POST /admin/users/:id/reject

    Active --> Active : Juega normalmente<br/>acumula puntos

    note right of Pending
        No puede iniciar sesión (401)
        "Account pending approval"
    end note

    note right of Rejected
        No puede iniciar sesión (401)
    end note
```

---

## 6. Diagrama de Algoritmo de Puntuación

```mermaid
flowchart TD
    A[Resultado final cargado<br/>home_final, away_final] --> B{¿Tendencia<br/>coincide?}

    B -->|NO| C[0 puntos]
    B -->|SÍ| D[+3 puntos<br/>acierto 1X2]

    D --> E{¿Marcador<br/>exacto?}
    E -->|NO| F[Total: 3 puntos]
    E -->|SÍ| G[+2 puntos bono<br/>Total: 5 puntos]

    subgraph "Tendencia (1X2)"
        H[home > away → Victoria local]
        I[home < away → Victoria visitante]
        J[home = away → Empate]
    end

    style C fill:#ef4444,color:#fff
    style F fill:#f59e0b,color:#fff
    style G fill:#10b981,color:#fff
```

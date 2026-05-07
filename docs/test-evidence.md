# Test Evidence — Quiniela Mundial 2026

**Fecha:** 2026-05-06  
**Rama:** `quiniela`

---

## 1. Suite pytest — 95/95 ✅

```
platform darwin -- Python 3.13.7, pytest-9.0.3, pluggy-1.6.0
tests/test_admin.py        15 passed
tests/test_auth.py         12 passed
tests/test_bonus.py         9 passed
tests/test_matches.py      12 passed
tests/test_models.py        6 passed
tests/test_predictions.py  12 passed
tests/test_scoring.py      13 passed
tests/test_time_utils.py   15 passed
─────────────────────────────────────
TOTAL                      95 passed, 271 warnings in 52.79s
```

Advertencias conocidas: `DeprecationWarning: datetime.utcnow()` en Python 3.13 — no bloqueante.

---

## 2. Suite Playwright E2E — 11/11 ✅

```
Running 11 tests using 1 worker

  ✓ T1  – Redirect a /login sin autenticación           (1.1s)
  ✓ T2  – Registro + pantalla Pending                   (1.7s)
  ✓ T3  – Admin login UI → /matches                     (3.0s)
  ✓ T4  – Admin aprueba usuario Pending                 (3.6s)
  ✓ T5  – Matches page: tabs, cards, grupos             (5.8s)
  ✓ T6  – Guardar predicción en partido Open            (5.5s)
  ✓ T7  – Leaderboard page                              (3.1s)
  ✓ T8  – Bonus page: cards y save                      (5.2s)
  ✓ T9  – Time Travel toggle (solo admin)               (3.9s)
  ✓ T10 – Admin carga resultado de partido              (7.2s)
  ✓ T11 – Logout y redirect a /login                    (2.6s)

  11 passed (44.6s)
```

**Screenshots:** 20 archivos en `docs/screenshots/`

Fixes aplicados durante QA:
- CORS: agregados `127.0.0.1:5173` y variantes a `allow_origins` en `main.py`
- E2E T8: locator `text=Bonus` → `h1:filter(hasText=Bonus)` (strict mode Playwright)
- `ctl.sh`: frontend ahora usa `npm run build` + `vite preview --port 5173` (prod build, libera puertos al iniciar)

---

## 3. Screenshots

### 01_login_page
![01_login_page](screenshots/01_login_page.png)

### 02_register_pending
![02_register_pending](screenshots/02_register_pending.png)

### 03_matches_dashboard
![03_matches_dashboard](screenshots/03_matches_dashboard.png)

### 04_admin_users_tab
![04_admin_users_tab](screenshots/04_admin_users_tab.png)

### 04b_admin_after_approve
![04b_admin_after_approve](screenshots/04b_admin_after_approve.png)

### 05_matches_page
![05_matches_page](screenshots/05_matches_page.png)

### 05b_matchday2
![05b_matchday2](screenshots/05b_matchday2.png)

### 05c_matchday3
![05c_matchday3](screenshots/05c_matchday3.png)

### 06_prediction_saved
![06_prediction_saved](screenshots/06_prediction_saved.png)

### 07_leaderboard
![07_leaderboard](screenshots/07_leaderboard.png)

### 08_bonus_page
![08_bonus_page](screenshots/08_bonus_page.png)

### 08b_bonus_champion_saved
![08b_bonus_champion_saved](screenshots/08b_bonus_champion_saved.png)

### 08c_bonus_topscorer_saved
![08c_bonus_topscorer_saved](screenshots/08c_bonus_topscorer_saved.png)

### 09_time_travel_active
![09_time_travel_active](screenshots/09_time_travel_active.png)

### 09b_time_travel_off
![09b_time_travel_off](screenshots/09b_time_travel_off.png)

### 10_admin_matches_tab
![10_admin_matches_tab](screenshots/10_admin_matches_tab.png)

### 10b_result_saved
![10b_result_saved](screenshots/10b_result_saved.png)

### 10c_leaderboard_after_result
![10c_leaderboard_after_result](screenshots/10c_leaderboard_after_result.png)

### 11_after_logout
![11_after_logout](screenshots/11_after_logout.png)

#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# qa.sh — Suite QA completa: pytest + Playwright E2E
# El backend puede estar ya corriendo (desde terminal nativa); si no, ctl.sh lo intenta levantar.
# Uso: ./qa.sh
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CTL="$REPO/ctl.sh"
BACKEND="$REPO/backend"
FRONTEND="$REPO/frontend"
DOCS="$REPO/docs"
EVIDENCE="$DOCS/screenshots"
EVIDENCE_MD="$DOCS/test-evidence.md"
PW_BIN="$FRONTEND/node_modules/.bin/playwright"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

ok()   { echo -e "${GREEN}[qa] ✓${RESET} $*"; }
warn() { echo -e "${YELLOW}[qa] ⚠${RESET} $*"; }
err()  { echo -e "${RED}[qa] ✗${RESET} $*" >&2; }
log()  { echo -e "${CYAN}[qa]${RESET} $*"; }
sep()  { echo -e "\n${BOLD}══════════════════════════════════════════${RESET}"; echo -e "${BOLD}  $*${RESET}"; echo -e "${BOLD}══════════════════════════════════════════${RESET}\n"; }

PYTEST_EXIT=0
PW_EXIT=0
FRONT_STARTED=false

# ── Helpers ───────────────────────────────────────────────────────────────────
service_up() {
  curl -s --max-time 2 "$1" -o /dev/null 2>/dev/null
}

wait_for() {
  local url=$1 name=$2 retries=15 i=0
  log "Esperando $name..."
  while ! service_up "$url"; do
    sleep 1; i=$(( i+1 ))
    (( i >= retries )) && { err "$name no respondió en ${retries}s"; return 1; }
    echo -n "."
  done
  [[ $i -gt 0 ]] && echo ""
  ok "$name OK ($url)"
}

free_port() {
  local port=$1
  local pid; pid=$(lsof -ti tcp:"$port" 2>/dev/null || true)
  if [[ -n "$pid" ]]; then
    warn "Puerto $port ocupado (PID $pid) — liberando..."
    kill -9 $pid 2>/dev/null || true
    sleep 0.5
  fi
}

# ─────────────────────────────────────────────────────────────────────────────
sep "0. Estado de servicios"
# ─────────────────────────────────────────────────────────────────────────────
mkdir -p "$EVIDENCE"

# ── Verificación de servicios (pre-flight) ────────────────────────────────────
log "Verificando backend  → http://127.0.0.1:8000 ..."
service_up "http://127.0.0.1:8000/docs" \
  && ok "Backend  OK" \
  || { err "Backend no responde. Ejecuta en tu terminal:"; \
       err "  cd backend && source .venv/bin/activate && uvicorn app.main:app --port 8000"; \
       exit 1; }

log "Verificando frontend → http://127.0.0.1:5173 ..."
service_up "http://127.0.0.1:5173" \
  && ok "Frontend OK" \
  || { err "Frontend no responde. Ejecuta en tu terminal:"; \
       err "  cd frontend && npm run dev"; \
       exit 1; }

# ─────────────────────────────────────────────────────────────────────────────
sep "1. pytest — Backend (95 tests)"
# ─────────────────────────────────────────────────────────────────────────────
PYTEST_LOG="/tmp/quiniela_pytest.txt"

if (cd "$BACKEND" && .venv/bin/pytest tests/ -v 2>&1 | tee "$PYTEST_LOG"); then
  ok "pytest PASSED"
else
  err "pytest FAILED"
  PYTEST_EXIT=1
fi

# ─────────────────────────────────────────────────────────────────────────────
sep "2. Playwright E2E — 11 tests"
# ─────────────────────────────────────────────────────────────────────────────
PW_LOG="/tmp/quiniela_playwright.txt"

if [[ ! -x "$PW_BIN" ]]; then
  log "Instalando @playwright/test..."
  (cd "$FRONTEND" && npm install --save-dev @playwright/test 2>&1)
  ok "@playwright/test instalado"
fi

if ! "$PW_BIN" install --dry-run chromium 2>&1 | grep -q "chromium.*installed"; then
  log "Instalando Chromium..."
  "$PW_BIN" install chromium 2>&1
  ok "Chromium listo"
fi

log "Playwright $("$PW_BIN" --version) — 11 tests"
if (cd "$FRONTEND" && "$PW_BIN" test --reporter=list 2>&1 | tee "$PW_LOG"); then
  ok "Playwright PASSED"
else
  warn "Playwright: algunos tests fallaron"
  PW_EXIT=1
fi

# ─────────────────────────────────────────────────────────────────────────────
sep "3. Generando test-evidence.md"
# ─────────────────────────────────────────────────────────────────────────────
PYTEST_SUMMARY=$(tail -3 "$PYTEST_LOG" 2>/dev/null || echo "(sin datos)")
SHOT_COUNT=$(ls "$EVIDENCE"/*.png 2>/dev/null | wc -l | tr -d ' ')

cat > "$EVIDENCE_MD" << MDEOF
# Test Evidence — Quiniela Mundial 2026

**Fecha:** $(date '+%Y-%m-%d %H:%M:%S')
**Rama:** $(git -C "$REPO" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "quiniela")

---

## 1. Suite pytest

**Resultado:** $([ "$PYTEST_EXIT" -eq 0 ] && echo "✅ PASSED" || echo "❌ FAILED")

\`\`\`
$(grep -E "PASSED|FAILED|ERROR" "$PYTEST_LOG" | head -40)
\`\`\`

\`\`\`
$PYTEST_SUMMARY
\`\`\`

---

## 2. Suite Playwright E2E

**Resultado:** $([ "$PW_EXIT" -eq 0 ] && echo "✅ PASSED" || echo "⚠️ PARCIAL")
**Screenshots:** $SHOT_COUNT archivos en \`docs/screenshots/\`

\`\`\`
$(tail -20 "$PW_LOG" 2>/dev/null || echo "(sin datos)")
\`\`\`

---

## 3. Screenshots

MDEOF

for f in "$EVIDENCE"/*.png; do
  [[ -f "$f" ]] || continue
  name=$(basename "$f" .png)
  echo "### ${name}" >> "$EVIDENCE_MD"
  echo "![${name}](screenshots/${name}.png)" >> "$EVIDENCE_MD"
  echo "" >> "$EVIDENCE_MD"
done

ok "test-evidence.md → docs/test-evidence.md ($SHOT_COUNT screenshots)"

# ─────────────────────────────────────────────────────────────────────────────
sep "Resumen"
# ─────────────────────────────────────────────────────────────────────────────
[ "$PYTEST_EXIT"  -eq 0 ] && ok "pytest      — ✅ PASSED" || err "pytest      — ❌ FAILED"
[ "$PW_EXIT"      -eq 0 ] && ok "Playwright  — ✅ PASSED" || warn "Playwright  — ⚠️  revisar reporte"
echo ""
echo -e "  📄 ${CYAN}docs/test-evidence.md${RESET}"
echo -e "  📸 ${CYAN}docs/screenshots/${RESET} ($SHOT_COUNT archivos)"
echo -e "  🌐 ${CYAN}docs/playwright-report/index.html${RESET}"
echo ""

exit $(( PYTEST_EXIT + PW_EXIT ))

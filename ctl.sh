#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# ctl.sh — Control de servidores Quiniela 2026
# Uso: ./ctl.sh <comando> [back|front|all]
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$REPO_ROOT/backend"
FRONTEND_DIR="$REPO_ROOT/frontend"
RUN_DIR="$REPO_ROOT/.run"
mkdir -p "$RUN_DIR"

BACK_PID="$RUN_DIR/backend.pid"
FRONT_PID="$RUN_DIR/frontend.pid"
BACK_LOG="$RUN_DIR/backend.log"
FRONT_LOG="$RUN_DIR/frontend.log"

# ── Colores ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

log()  { echo -e "${CYAN}[ctl]${RESET} $*"; }
ok()   { echo -e "${GREEN}[ctl] ✓${RESET} $*"; }
warn() { echo -e "${YELLOW}[ctl] ⚠${RESET} $*"; }
err()  { echo -e "${RED}[ctl] ✗${RESET} $*" >&2; }

# ── Helpers ───────────────────────────────────────────────────────────────────

is_running() {
  local pidfile="$1"
  [[ -f "$pidfile" ]] && kill -0 "$(cat "$pidfile")" 2>/dev/null
}

free_port() {
  local port=$1
  local pids; pids=$(lsof -ti tcp:"$port" 2>/dev/null || true)
  if [[ -n "$pids" ]]; then
    warn "Puerto $port ocupado (PIDs: $pids) — liberando..."
    echo "$pids" | xargs kill -9 2>/dev/null || true
    sleep 0.5
  fi
}

stop_proc() {
  local name="$1" pidfile="$2"
  if is_running "$pidfile"; then
    local pid
    pid=$(cat "$pidfile")
    kill "$pid" 2>/dev/null && sleep 0.5
    # Force-kill if still alive
    kill -9 "$pid" 2>/dev/null || true
    rm -f "$pidfile"
    ok "$name detenido (PID $pid)"
  else
    warn "$name no estaba corriendo"
    rm -f "$pidfile"
  fi
}

start_backend() {
  if is_running "$BACK_PID"; then
    warn "Backend ya está corriendo (PID $(cat "$BACK_PID"))"
    return
  fi
  free_port 8000
  log "Iniciando backend..."
  (
    cd "$BACKEND_DIR"
    source .venv/bin/activate
    nohup .venv/bin/uvicorn app.main:app --reload --port 8000 \
      > "$BACK_LOG" 2>&1 &
    echo $! > "$BACK_PID"
  )
  sleep 1
  if is_running "$BACK_PID"; then
    ok "Backend corriendo → http://localhost:8000  (PID $(cat "$BACK_PID"))"
    ok "Docs Swagger    → http://localhost:8000/docs"
  else
    err "Backend no arrancó. Revise: tail -f $BACK_LOG"
    return 1
  fi
}

start_frontend() {
  if is_running "$FRONT_PID"; then
    warn "Frontend ya está corriendo (PID $(cat "$FRONT_PID"))"
    return
  fi
  free_port 4173
  free_port 5173
  log "Compilando frontend (prod build)..."
  NPM_BIN="$(command -v npm 2>/dev/null || echo /opt/homebrew/bin/npm)"
  if ! (cd "$FRONTEND_DIR" && "$NPM_BIN" run build >> "$FRONT_LOG" 2>&1); then
    err "Build del frontend falló. Revise: tail -f $FRONT_LOG"
    return 1
  fi
  ok "Build OK — iniciando servidor de producción..."
  (
    cd "$FRONTEND_DIR"
    nohup "$NPM_BIN" run preview -- --port 5173 > "$FRONT_LOG" 2>&1 &
    echo $! > "$FRONT_PID"
  )
  sleep 2
  if is_running "$FRONT_PID"; then
    ok "Frontend corriendo → http://localhost:5173  (PID $(cat "$FRONT_PID"))"
  else
    err "Frontend no arrancó. Revise: tail -f $FRONT_LOG"
    return 1
  fi
}

status_proc() {
  local name="$1" pidfile="$2" url="$3"
  if is_running "$pidfile"; then
    echo -e "  ${GREEN}●${RESET} ${BOLD}${name}${RESET} corriendo (PID $(cat "$pidfile")) → $url"
  else
    echo -e "  ${RED}○${RESET} ${BOLD}${name}${RESET} detenido"
  fi
}

# ── Comandos ──────────────────────────────────────────────────────────────────

cmd_start() {
  case "${1:-all}" in
    back)    start_backend ;;
    front)   start_frontend ;;
    all|*)   start_backend; start_frontend ;;
  esac
}

cmd_stop() {
  case "${1:-all}" in
    back)    stop_proc "Backend"  "$BACK_PID" ;;
    front)   stop_proc "Frontend" "$FRONT_PID" ;;
    all|*)   stop_proc "Backend"  "$BACK_PID"
             stop_proc "Frontend" "$FRONT_PID" ;;
  esac
}

cmd_restart() {
  cmd_stop  "${1:-all}"
  sleep 0.5
  cmd_start "${1:-all}"
}

cmd_status() {
  echo ""
  echo -e "${BOLD}  Quiniela 2026 — Estado de servicios${RESET}"
  echo "  ─────────────────────────────────────"
  status_proc "Backend  (FastAPI)" "$BACK_PID" "http://localhost:8000"
  status_proc "Frontend (Vite)  " "$FRONT_PID" "http://localhost:5173"
  echo ""
}

cmd_logs() {
  local target="${1:-all}"
  case "$target" in
    back)
      log "--- Backend log ($BACK_LOG) ---"
      tail -f "$BACK_LOG"
      ;;
    front)
      log "--- Frontend log ($FRONT_LOG) ---"
      tail -f "$FRONT_LOG"
      ;;
    all|*)
      # Multiplex ambos logs con prefijo
      tail -f "$BACK_LOG" | sed 's/^/[BACK]  /' &
      tail -f "$FRONT_LOG" | sed 's/^/[FRONT] /' &
      wait
      ;;
  esac
}

usage() {
  echo ""
  echo -e "${BOLD}Uso:${RESET} ./ctl.sh <comando> [back|front|all]"
  echo ""
  echo "  Comandos:"
  echo "    start    [back|front|all]   Iniciar servidor(es)"
  echo "    stop     [back|front|all]   Detener servidor(es)"
  echo "    restart  [back|front|all]   Reiniciar servidor(es)"
  echo "    status                      Ver estado de ambos"
  echo "    logs     [back|front|all]   Seguir logs en tiempo real"
  echo ""
  echo "  Ejemplos:"
  echo "    ./ctl.sh start              # Inicia todo"
  echo "    ./ctl.sh restart back       # Reinicia solo el backend"
  echo "    ./ctl.sh logs front         # Sigue logs del frontend"
  echo ""
}

# ── Dispatcher ────────────────────────────────────────────────────────────────

COMMAND="${1:-help}"
TARGET="${2:-all}"

case "$COMMAND" in
  start)   cmd_start   "$TARGET" ;;
  stop)    cmd_stop    "$TARGET" ;;
  restart) cmd_restart "$TARGET" ;;
  status)  cmd_status ;;
  logs)    cmd_logs    "$TARGET" ;;
  help|--help|-h) usage ;;
  *)
    err "Comando desconocido: '$COMMAND'"
    usage
    exit 1
    ;;
esac

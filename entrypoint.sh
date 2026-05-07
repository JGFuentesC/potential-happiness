#!/bin/bash
set -e

export SECRET_KEY=${SECRET_KEY:-"docker-test-secret-key"}
export ALGORITHM=${ALGORITHM:-"HS256"}
export ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES:-10080}
export DATABASE_URL=${DATABASE_URL:-"sqlite:///./quiniela.db"}
export ENABLE_TIME_TRAVEL=${ENABLE_TIME_TRAVEL:-"False"}
export TOURNAMENT_KICKOFF=${TOURNAMENT_KICKOFF:-"2026-06-11T20:00:00"}
export ADMIN_USERNAME=${ADMIN_USERNAME:-"admin"}
export ADMIN_PASSWORD=${ADMIN_PASSWORD:-"changeme-admin"}

# Seed DB and start backend
cd /app/backend
python seed_matches.py
python seed_admin.py
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Start frontend (vite preview — handles SPA routing)
cd /app/frontend
npx vite preview --host 0.0.0.0 --port 5173 &

echo "→ Waiting for backend..."
until curl -sf http://localhost:8000/health > /dev/null 2>&1; do sleep 1; done
echo "  ✓ Backend listo en :8000"

echo "→ Waiting for frontend..."
until curl -sf http://localhost:5173 > /dev/null 2>&1; do sleep 1; done
echo "  ✓ Frontend listo en :5173"

# Si se pasa el argumento "test", corre E2E
if [ "$1" = "test" ]; then
  echo "→ Running Playwright E2E tests..."
  cd /app/frontend
  BASE_URL=http://127.0.0.1:5173 API_URL=http://127.0.0.1:8000 npx playwright test
else
  echo ""
  echo "  App:    http://localhost:5173"
  echo "  API:    http://localhost:8000"
  echo "  Swagger: http://localhost:8000/docs"
  echo ""
  # Mantener el contenedor vivo
  wait
fi

#!/usr/bin/env bash
# One-shot dev runner — starts backend + frontend.
set -e

cd "$(dirname "$0")"

echo "→ Backend setup"
cd backend
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -r requirements.txt

echo "→ Starting FastAPI on :8000"
uvicorn app.main:app --reload --port 8000 &
BACK_PID=$!
cd ..

echo "→ Frontend setup"
cd frontend
if [ ! -d node_modules ]; then
  npm install
fi

echo "→ Starting Vite on :5173"
npm run dev &
FRONT_PID=$!

echo
echo "────────────────────────────────────────────────"
echo "  Frontend  : http://localhost:5173"
echo "  Backend   : http://localhost:8000"
echo "  Swagger   : http://localhost:8000/docs"
echo
echo "  Demo user : demo@fashion.ai / demo1234"
echo "  Admin     : admin@fashion.ai / admin1234"
echo "────────────────────────────────────────────────"

cleanup() { kill $BACK_PID $FRONT_PID 2>/dev/null || true; }
trap cleanup EXIT INT TERM
wait

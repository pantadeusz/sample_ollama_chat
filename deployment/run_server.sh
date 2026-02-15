#!/usr/bin/env bash
set -euo pipefail

# Deployment launcher: finds/activates a venv then runs the Flask app.
# Location: deployment/run_server.sh (project root = one level up)

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# Candidate venv locations (checked in order)
CANDIDATES=(
  "$PROJECT_ROOT/venv"
  "$PROJECT_ROOT/../venv"
  "$PROJECT_ROOT/../sample_ollama_chat/venv"
)

PY=""
for d in "${CANDIDATES[@]}"; do
  if [ -f "$d/bin/activate" ]; then
    # shellcheck disable=SC1090
    source "$d/bin/activate"
    PY="$VIRTUAL_ENV/bin/python"
    break
  elif [ -x "$d/bin/python" ]; then
    PY="$d/bin/python"
    break
  fi
done

if [ -z "${PY:-}" ]; then
  echo "No virtualenv found in candidates; falling back to system Python" >&2
  PY="$(command -v python3 || command -v python || true)"
  if [ -z "$PY" ]; then
    echo "No Python interpreter found on PATH" >&2
    exit 1
  fi
fi

export FLASK_PORT="${FLASK_PORT:-5000}"

echo "Starting app with $PY (FLASK_PORT=$FLASK_PORT) in $PROJECT_ROOT"
exec "$PY" backend/app.py

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

usage(){
  cat <<EOF
Usage: $(basename "$0") [options]

Generates a systemd service unit for the sample_ollama_chat app.

Options:
  --service-name NAME    Service name (default: sample_ollama_chat)
  --user USER            User to run the service as (default: tp)
  --group GROUP          Group to run the service as (default: tp)
  --working-dir DIR      Working directory (default: project root)
  --venv DIR             Virtualenv path (default: PROJECT_ROOT/venv)
  --use-launcher         Use deployment/run_server.sh as ExecStart
  --port PORT            FLASK_PORT (default: 5000)
  --output FILE          Output path (default: deployment/<service>.service)
  -h, --help             Show this help

Examples:
  $(basename "$0") --service-name mysvc --user svcuser --venv /opt/venvs/mysvc
EOF
}

# Defaults
SERVICE_NAME="sample_ollama_chat"
USER_NAME="tp"
GROUP_NAME="tp"
WORKING_DIR="$PROJECT_ROOT"
VENV_DIR="$PROJECT_ROOT/venv"
USE_LAUNCHER=0
FLASK_PORT=5000
OUTPUT_FILE=""

while [[ ${#} -gt 0 ]]; do
  case "$1" in
    --service-name) SERVICE_NAME="$2"; shift 2;;
    --user) USER_NAME="$2"; shift 2;;
    --group) GROUP_NAME="$2"; shift 2;;
    --working-dir) WORKING_DIR="$2"; shift 2;;
    --venv) VENV_DIR="$2"; shift 2;;
    --use-launcher) USE_LAUNCHER=1; shift 1;;
    --port) FLASK_PORT="$2"; shift 2;;
    --output) OUTPUT_FILE="$2"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown option: $1" >&2; usage; exit 2;;
  esac
done

if [ -z "$OUTPUT_FILE" ]; then
  OUTPUT_FILE="$SCRIPT_DIR/${SERVICE_NAME}.service"
fi

# Determine ExecStart
if [ "$USE_LAUNCHER" -eq 1 ]; then
  LAUNCHER="$SCRIPT_DIR/run_server.sh"
  if [ ! -x "$LAUNCHER" ]; then
    echo "Warning: launcher $LAUNCHER not executable or missing." >&2
  fi
  EXEC_START="$LAUNCHER"
else
  PY_BIN="$VENV_DIR/bin/python"
  if [ ! -x "$PY_BIN" ]; then
    echo "Warning: python not found at $PY_BIN; generator will still write unit but it may fail." >&2
  fi
  EXEC_START="$PY_BIN $WORKING_DIR/backend/app.py"
fi

cat > "$OUTPUT_FILE" <<EOF
[Unit]
Description=Sample Ollama Chat Flask app ($SERVICE_NAME)
After=network.target

[Service]
Type=simple
User=$USER_NAME
Group=$GROUP_NAME
WorkingDirectory=$WORKING_DIR
Environment=FLASK_PORT=$FLASK_PORT
ExecStart=$EXEC_START
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "Wrote $OUTPUT_FILE"

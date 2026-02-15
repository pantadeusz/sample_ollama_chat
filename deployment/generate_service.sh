#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

usage(){
  cat <<EOF
Usage: $(basename "$0") [options]

Generates a systemd service unit for the sample_ollama_chat app.
Always uses deployment/run_server.sh as ExecStart for venv and initialization.

Options:
  --service-name NAME    Service name (default: sample_ollama_chat)
  --user USER            User to run the service as (default: tp)
  --group GROUP          Group to run the service as (default: tp)
  --working-dir DIR      Working directory (default: project root)
  --port PORT            FLASK_PORT (default: 5000)
  --output FILE          Output path (default: deployment/<service>.service)
  -h, --help             Show this help

Examples:
  $(basename "$0") --service-name mysvc --user svcuser --port 8080
EOF
}

# Defaults
SERVICE_NAME="sample_ollama_chat"
USER_NAME="tp"
GROUP_NAME="tp"
WORKING_DIR="$PROJECT_ROOT"
FLASK_PORT=5000
OUTPUT_FILE=""

while [[ ${#} -gt 0 ]]; do
  case "$1" in
    --service-name) SERVICE_NAME="$2"; shift 2;;
    --user) USER_NAME="$2"; shift 2;;
    --group) GROUP_NAME="$2"; shift 2;;
    --working-dir) WORKING_DIR="$2"; shift 2;;
    --port) FLASK_PORT="$2"; shift 2;;
    --output) OUTPUT_FILE="$2"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown option: $1" >&2; usage; exit 2;;
  esac
done

if [ -z "$OUTPUT_FILE" ]; then
  OUTPUT_FILE="$SCRIPT_DIR/${SERVICE_NAME}.service"
fi

# Always use the launcher script for ExecStart
LAUNCHER="$SCRIPT_DIR/run_server.sh"
if [ ! -x "$LAUNCHER" ]; then
  echo "Error: launcher $LAUNCHER not executable or missing." >&2
  exit 1
fi
EXEC_START="$LAUNCHER"

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

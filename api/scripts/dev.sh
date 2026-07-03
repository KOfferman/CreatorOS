#!/usr/bin/env bash
# Start Ollama (when LLM_PROVIDER=hermes) and run the API together.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$API_DIR/.env.local"

read_env_var() {
  local key="$1"
  local default_value="${2:-}"
  if [[ -f "$ENV_FILE" ]]; then
    local line
    line="$(grep -E "^${key}=" "$ENV_FILE" | tail -1 || true)"
    if [[ -n "$line" ]]; then
      line="${line#${key}=}"
      line="${line%$'\r'}"
      line="${line#\"}"
      line="${line#\'}"
      line="${line%\"}"
      line="${line%\'}"
      printf '%s' "$line"
      return
    fi
  fi
  printf '%s' "$default_value"
}

OLLAMA_HOST="$(read_env_var OLLAMA_BASE_URL "http://127.0.0.1:11434")"
OLLAMA_HOST="${OLLAMA_HOST%/}"
OLLAMA_TAGS_URL="${OLLAMA_HOST}/api/tags"
LLM_PROVIDER="$(read_env_var LLM_PROVIDER "mock")"
API_PORT="$(read_env_var API_PORT "8000")"

ollama_ready() {
  curl -sf "$OLLAMA_TAGS_URL" >/dev/null 2>&1
}

start_ollama() {
  echo "Starting Ollama (required for LLM_PROVIDER=${LLM_PROVIDER})..."

  if command -v brew >/dev/null 2>&1 && brew services list 2>/dev/null | grep -q '^ollama'; then
    brew services start ollama >/dev/null
  elif command -v ollama >/dev/null 2>&1; then
    if ! pgrep -x ollama >/dev/null 2>&1; then
      nohup ollama serve >/tmp/creatoros-ollama.log 2>&1 &
    fi
  else
    echo "ERROR: Ollama is required but not installed."
    echo "  brew install ollama && ollama pull hermes3"
    exit 1
  fi

  for _ in $(seq 1 45); do
    if ollama_ready; then
      echo "Ollama is ready at ${OLLAMA_HOST}"
      return 0
    fi
    sleep 1
  done

  echo "ERROR: Ollama did not become ready within 45s."
  echo "Check: curl ${OLLAMA_TAGS_URL}"
  exit 1
}

if [[ "$LLM_PROVIDER" =~ ^(hermes|hermes-local|ollama)$ ]]; then
  if ollama_ready; then
    echo "Ollama already running at ${OLLAMA_HOST}"
  else
    start_ollama
  fi
fi

cd "$API_DIR"
echo "Starting API on port ${API_PORT}..."
exec uvicorn app.main:app --reload --host 0.0.0.0 --port "$API_PORT"

#!/usr/bin/env bash
# Install API + monorepo shared packages for Vercel Services (api/ root).
set -euo pipefail

API_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPO_ROOT="$(cd "$API_ROOT/.." && pwd)"

cd "$API_ROOT"

PY="${PYTHON:-python3}"
if ! command -v "$PY" >/dev/null 2>&1; then
  PY=python
fi

echo "Vercel install: api=$API_ROOT repo=$REPO_ROOT (python=$PY)"

"$PY" -m pip install --upgrade pip

# Shared workspace packages (non-editable — survives serverless bundling)
"$PY" -m pip install \
  "$REPO_ROOT/shared/ai_core" \
  "$REPO_ROOT/shared/database" \
  "$REPO_ROOT/shared/shared" \
  "$REPO_ROOT/shared/agents"

"$PY" -m pip install -r requirements-vercel.txt

# Fail the build early if imports break
"$PY" -c "from app.main import app; print('vercel-import-ok:', app.title)"

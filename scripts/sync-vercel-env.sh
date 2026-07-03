#!/usr/bin/env bash
# Sync app env (from GitHub secrets/vars in the job environment) to Vercel.
# Usage: ./scripts/sync-vercel-env.sh [production|preview]
set -euo pipefail

TARGET="${1:-production}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="$ROOT/.github/env.manifest.json"

if ! command -v vercel >/dev/null 2>&1; then
  echo "ERROR: vercel CLI is required. Run: npm i -g vercel"
  exit 1
fi

export ROOT MANIFEST TARGET
python3 <<'PY'
import json
import os
import subprocess
from pathlib import Path

root = Path(os.environ["ROOT"])
manifest = json.loads((root / ".github/env.manifest.json").read_text())
target = os.environ["TARGET"]
vercel_cfg = manifest.get("vercel", {})
keys = vercel_cfg.get("deploySecrets", []) + vercel_cfg.get("deployVariables", [])

values: dict[str, str] = {}
for key in keys:
    value = os.environ.get(key, "")
    if value:
        values[key] = value


def upsert(name: str, value: str) -> None:
    subprocess.run(
        ["vercel", "env", "rm", name, target, "--yes"],
        cwd=root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        ["vercel", "env", "add", name, target],
        input=value + "\n",
        text=True,
        cwd=root,
        check=True,
    )

synced = 0
for key in keys:
    value = values.get(key, "")
    if not value:
        continue
    print(f"  vercel env {key}")
    upsert(key, value)
    synced += 1

print(f"Synced {synced} variables to Vercel ({target}).")
PY

#!/usr/bin/env bash
# Push api/.env.local + web/.env.local values to GitHub Actions secrets/variables.
#
# Usage:
#   ./scripts/sync-github-env.sh
#   ./scripts/sync-github-env.sh --env production --repo KOfferman/CreatorOS
#
# Requires: gh auth login
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_ENV="production"
REPO_ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --env)
      TARGET_ENV="${2:?missing environment name}"
      shift 2
      ;;
    --repo)
      REPO_ARGS=(--repo "$2")
      shift 2
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

if ! command -v gh >/dev/null 2>&1; then
  echo "ERROR: GitHub CLI (gh) is required. Install: brew install gh && gh auth login"
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "ERROR: gh is not authenticated. Run: gh auth login"
  exit 1
fi

chmod +x "$ROOT/scripts/sync-vercel-env.sh"
export ROOT TARGET_ENV
export GH_REPO_ARGS="${REPO_ARGS[*]}"

python3 <<'PY'
import json
import os
import subprocess
from pathlib import Path

root = Path(os.environ["ROOT"])
manifest = json.loads((root / ".github/env.manifest.json").read_text())
target_env = os.environ["TARGET_ENV"]
repo_args = os.environ.get("GH_REPO_ARGS", "").split()


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        values[key] = value
    return values


env: dict[str, str] = {}
for rel in manifest["sources"]:
    env.update(parse_env_file(root / rel))

override = root / manifest.get("overrideFile", ".github/env.production.local")
if override.exists():
    env.update(parse_env_file(override))

for key, value in manifest.get("productionDefaults", {}).items():
    env.setdefault(key, value)

aliases = {
    "META_APP_SECRET": "META_CLIENT_SECRET",
    "META_APP_ID": "META_CLIENT_ID",
    "GOOGLE_REDIRECT_URI": "GOOGLE_AUTH_REDIRECT_URI",
    "INSTAGRAM_REDIRECT_URI": "META_REDIRECT_URI",
}
for canonical, source in aliases.items():
    if source in env and canonical not in env:
        env[canonical] = env[source]

local_only = set(manifest.get("localOnly", []))
deploy_env = {k: v for k, v in env.items() if k not in local_only and v}

secret_keys = set(manifest.get("secrets", [])) & set(deploy_env)
variable_keys = set(manifest.get("variables", [])) & set(deploy_env)


def gh(*args: str, input_text: str | None = None) -> None:
    cmd = ["gh", *repo_args, *args]
    subprocess.run(cmd, input=input_text, text=True, check=True)


print(f"Syncing to GitHub environment: {target_env}")
print(f"  repo:      {' '.join(repo_args) or '(current)'}")

for key in sorted(secret_keys):
    print(f"  secret    {key}")
    gh("secret", "set", key, "--env", target_env, input_text=deploy_env[key] + "\n")

for key in sorted(variable_keys):
    print(f"  variable  {key}")
    gh("variable", "set", key, "--env", target_env, deploy_env[key])

bundle = {k: deploy_env[k] for k in sorted(deploy_env)}
print("  secret    APP_ENV_JSON (bundle for deploy workflow)")
gh(
    "secret",
    "set",
    "APP_ENV_JSON",
    "--env",
    target_env,
    input_text=json.dumps(bundle) + "\n",
)

print(f"Done. Synced {len(secret_keys)} secrets, {len(variable_keys)} variables, and APP_ENV_JSON.")
PY

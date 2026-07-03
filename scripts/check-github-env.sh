#!/usr/bin/env bash
# Validate required GitHub secrets/variables are present in the job environment.
# Usage: ./scripts/check-github-env.sh
set -euo pipefail

missing=0

check_secret() {
  if [ -z "${!1:-}" ]; then
    echo "Missing GitHub secret: $2" >&2
    missing=1
  fi
}

check_var() {
  if [ -z "${!1:-}" ]; then
    echo "Missing GitHub variable: $2" >&2
    missing=1
  fi
}

# Required for CI (sync from api/.env.local via scripts/sync-github-env.sh)
check_secret AUTH_SECRET AUTH_SECRET
check_var ENVIRONMENT ENVIRONMENT
check_var LOG_LEVEL LOG_LEVEL
check_var AUTH_URL AUTH_URL
check_var AUTH_ENABLED AUTH_ENABLED
check_secret DATABASE_URL DATABASE_URL
check_secret CELERY_BROKER_URL CELERY_BROKER_URL
check_secret CELERY_RESULT_BACKEND CELERY_RESULT_BACKEND
check_var LLM_PROVIDER LLM_PROVIDER
check_var NEXT_PUBLIC_API_BASE_URL NEXT_PUBLIC_API_BASE_URL
check_var NEXT_PUBLIC_CREATOR_USER_ID NEXT_PUBLIC_CREATOR_USER_ID

# Optional — warn only if missing
for optional in REDIS_URL GOOGLE_CLIENT_SECRET META_CLIENT_SECRET INSTAGRAM_CONFIG_SECRET; do
  if [ -z "${!optional:-}" ]; then
    echo "Optional not set: $optional" >&2
  fi
done

if [ "$missing" -ne 0 ]; then
  echo "Run: ./scripts/sync-github-env.sh --repo YOUR_ORG/CreatorOS" >&2
  exit 1
fi

echo "GitHub env OK"

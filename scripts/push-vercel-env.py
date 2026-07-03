#!/usr/bin/env python3
"""Push api/.env.local + web/.env.local to Vercel project env (REST API)."""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / ".github/env.manifest.json"

PRODUCTION_DEFAULTS = {
    "ENVIRONMENT": "production",
    "LOG_LEVEL": "INFO",
    "AUTH_ENABLED": "true",
    "LLM_PROVIDER": "mock",
    "NEXT_PUBLIC_API_BASE_URL": "/api/v1",
}


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
        value = value.strip().strip('"').strip("'")
        values[key] = value
    return values


def api_request(
    method: str,
    path: str,
    token: str,
    *,
    body: dict | None = None,
    team_id: str | None = None,
) -> object:
    query = f"?teamId={urllib.parse.quote(team_id)}" if team_id else ""
    url = f"https://api.vercel.com{path}{query}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode()
        raise RuntimeError(f"Vercel API {method} {path} failed ({exc.code}): {detail}") from exc


def discover_project(token: str, team_id: str | None) -> tuple[str, str]:
    project_id = os.environ.get("VERCEL_PROJECT_ID", "").strip()
    project_name = os.environ.get("VERCEL_PROJECT_NAME", "creatoros").strip().lower()

    data = api_request("GET", "/v9/projects", token, team_id=team_id)
    projects = data.get("projects", [])
    if project_id:
        for project in projects:
            if project.get("id") == project_id:
                return project_id, project.get("name", project_id)
        return project_id, project_id

    for project in projects:
        name = str(project.get("name", "")).lower()
        if name == project_name or "creator" in name:
            return project["id"], project.get("name", name)

    if not projects:
        raise RuntimeError("No Vercel projects found for this token/team.")

    project = projects[0]
    return project["id"], project.get("name", project["id"])


def production_url(token: str, project_id: str, team_id: str | None) -> str:
    creds = parse_env_file(ROOT / "api/.env.vercel")
    explicit = (
        os.environ.get("VERCEL_APP_URL", "").strip()
        or creds.get("VERCEL_APP_URL", "").strip()
    ).rstrip("/")
    if explicit:
        return explicit if explicit.startswith("http") else f"https://{explicit}"

    project = api_request("GET", f"/v9/projects/{project_id}", token, team_id=team_id)
    for alias in project.get("alias", []) or []:
        if alias:
            return f"https://{alias}".rstrip("/")

    name = project.get("name", "creatoros")
    return f"https://{name}.vercel.app"


def load_values(production_base: str) -> dict[str, str]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    env: dict[str, str] = {}
    for rel in manifest.get("sources", []):
        env.update(parse_env_file(ROOT / rel))

    override = ROOT / manifest.get("overrideFile", ".github/env.production.local")
    if override.exists():
        env.update(parse_env_file(override))

    vercel_local = ROOT / "api/.env.vercel"
    if vercel_local.exists():
        env.update(parse_env_file(vercel_local))

    for key, value in PRODUCTION_DEFAULTS.items():
        env[key] = value

    # Production URLs derived from deployed domain
    env["AUTH_URL"] = production_base
    env["CORS_ALLOW_ORIGINS"] = production_base
    env["OAUTH_REDIRECT_BASE_URL"] = f"{production_base}/api/v1/integrations/oauth"
    if env.get("GOOGLE_AUTH_REDIRECT_URI", "").startswith("http://localhost"):
        env["GOOGLE_AUTH_REDIRECT_URI"] = f"{production_base}/api/v1/auth/google/callback"
    if env.get("META_REDIRECT_URI", "").startswith("http://localhost"):
        env["META_REDIRECT_URI"] = f"{production_base}/api/v1/social/instagram/callback"

    local_only = set(manifest.get("localOnly", []))
    vercel_cfg = manifest.get("vercel", {})
    keys = vercel_cfg.get("deploySecrets", []) + vercel_cfg.get("deployVariables", [])
    return {k: env[k] for k in keys if k in env and k not in local_only and env[k]}


def list_env(token: str, project_id: str, team_id: str | None) -> dict[str, list[dict]]:
    data = api_request("GET", f"/v9/projects/{project_id}/env", token, team_id=team_id)
    by_key: dict[str, list[dict]] = {}
    for item in data.get("envs", []):
        by_key.setdefault(item["key"], []).append(item)
    return by_key


def delete_env(token: str, project_id: str, env_id: str, team_id: str | None) -> None:
    api_request("DELETE", f"/v9/projects/{project_id}/env/{env_id}", token, team_id=team_id)


def create_env(
    token: str,
    project_id: str,
    key: str,
    value: str,
    team_id: str | None,
    *,
    sensitive: bool,
) -> None:
    api_request(
        "POST",
        f"/v10/projects/{project_id}/env",
        token,
        body={
            "key": key,
            "value": value,
            "type": "sensitive" if sensitive else "encrypted",
            "target": ["production", "preview"],
        },
        team_id=team_id,
    )


def main() -> int:
    token = os.environ.get("VERCEL_TOKEN", "").strip()
    if not token:
        creds = parse_env_file(ROOT / "api/.env.vercel")
        token = creds.get("VERCEL_TOKEN", "").strip()
    if not token:
        print(
            "Missing VERCEL_TOKEN. Create api/.env.vercel with:\n"
            "  VERCEL_TOKEN=your-token\n"
            "  VERCEL_PROJECT_ID=optional\n"
            "  VERCEL_TEAM_ID=optional\n"
            "  VERCEL_APP_URL=https://your-app.vercel.app",
            file=sys.stderr,
        )
        return 1

    team_id = os.environ.get("VERCEL_TEAM_ID", "").strip() or parse_env_file(
        ROOT / "api/.env.vercel"
    ).get("VERCEL_TEAM_ID", "")

    project_id, project_name = discover_project(token, team_id or None)
    base_url = production_url(token, project_id, team_id or None)
    values = load_values(base_url)
    secret_keys = set(json.loads(MANIFEST.read_text())["vercel"]["deploySecrets"])

    existing = list_env(token, project_id, team_id or None)
    synced = 0
    print(f"Vercel project: {project_name} ({project_id})")
    print(f"Production URL: {base_url}")
    print(f"Syncing {len(values)} variables...")

    for key in sorted(values):
        value = values[key]
        for item in existing.get(key, []):
            delete_env(token, project_id, item["id"], team_id or None)
        create_env(
            token,
            project_id,
            key,
            value,
            team_id or None,
            sensitive=key in secret_keys,
        )
        print(f"  {key}")
        synced += 1

    print(f"Done. Synced {synced} env vars to Vercel.")
    if values.get("CELERY_BROKER_URL", "").startswith("redis://redis"):
        print(
            "WARNING: CELERY/REDIS URLs point to Docker host 'redis' — "
            "set Upstash Redis URLs in Vercel for production workers.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# Deployment

CreatorOS supports **Vercel** (recommended for web + API) and **Docker** (self-hosted / CI validation).

---

## Vercel (web + API, one project)

The repo root [`vercel.json`](../vercel.json) uses [Vercel Services](https://vercel.com/docs/services) to deploy:

| Service | Root | Public routes |
|---|---|---|
| **web** | `web/` | `/` (Next.js dashboard) |
| **api** | `api/` | `/api/*`, `/health`, `/healthz` |

The browser calls the API on the **same domain** at `/api/v1/...` — no CORS setup required in production.

### 1. Create the Vercel project

```bash
npm i -g vercel
vercel login
vercel link          # from repo root — creates/links one project
```

In the Vercel dashboard, confirm **Root Directory** is the **repository root** (not `web/`).

### 2. GitHub Actions secrets & variables

**One-time sync from your local `.env.local` files:**

```bash
gh auth login
chmod +x scripts/sync-github-env.sh
./scripts/sync-github-env.sh --env production --repo KOfferman/CreatorOS
```

This reads `api/.env.local` + `web/.env.local` and pushes values to the GitHub **`production`** environment:

| Type | Examples |
|---|---|
| **Secrets** | `AUTH_SECRET`, `DATABASE_URL`, `CELERY_*`, OAuth secrets, `APP_ENV_JSON` |
| **Variables** | `ENVIRONMENT`, `AUTH_URL`, `LLM_PROVIDER`, `NEXT_PUBLIC_*`, OAuth client IDs |

Optional production overrides: copy [`.github/env.production.example`](../.github/env.production.example) → `.github/env.production.local` (gitignored) and set your Vercel URL before syncing.

Manifest (which key is secret vs variable): [`.github/env.manifest.json`](../.github/env.manifest.json)

**Deploy credentials** (set manually or via the sync script if stored locally):

| Secret | Where to find it |
|---|---|
| `VERCEL_TOKEN` | [vercel.com/account/tokens](https://vercel.com/account/tokens) |
| `VERCEL_ORG_ID` | Project → Settings → General, or `vercel project ls` |
| `VERCEL_PROJECT_ID` | Same as above |

On deploy, [`.github/workflows/deploy-vercel.yml`](../.github/workflows/deploy-vercel.yml) uses `APP_ENV_JSON` to sync env to Vercel automatically.

You can also enable **Vercel Git integration** (connect the repo in the dashboard) — GitHub env sync still recommended for CI/CD.

### 3. Required environment variables (Vercel)

Set these on the **Vercel project** (Production) — or let the deploy workflow sync them from GitHub via `APP_ENV_JSON`:

**Shared / API**

| Variable | Example | Notes |
|---|---|---|
| `ENVIRONMENT` | `production` | |
| `LOG_LEVEL` | `INFO` | |
| `AUTH_SECRET` | *(32+ char random string)* | Required |
| `AUTH_URL` | `https://your-app.vercel.app` | Production site URL |
| `AUTH_ENABLED` | `true` | |
| `DATABASE_URL` | `mysql+pymysql://...` | Remote MySQL (e.g. Hostinger) |
| `CELERY_BROKER_URL` | `redis://...` | Upstash Redis or similar |
| `CELERY_RESULT_BACKEND` | `redis://...` | |
| `LLM_PROVIDER` | `mock` or `openai` | **Do not use `hermes`/Ollama on Vercel** — no local Ollama |
| `OPENAI_API_KEY` | `sk-...` | If `LLM_PROVIDER=openai` |
| `CORS_ALLOW_ORIGINS` | `https://your-app.vercel.app` | |

**Web (build-time)**

| Variable | Value |
|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | `/api/v1` |
| `NEXT_PUBLIC_CREATOR_USER_ID` | *(optional demo user id)* |

Copy from [`api/.env.example`](../api/.env.example) for OAuth keys if you enable integrations.

### 4. Manual deploy

```bash
vercel --prod
```

### Notes

- **Coach / LLM**: Vercel functions have a **60s max duration** (Pro). Use `LLM_PROVIDER=mock` or a cloud provider (`openai`, `openrouter`). Local Hermes/Ollama is for `make dev` only.
- **Celery worker**: Not run on Vercel. Background jobs need a separate worker (Railway, Fly.io, VPS) using the same `api/Dockerfile` + Redis.
- **Database**: Run migrations before first deploy: `cd shared/database && alembic upgrade head` against your production `DATABASE_URL`.

---

## Docker (self-hosted)

Build from the repo root:

```bash
docker build -f api/Dockerfile -t creatoros-api .
docker build -f web/Dockerfile -t creatoros-web .
```

Full stack with MySQL + Redis:

```bash
cp api/.env.example api/.env
docker compose up --build
```

With local Hermes coach:

```bash
docker compose --profile hermes up --build
```

---

## CI

[`.github/workflows/ci.yml`](../.github/workflows/ci.yml) runs on every PR and push to `main`:

- API pytest
- Web vitest + Next.js build
- Docker image build (api + web, no push by default)

To push images to GHCR on release, extend the workflow with `docker/login-action` and `push: true`.

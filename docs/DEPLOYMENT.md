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

### 1. Connect Vercel to GitHub

1. In [Vercel](https://vercel.com) → **Add New Project** → import `KOfferman/CreatorOS`
2. Set **Root Directory** to the **repository root** (not `web/`)
3. Vercel reads [`vercel.json`](../vercel.json) for web + API services
4. Set **Production Branch** to `main`

[`vercel.json`](../vercel.json) sets `"git.deploymentEnabled": false` so production deploys run from **GitHub Actions** after CI passes (not in parallel with failing builds).

### 2. GitHub Actions (CI + deploy)

**Sync local env → GitHub** (CI tests + Vercel deploy credentials):

```bash
gh auth login
# api/.env.vercel: VERCEL_TOKEN, VERCEL_ORG_ID, VERCEL_PROJECT_ID
./scripts/sync-github-env.sh --repo KOfferman/CreatorOS
```

| Type | Used by |
|---|---|
| **GitHub Secrets** | CI + deploy (`AUTH_SECRET`, `DATABASE_URL`, `VERCEL_TOKEN`, …) |
| **GitHub Variables** | CI (`ENVIRONMENT`, `NEXT_PUBLIC_*`, …) |

**Deploy flow:** push to `main` → API + web tests → `deploy-vercel` job (`vercel deploy --prod`) → smoke test `/api/v1/health`.

Manifest: [`.github/env.manifest.json`](../.github/env.manifest.json)

### 3. Vercel environment variables (runtime)

GitHub secrets are **not** automatically available to Vercel. Set the same values in **Vercel → Project → Settings → Environment Variables** (Production):

**Required for production**

| Variable | Production value |
|---|---|
| `ENVIRONMENT` | `production` |
| `AUTH_SECRET` | same as GitHub secret |
| `AUTH_URL` | `https://your-app.vercel.app` |
| `DATABASE_URL` | your remote MySQL URL |
| `CELERY_BROKER_URL` | Redis URL (Upstash, etc.) |
| `CELERY_RESULT_BACKEND` | Redis URL |
| `LLM_PROVIDER` | `mock` or `openai` — **not** `hermes` |
| `NEXT_PUBLIC_API_BASE_URL` | `/api/v1` |
| `CORS_ALLOW_ORIGINS` | `https://your-app.vercel.app` |

Copy OAuth keys from [`api/.env.example`](../api/.env.example) if using integrations.

**Optional — push local env to Vercel CLI** (after `vercel link`):

```bash
source api/.env.local   # or export vars manually
./scripts/sync-vercel-env.sh production
```

### 4. Manual deploy

```bash
vercel link    # once, from repo root
vercel --prod
```

### Notes

- **Deploy flow**: push to `main` → [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) tests → deploy job → Vercel production
- **Coach / LLM**: Vercel functions max **60s** (Pro). Use `mock` or cloud LLM — no Ollama on Vercel
- **Celery worker**: not on Vercel — run separately with `api/Dockerfile` + Redis
- **Database**: run migrations before first deploy: `cd shared/database && alembic upgrade head`

---

## Docker (self-hosted)

```bash
docker build -f api/Dockerfile -t creatoros-api .
docker build -f web/Dockerfile -t creatoros-web .
cp api/.env.example api/.env && docker compose up --build
```

With Hermes coach: `docker compose --profile hermes up --build`

---

## CI

[`.github/workflows/ci.yml`](../.github/workflows/ci.yml) on every PR and push to `main`:

- API pytest (uses GitHub secrets/vars)
- Web vitest + Next.js build
- Docker image build validation

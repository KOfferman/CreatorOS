# CreatorOS — Interview Demo Script

**Duration:** 12–15 minutes (core demo) + 5 minutes (architecture)  
**Persona:** Daniela Vargas — relationships, lifestyle, self-growth, Costa Rica travel  
**Goal:** Show a believable creator workflow from insight → content → calendar → coaching, then explain how the system is built for production.

---

## Before the Interview (15 minutes)

### 1. Start the stack

From the repo root:

```bash
# Terminal 1 — API + MySQL + Redis + worker
cd api
docker compose up --build

# Terminal 2 — Web app
cd web
corepack pnpm install
corepack pnpm dev
```

**URLs**
- Web: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`
- System status: `http://localhost:8000/api/v1/admin/system-status`

### 2. Seed Daniela's demo data (Python 3.11+)

```bash
cd api
python scripts/seed_daniela.py
```

If seeding is unavailable, the demo still works — the UI will create a profile on first load and you can run trend research live.

### 3. Set environment (optional but recommended)

In `web/.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_CREATOR_USER_ID=<daniela-user-id-if-seeded>
```

For local dev, auth is typically disabled (`AUTH_ENABLED=false` in `api/.env`).

### 4. Sanity check (30 seconds)

Open `http://localhost:3000` — you should see **Good morning, daniela.creates** (or similar) and populated cards if seed data loaded.

**Fallback if API is slow:** Keep the web UI open; narrate that async jobs run in Celery while the dashboard reads persisted state from MySQL.

---

## Demo Flow Overview

| Step | Screen | Time | What you're proving |
|------|--------|------|---------------------|
| 1 | Dashboard (Home) | 2 min | Daily briefing + unified creator view |
| 2 | Trends | 2 min | Signal discovery and prioritization |
| 3 | Generator (from trend) | 2 min | AI content pipeline with structured output |
| 4 | Calendar | 1.5 min | Planning loop closes |
| 5 | Growth Coach | 2 min | Conversational coaching grounded in context |
| 6 | Architecture | 5 min | Production-minded system design |

---

## Step 1 — Dashboard Daily Briefing (2 min)

**Navigate:** Sidebar → **Home** (`/`)

### What to show

Point to each card in order:

1. **Daily AI Briefing** — personalized action for today  
2. **Creator Score** — composite health metric  
3. **Top Trend Opportunity** — highest-signal trend from recent research  
4. **Recommended Posts** — content ideas ready to draft or schedule  
5. **Audience Growth Insight** — projected growth based on activity  
6. **Upcoming Scheduled Content** — what's going live next  

### What to say

> "This is Daniela's command center. CreatorOS doesn't just generate text — it synthesizes profile, trends, ideas, and calendar into a daily briefing so she knows *what to do today*, not just what data exists.
>
> Everything on this page is live from our FastAPI backend — trends, ideas, and calendar items are persisted in MySQL. The briefing is computed from that state so creators get a single actionable view instead of jumping between five tools."

### Optional deep-dive (if asked)

- Dashboard pulls from `/creators`, `/trends`, `/content-ideas`, and `/calendar` in parallel.
- Creator score is derived from audience size, trend volume, scheduled content, and idea pipeline — a simple v1 metric that can evolve into a scored model.

---

## Step 2 — Trend Discovery (2 min)

**Navigate:** Sidebar → **Trends** (`/trends`)

### What to show

1. Trend table with **trend score**, **confidence score**, and **suggested content angle**
2. **Platform filter** (Instagram, TikTok, YouTube, etc.)
3. **Run Trend Research** button (optional — only if you want to show live AI; takes a few seconds)
4. **Generate content** action on a high-scoring row

### What to say

> "Trend discovery is where Daniela decides what to create *this week*. Each trend has a score and confidence so she can prioritize signal over noise.
>
> Under the hood, `TrendResearchAgent` combines mock research data — easy to swap for real scrapers later — with LLM analysis. Results land as `trend_reports` in the database and surface here immediately.
>
> I'm going to pick this top trend — something in her niche like relationships or Costa Rica lifestyle — and turn it into content in one click."

### Pick a trend

Choose a row with:
- High trend score (80+)
- Clear suggested angle
- Platform that matches Daniela (Instagram or TikTok works well)

Click **Generate content from trend** (or equivalent action on the row).

---

## Step 3 — Generate Content from Trend (2 min)

**Navigate:** You'll land on **Generator** (`/generator`) with fields pre-filled, or go there manually.

### What to show

**Inputs (left / top):**
- Platform
- Topic (from the trend)
- Audience
- Goal
- Tone/voice (Daniela: *warm, honest, reflective, practical, story-first*)

Click **Generate** if not already generated.

**Outputs (structured cards):**
- Hook
- Caption
- Script
- Hashtags
- CTA

### What to say

> "The generator isn't a blank ChatGPT window. `ContentWriterAgent` takes typed inputs — platform, audience, goal, voice — and returns a *structured* payload we can store, score, and schedule.
>
> Every generation creates an `AgentRun` record: model, tokens, latency, cost. That's how we keep AI workloads observable and budgetable in production."

### Pro tip

If generation is slow, narrate:

> "Longer agent runs can be offloaded to Celery; for this demo we're running synchronously so you see the full round-trip."

---

## Step 4 — Save to Calendar (1.5 min)

**Still on Generator** — scroll to **Save to Calendar**.

### What to show

1. Click **Save to Calendar**
2. Confirm success state (button shows "Saving..." then completes)
3. Navigate to **Calendar** (`/calendar`)

**On Calendar:**
- Find the new item in **list view** or **monthly view**
- Show **status badge** (idea → draft → scheduled → published)
- Show **platform badge**
- Optionally edit scheduled date/time or drag to reschedule (monthly view)

### What to say

> "This closes the loop: insight → draft → scheduled post. Saving creates a content idea *and* a calendar item linked together, so Daniela's pipeline stays traceable.
>
> The calendar supports status workflow and rescheduling — creators plan in one place instead of copying AI output into Notion or a spreadsheet."

---

## Step 5 — Ask Growth Coach Why a Post Performed Well (2 min)

**Navigate:** Sidebar → **Coach** (`/coach`)

### What to show

1. Chat interface with message history (persisted in localStorage)
2. Suggested questions chips
3. Type a performance question, e.g.:

   > "My reel about setting boundaries while traveling in Costa Rica got 3x my usual saves. Why did it perform so well, and how should I repeat that?"

4. Send and show **loading state**
5. Show **markdown-formatted** coaching response with actionable recommendations

### What to say

> "The Growth Coach is powered by `GrowthCoachAgent`. It receives Daniela's profile, recent trends, and audience context — not just the question in isolation.
>
> Each chat turn is an `AgentRun`, so we have auditability: what model ran, how many tokens, how long it took, whether it succeeded. That's the difference between a demo chatbot and a production coaching feature."

### If the response is generic

Follow up in the UI:

> "What should I post next week to build on this momentum?"

This shows multi-turn coaching and practical next actions.

---

## Step 6 — Explain the Architecture (5 min)

**No screen required** — use README diagrams, a whiteboard, or `docs/ARCHITECTURE.md`. Optionally show `http://localhost:8000/docs` or `/api/v1/admin/system-status`.

### Opening frame (30 sec)

> "CreatorOS is a multi-service SaaS monorepo: Next.js frontend, FastAPI control plane, Celery workers, shared agent libraries, and MySQL. The design goal is fast iteration *with* production guardrails."

### Layer-by-layer walkthrough

#### 1. Client layer — `web/`

> "Next.js App Router pages map to creator workflows: dashboard, trends, generator, calendar, coach. The API client in `web/lib/api.ts` is typed against our REST contracts."

#### 2. API control plane — `api/`

> "FastAPI owns routing, validation, auth, rate limiting, and observability. Routers stay thin — business logic lives in services, data access in repositories. We don't call LLMs directly from route handlers."

**Mention:**
- JWT auth scaffold (`AUTH_ENABLED` for local dev)
- Rate limiting middleware
- Request IDs + structured JSON logs
- Input guardrails against prompt injection
- `GET /api/v1/admin/system-status` for ops visibility

#### 3. Async execution — `api/worker/`

> "Heavy jobs — daily trend research, audience analysis, briefing generation, creator score refresh — run in Celery workers backed by Redis. Failed jobs retry with logging; every agent execution writes to `agent_runs`."

#### 4. Agent layer — `shared/agents/`

> "Agents are typed classes with Pydantic input/output schemas: Trend Research, Content Writer, Audience Analyst, Growth Coach. They share a `BaseAgent` that handles provider access, retries, token/cost tracking, and error handling."

**Agent workflow ( narrate the sequence ):**
1. User action in web
2. API validates and persists context
3. Service invokes agent (sync) or enqueues Celery task (async)
4. Agent calls LLM via provider abstraction
5. Output validated against schema; retry if invalid JSON
6. `AgentRun` saved with usage and latency

#### 5. Provider abstraction — `shared/ai_core/`

> "`BaseLLMProvider` lets us swap OpenAI for other vendors without rewriting agents. Model routing and cost optimization become configuration, not refactors."

#### 6. Data layer — `shared/database/`

> "MySQL via SQLAlchemy. Core entities: users, creator profiles, trend reports, content ideas, calendar items, audience insights, agent runs. Alembic manages migrations."

### Architecture diagram (verbal)

```
User → Next.js → FastAPI → MySQL
                    ↓
                 Redis → Celery Worker → Agents → LLM
                    ↓
              agent_runs (audit + cost)
```

### Production themes to land (pick 2–3)

| Theme | One-liner |
|-------|-----------|
| **Observability** | Request IDs, structured logs, agent run metrics, admin status endpoint |
| **Security** | JWT, rate limits, input validation, prompt injection guardrails, Celery task allowlisting |
| **Scalability** | Stateless API replicas, dedicated worker pools, managed MySQL/Redis |
| **Cost control** | Token tracking per run, model routing, async batch jobs for research |
| **Testability** | API tests, repository tests, agents tested with mocked LLM, frontend Vitest |

### Closing architecture line

> "We built the product path creators feel — briefing, trends, generate, schedule, coach — on top of a control plane you'd actually operate in production: typed agents, durable run history, and clear service boundaries."

---

## Suggested Questions & Answers

**Q: Why FastAPI + Celery instead of doing everything synchronously?**  
A: Creator workflows mix fast reads (dashboard) with slow LLM work (research, generation). Celery keeps API latency predictable and lets us scale workers independently.

**Q: How do you prevent prompt injection?**  
A: Schema validation on inputs, pattern guardrails in Pydantic models and the prompt manager, size limits, and no arbitrary tool execution from user text.

**Q: How would you add real trend data?**  
A: `TrendResearchAgent` already separates mock research from LLM analysis. Swap the research provider for APIs/scrapers; agent contract and API stay the same.

**Q: How do you track AI cost?**  
A: Every agent run records prompt/completion tokens and estimated USD cost. That feeds ops dashboards and future per-creator budgets.

**Q: What's not built yet?**  
A: Real OAuth/social analytics ingestion, multi-tenant billing, and production auth hardening — but the scaffolding (auth, observability, agent runs) is in place.

---

## Troubleshooting During Live Demo

| Issue | What to do |
|-------|------------|
| Dashboard empty | Run seed script or click **Run Trend Research** on Trends page |
| API connection error | Check `NEXT_PUBLIC_API_BASE_URL`; verify `docker compose ps` |
| Coach/generator timeout | Acknowledge async architecture; show a previously generated result on Generator |
| Auth 401 errors | Set `AUTH_ENABLED=false` locally or mint token via `POST /api/v1/auth/token` |
| Slow LLM | Narrate Celery path; show persisted trends/ideas from seed data instead |

---

## One-Paragraph Elevator Version (60 sec)

> "CreatorOS is an AI operating system for content creators. Daniela opens her dashboard and gets a daily briefing synthesized from trends, ideas, and her calendar. She discovers a high-confidence trend, generates structured content — hook, script, hashtags — saves it to her calendar, and asks the Growth Coach why a recent post outperformed. Under the hood: Next.js frontend, FastAPI API, Celery workers, typed AI agents with full run tracking, MySQL persistence, and production basics like auth, rate limiting, and observability. It's the creator workflow end-to-end, built like a real SaaS platform."

---

## Related Docs

- [ARCHITECTURE.md](./ARCHITECTURE.md)
- [AI_AGENT_DESIGN.md](./AI_AGENT_DESIGN.md)
- [SECURITY.md](./SECURITY.md)
- [README.md](../README.md) — setup, diagrams, API overview

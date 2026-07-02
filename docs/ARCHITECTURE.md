# CreatorOS Architecture

## Purpose
CreatorOS is a multi-service SaaS platform for AI-assisted creator workflows: trend discovery, content generation, coaching, and publishing orchestration.

This architecture is optimized for:
- fast product iteration
- strong operational guardrails
- clear boundaries between API, async jobs, agent logic, and UI

## System Overview
- `web/` — Next.js frontend (dashboard, generator, calendar, coach)
- `api/` — FastAPI control plane (REST API, auth, validation, observability)
- `api/worker/` — Celery async workers (agent jobs, scheduled automation)
- `shared/agents/` — reusable agent implementations and prompt orchestration
- `shared/ai_core/` — model/provider abstraction layer
- `shared/database/` — SQLAlchemy models + Alembic migrations (MySQL)
- `mobile/` — React Native app shell for mobile use cases

## Runtime Data Flow
1. Client sends request to FastAPI (`/api/v1/*`).
2. API validates input, applies auth/rate limits, and returns:
   - synchronous response (for reads/simple writes), or
   - async task handle via Celery for long-running jobs.
3. Worker executes AI/analysis pipeline and updates `agent_runs`.
4. Client polls/lists updated entities (trends, ideas, calendar, insights).

## Service Boundaries
- **API Layer**
  - routing, policy enforcement, request/response contracts
  - no direct LLM business logic in routers
- **Service Layer**
  - orchestration and domain-level behavior
  - task allowlisting + safe payload boundaries
- **Repository Layer**
  - data access only; no domain policy
- **Agent Layer**
  - deterministic schemas, provider-agnostic execution, token/cost capture

## Storage and State
- **Primary DB:** MySQL
- **Queue + result backend:** Redis
- **Durable execution history:** `agent_runs` table
- **Operational signals:** structured logs + request IDs + admin status endpoint

## Deployment Topology (Recommended)
- **Edge/CDN:** static assets + request shielding
- **App tier:** autoscaled API replicas (stateless)
- **Worker tier:** dedicated Celery pools by job class (LLM-heavy vs lightweight)
- **State tier:** managed MySQL + managed Redis with backups and failover

## Environment Strategy
- **Local:** Docker Compose, mock/provider fallback, permissive auth mode
- **Staging:** production-like topology + synthetic traffic + release checks
- **Production:** strict auth, secret management, budget and rate controls

## Observability Baseline
- JSON structured logs across API/worker/agents
- Request IDs propagated in responses/logs
- Latency tracking at request, task, and agent execution level
- Failed-job and failed-agent tracking in logs and `agent_runs`
- `/api/v1/admin/system-status` for operator visibility

## Reliability and Recovery
- retries + backoff in Celery base task
- idempotent write patterns for task-generated entities
- health endpoints + status endpoint for fast incident triage
- DB migrations managed through Alembic and release runbooks

## Near-Term Architecture Priorities
1. add multi-tenant authorization model (org/workspace scoping)
2. add read replicas + query optimization for dashboard-heavy endpoints
3. split worker queues by SLA class and model/provider cost profile
4. add metrics backend (Prometheus/OpenTelemetry) for SLOs

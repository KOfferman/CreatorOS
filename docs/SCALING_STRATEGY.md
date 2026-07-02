# Scaling Strategy

## North-Star Targets
- p95 API latency < 250ms for non-AI endpoints
- queue wait time < 30s for standard AI jobs
- predictable cost per active creator
- zero-downtime deploys for API/web tiers

## Current Baseline
- stateless API and web services
- async job processing with Celery + Redis
- MySQL as primary DB
- limited horizontal tuning and no dedicated queue classes yet

## Scaling Plan by Phase

### Phase 1: Vertical + Low-Risk Horizontal (Now)
- autoscale API replicas
- separate worker from API compute
- add queue concurrency limits
- implement query/index tuning for hot endpoints

### Phase 2: Workload Segmentation
- split Celery queues by workload class:
  - `realtime-light`
  - `batch-analytics`
  - `llm-heavy`
- route jobs based on SLA and cost sensitivity
- add retry policies per queue type

### Phase 3: Data Plane Optimization
- read replicas for dashboard/list endpoints
- caching layer for high-read aggregate views
- archival strategy for large `agent_runs` payloads
- partitioning strategy for high-volume time-series-like tables

### Phase 4: Global and Enterprise Readiness
- multi-region read strategy
- region-aware job routing
- tenant isolation controls for enterprise plans
- stronger SLO/SLA enforcement with auto-remediation

## Bottleneck Playbook

### API Bottlenecks
- symptoms: high p95 latency, CPU saturation
- actions: autoscale, cache hot reads, reduce N+1 queries

### Worker Bottlenecks
- symptoms: queue lag, timeout spikes
- actions: queue partitioning, model routing, dedicated pools

### Database Bottlenecks
- symptoms: lock waits, slow scans
- actions: index tuning, replica reads, write batching

## Capacity Management
- forecast by:
  - active creators/day
  - generated assets/day
  - tokens consumed/day
- maintain headroom:
  - 30% compute buffer for API
  - 2x burst buffer for worker queues

## Guardrails
- fail fast on overloaded non-critical jobs
- degrade gracefully to cached/last-known outputs
- enforce per-tenant quotas for abusive patterns

## Key Metrics to Track
- request throughput + p95 latency
- queue depth + queue wait time
- token usage per feature
- DB connection pool utilization
- failed jobs and retry rates

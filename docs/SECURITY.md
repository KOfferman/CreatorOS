# Security Foundations

## Security Objectives
- protect user data and operational secrets
- enforce least privilege at API boundaries
- prevent abuse (rate, injection, task misuse)
- maintain auditability through logs and execution records

## Implemented Controls

### Authentication and Access
- JWT issuance endpoint (`/api/v1/auth/token`)
- bearer token verification with issuer/audience checks
- route protection via dependency-based auth gates
- **admin RBAC** — `/admin/*` requires `user_id` in `ADMIN_USER_IDS` (comma-separated env allowlist)
- `AUTH_ENABLED` flag supports staged rollout

### API Abuse Protection
- **Redis-backed** per-IP+path rate limiting in production/staging (`REDIS_URL`)
- in-memory fallback for local development and tests
- configurable threshold: `API_RATE_LIMIT_PER_MINUTE`
- explicit 429 responses and retry hints

### Request and Input Hardening
- strict Pydantic schema constraints (length/type/ranges)
- guardrails for known injection patterns in user-provided text
- sanitized and bounded task payload inputs

### Prompt Injection Guardrails
- prompt manager scans input fields for unsafe instruction patterns
- blocked phrases include override/system prompt exfiltration attempts
- failures are explicit and non-silent

### Safe Tool/Task Boundaries
- Celery dispatch goes through allowlisted task names only
- task payload field count/size checks before enqueue
- prevents arbitrary task execution from service layer misuse

### Secrets and Environment Controls
- auth secret minimum-strength enforcement in secure modes
- startup checks for invalid production/staging secret patterns
- provider key sanity checks for selected LLM provider
- `.env.local` files are gitignored — never commit environment files

### OAuth State (Social Integrations)
- OAuth `state` is a **signed JWT** (`create_oauth_state` / `verify_oauth_state` in `api/app/social/oauth_service.py`)
- Claims: `sub` (user id), `platform`, `purpose=social_oauth_state`, `iss`, `aud`, 10-minute `exp`
- Callback verifies signature, issuer, audience, and purpose before completing the connection
- **Current limitation:** state binds platform + user id but is not yet bound to a browser session nonce; treat stolen state links as in-scope for future hardening (PKCE + server-side session binding)

### Observability for Security
- request IDs in logs + responses
- structured logs with latency/status/error metadata
- failed job + failed agent run tracking
- admin status endpoint for quick operational triage

## Threat Model (Baseline)
- credential/token misuse
- endpoint flooding and brute-force patterns
- prompt injection and policy override attempts
- unauthorized task execution and queue abuse
- sensitive data leakage through logs/errors

## Operational Security Practices
- rotate `AUTH_SECRET` on a fixed schedule
- avoid committing `.env` or secret-bearing files
- restrict admin endpoint access in production
- isolate worker/API credentials per environment
- run dependency scanning in CI

## Recommended Next Steps
1. move secrets to managed secret store (AWS/GCP/Vault)
2. bind OAuth state to server session nonce + PKCE
3. add WAF + IP reputation filtering at edge
4. implement signed audit trails for high-risk operations
5. add SAST/DAST + dependency vulnerability gates in CI

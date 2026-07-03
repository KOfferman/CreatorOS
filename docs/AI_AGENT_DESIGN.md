# AI Agent Design

## Design Goals
CreatorOS agents are designed to be:
- provider-agnostic
- schema-constrained
- observable
- cost-aware
- safe by default

## Core Components
- `BaseAgent` (`shared/agents/agents/base.py`)
  - lifecycle management
  - token/cost accounting
  - `agent_runs` persistence
  - failure and completion logging
- domain agents
  - `TrendResearchAgent`
  - `ContentWriterAgent`
  - `AudienceAnalystAgent`
  - `GrowthCoachAgent`
- prompt manager + templates
  - versioned templates
  - typed input/output schemas
  - validation retries
  - prompt-injection guardrails

## Execution Lifecycle
1. Validate typed input schema.
2. Create `agent_runs` row with `running` status.
3. Build prompt context and call provider abstraction.
4. Validate model output schema.
5. Persist output payload, usage, cost, and timestamps.
6. Emit completion/failure logs with execution metadata.

## Provider Abstraction
`shared/ai_core` defines a stable contract:
- `generate_text`
- `generate_json`
- `stream_text`

| Provider | Status |
|---|---|
| OpenAI | Implemented (`OpenAIProvider`) |
| Claude | Extension point (interface only) |
| Gemini | Extension point (interface only) |
| OpenRouter | Extension point (interface only) |
| Hermes (local) | Extension point (interface only) |
| Mock | Implemented for local dev |

This isolates vendor changes from application logic and allows:
- provider swapping
- differential testing
- fallback policies

## Prompt and Output Safety
- Strict Pydantic output contracts
- Retry on schema mismatch
- Input guardrails against known prompt-injection patterns
- No direct execution of model-generated code/tools

## Agent Run Record Standard
Every run should include:
- `agent_name`
- `status` (`running`, `completed`, `failed`)
- `input_payload`
- `output_payload`
- `error_message` (on failure)
- `started_at`, `finished_at`
- usage/cost metadata in output payload

## Testing Strategy
- unit tests with mocked LLM JSON responses
- schema failure + retry behavior tests
- task-level tests for worker integration points
- contract tests for stable response shapes

## Operational Policy
- set token and latency budgets per agent type
- route expensive workloads to async queues only
- maintain agent-level quality checks before rollout
- version prompts with explicit migration notes

## Future Maturity Roadmap
1. automated eval datasets per agent
2. semantic regression detection on prompt/template updates
3. policy engine for dynamic model routing (quality/cost/latency)
4. HITL escalation path for high-risk outputs

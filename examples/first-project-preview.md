# TraceForge — Reproducible Replay and Regression Testing for Tool-Calling AI Agents

> This is an illustrative sample brief. A live daily brief includes a Hugging Face optimization status section; that optimizer improves the specification but does not generate the initial draft.

**Difficulty:** Advanced · **Effort:** 7 days · **Category:** LLM evaluation and observability

> Build a testing workbench that records how a tool-using agent solved a task, safely replays the same scenario after a model/prompt/tool change, and catches regressions before deployment.

## 1. The problem

A LangChain, LangGraph, or CrewAI agent may call tools in a different order, produce invalid structured output, or silently fail after a prompt or model update. Plain application logs often capture text but do not provide a clean, versioned test case, redacted tool trace, deterministic replay, and side-by-side regression report.

TraceForge focuses on one job: turn real agent executions into privacy-filtered regression tests. It is an evaluation/observability system, not another chatbot or RAG interface.

## 2. Unique angle

Combine trace normalization, secret/PII redaction, deterministic replay with recorded tool fixtures, and version-to-version regression diffs. Score not only final-answer quality but also tool-call sequence, schema compliance, success criteria, latency, and estimated token/API cost. A run is useful only if its replay state and evaluator inputs are reproducible.

## 3. MVP requirements

### A. Trace capture
- Accept trace events from a small LangGraph demo agent or an adapter interface.
- Normalize each run into `run`, `span`, `tool_call`, and `model_response` events.
- Store agent version, prompt hash, model ID, tool names, timestamps, statuses, errors, and token/cost estimates when available.
- Acceptance: a single demo task creates a trace that can be retrieved by run ID and reconstructed in time order.

### B. Safe trace storage
- Redact known API key patterns, bearer tokens, emails, and configurable sensitive fields before persistence.
- Retain the redaction count and field path, not the original secret.
- Acceptance: seeded fake credentials never appear in persisted trace JSON, Markdown export, or logs; add a regression test for every redaction rule.

### C. Scenario library
- Turn a completed run into a named test case with input, expected outcome, permitted tool list, evaluator checks, and mock tool responses.
- Add tags such as `tool-routing`, `structured-output`, `timeout`, and `permission-denied`.
- Acceptance: a stored scenario can be exported/imported as JSON and run without contacting a live external tool.

### D. Deterministic replay
- Implement a tool adapter that replays recorded outputs by tool name and normalized input hash.
- Mark unmatched tool inputs as replay mismatches instead of silently using live tools.
- Acceptance: replaying the same recorded scenario produces the same mock tool sequence and a diff report.

### E. Regression comparison
Compare a baseline run to a candidate run:
- Task success according to the scenario's evaluator.
- Tool-sequence similarity and unmatched/missing calls.
- Pydantic/JSON Schema validity for structured responses.
- Latency and estimated cost deltas.
- Evidence/grounding checks only when the scenario defines a verifiable expected source.
- Acceptance: a deliberately broken tool name or malformed JSON fixture triggers a failing regression check.

## 4. Suggested stack

- **Python 3.11+:** primary implementation.
- **FastAPI + Pydantic:** trace and scenario API with strict schemas.
- **SQLite first, PostgreSQL/Supabase later:** local-first persistence and easy development.
- **LangGraph or LangChain callbacks:** adapter for one demo agent; keep the core event schema framework-neutral.
- **OpenTelemetry-compatible spans:** stable trace/span IDs and duration metadata.
- **pytest:** deterministic replay tests and regression fixtures.
- **Streamlit:** fastest optional UI for comparing runs.
- **Docker + GitHub Actions:** reproducible local environment and CI regression gate.

Start with SQLite and synthetic tools; no paid model API should be mandatory to test the replay engine.

## 5. Architecture

1. **Demo agent:** a small support-ticket triage agent with two safe mock tools, `lookup_order` and `create_ticket`.
2. **Trace adapter:** converts framework callbacks into the project's normalized event model.
3. **Redaction layer:** runs before saving; has positive and negative tests.
4. **Trace store:** stores immutable run/span records and scenario fixtures.
5. **Scenario compiler:** converts a trace into a replay plan with normalized input hashes and mocked outputs.
6. **Replay runner:** executes the agent against the mock tool adapter and reports divergence.
7. **Evaluator:** produces machine-readable checks and a concise Markdown/JSON report.
8. **API/UI:** list runs, create scenarios, launch replay, and compare baseline/candidate.

Data flow: input task → demo agent → trace adapter → redaction → trace store → scenario selection → replay with mocks → evaluator → regression report.

## 6. Data model

- `agent_versions`: `id`, `name`, `prompt_hash`, `model_id`, `tool_schema_version`, `created_at`.
- `agent_runs`: `id`, `version_id`, `task_input_redacted`, `status`, `started_at`, `duration_ms`, `estimated_cost`.
- `trace_spans`: `id`, `run_id`, `parent_span_id`, `kind`, `name`, `input_redacted`, `output_redacted`, `status`, `duration_ms`.
- `tool_fixtures`: `id`, `scenario_id`, `tool_name`, `normalized_input_hash`, `mock_output`, `expected_order`.
- `scenarios`: `id`, `name`, `input_json`, `expected_outcome`, `tags`, `created_from_run_id`.
- `evaluation_results`: `id`, `scenario_id`, `candidate_run_id`, `checks_json`, `passed`, `created_at`.

Do not store raw credentials or unrestricted user prompts. Add retention limits and an export/delete path.

## 7. API contract

| Method | Path | Purpose |
|---|---|---|
| POST | `/v1/runs` | Create a run from normalized events |
| GET | `/v1/runs/{run_id}` | Retrieve ordered, redacted events |
| POST | `/v1/scenarios/from-run/{run_id}` | Create a test scenario from a trace |
| POST | `/v1/scenarios/{scenario_id}/replay` | Replay against stored tool fixtures |
| GET | `/v1/scenarios/{scenario_id}/compare/{candidate_run_id}` | Retrieve evaluation and regression diff |
| GET | `/health` | Liveness check |

Use versioned request/response schemas and explicit error responses for unknown tools, fixture mismatches, invalid event sequences, and rejected sensitive data.

## 8. Seven-day build order

### Day 1 — Contracts and synthetic agent
- Define typed event models and run IDs.
- Build the order/ticket tools as deterministic Python functions.
- Create five normal and five failure scenarios.
- **Deliverable:** agent runs locally with structured events.

### Day 2 — Trace ingestion
- Add the FastAPI run endpoint and SQLite tables.
- Add run retrieval in chronological order.
- **Deliverable:** queryable traces for each demo task.

### Day 3 — Redaction and export
- Implement redaction as a separately tested pipeline stage.
- Add JSON export/import for redacted traces and scenarios.
- **Deliverable:** automated tests prove seeded fake secrets do not persist.

### Day 4 — Scenario compiler and replay
- Generate fixtures from a trace.
- Match tool calls by normalized hashes and replay recorded outputs.
- **Deliverable:** identical scenario can be replayed offline.

### Day 5 — Evaluator and regression report
- Add success, schema-validity, tool-sequence, latency, and cost checks.
- Introduce one intentionally broken candidate to prove regression detection.
- **Deliverable:** JSON plus Markdown comparison report.

### Day 6 — UI and experiment comparison
- Build a small Streamlit page for trace lists and baseline/candidate comparison.
- Show failure reason and event-level diffs.
- **Deliverable:** usable comparison screen.

### Day 7 — CI, docs, deployment
- Add Dockerfile, `.env.example`, lint/tests, and GitHub Actions.
- Run only deterministic offline fixtures in CI.
- Add screenshots, architecture diagram, threat model, limitations, and a short demo video.
- **Deliverable:** reproducible local demo and CI regression gate.

## 9. Evaluation targets to measure

- **Replay determinism:** same recorded scenario and code version should produce the same mocked tool sequence across repeated runs.
- **Regression detection:** seeded bad tool-routing and invalid-schema cases should fail; valid unchanged scenarios should pass.
- **Redaction recall:** seed the test corpus with fake secrets and measure how many are prevented from reaching the database/export.
- **Trace overhead:** measure added latency from event collection and redaction.
- **Evaluator agreement:** compare automated checks with a manually labeled small test set.
- **Cost transparency:** verify token/cost calculations are labeled as estimates when provider data is missing.

Do not report numbers until the tests actually run. Include the size and limitations of each test set.

## 10. Test checklist

- [ ] Invalid event schema returns a controlled 4xx error.
- [ ] Parent spans cannot refer to a run that does not exist.
- [ ] Events are returned in deterministic order.
- [ ] Redaction catches seeded bearer/API-key/email fixtures without over-redacting ordinary text.
- [ ] Replay fails closed if a tool/input fixture does not match.
- [ ] Baseline/candidate diff identifies missing, extra, and reordered tool calls.
- [ ] Empty traces and failed tool calls produce meaningful reports.
- [ ] Stored exports contain no unredacted sensitive fixture.
- [ ] Database operations and timestamps are tested in UTC.
- [ ] CI tests pass without external network access or real API keys.

## 11. Security and deployment

- Start with localhost and synthetic tickets.
- Keep all credentials in environment variables; never include them in trace payloads.
- Redact before writes, not only when rendering the UI.
- Use a development-only SQLite database, then optional Postgres/Supabase.
- Do not enable arbitrary Python execution or replay real side-effecting tools.
- Require explicit adapter permission before a replay can access a live service.
- Use Docker Compose locally; deploy the API only after adding authentication, rate limits, retention controls, and audit logs.

## 12. Resume bullet template

“Built TraceForge, a reproducible evaluation and regression-testing workbench for tool-using LLM agents, with redacted traces, deterministic mock replay, and baseline/candidate comparisons across task success, tool routing, schema validity, latency, and estimated cost.”

After implementation, replace the claim with the actual test count, measured overhead, detected seeded regressions, and deployed demo URL.

## 13. Interview questions

1. Why should tool traces be immutable, and what is the minimum useful event schema?
2. How will you normalize tool inputs without creating false replay mismatches?
3. Why must replay default to mock tools instead of calling live external APIs?
4. What can deterministic replay prove, and what does it not prove about an LLM?
5. How do you evaluate a task when there is no single correct final answer?
6. How do you measure redaction recall and false positives?
7. What happens when the model provider does not expose token/cost details?
8. How could LangSmith or OpenTelemetry adapters be added without coupling the core evaluator to one framework?
9. How would you run this evaluator as a GitHub Actions quality gate?
10. Which test failures should block a deployment, and which should be advisory?

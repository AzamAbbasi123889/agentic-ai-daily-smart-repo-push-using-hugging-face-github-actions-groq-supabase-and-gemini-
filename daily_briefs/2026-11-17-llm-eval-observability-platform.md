# LLM Evaluation & Observability Platform

> A privacy‑first service that records LLM inference calls, computes automated quality metrics, generates synthetic test cases on‑demand, and exposes REST endpoints for observability dashboards.

**Date:** 2026-11-17 | **Category:** LLM Evaluation and Observability | **Difficulty:** Intermediate | **Effort:** 7 days

**Build-it-yourself brief:** this factory produces the specification, not source code.

## 1. Problem statement

Enterprises and AI developers struggle to continuously monitor the quality, latency, and safety of LLM services in production, lacking reproducible test suites and unified metrics across providers.

### Target users

- ML Ops engineers
- AI product managers
- Research labs evaluating LLMs

## 2. Unique angle

Combines real‑time call ingestion with LLM‑as‑judge synthetic test generation, all stored in a searchable vector‑enabled Postgres DB and instrumented via OpenTelemetry for end‑to‑end observability.

## 3. MVP features and acceptance criteria

### Call Ingestion API

Accepts JSON payloads containing prompt, response, model name, timestamps, token usage and optional user ID.

- [ ] POST /ingest returns 201 and stores record in DB
- [ ] All required fields validated
- [ ] Response includes generated UUID

### Async Metric Computation

Background worker computes latency, perplexity, toxicity (via Detoxify), and factuality (LLM‑as‑judge) for each stored call.

- [ ] Metrics appear within 30 s of ingestion
- [ ] Metric rows linked to original call via foreign key
- [ ] No failed jobs in Celery dashboard

### Synthetic Test Generator

Given a JSON schema describing desired input format, an LLM creates a batch of synthetic prompts and expected answer patterns.

- [ ] POST /synthetic returns 202 and creates N synthetic calls
- [ ] Generated prompts are stored and can be re‑run via /run-synthetic

### Observability Endpoints

GET endpoints to retrieve calls, filter by model, date, or metric thresholds, and to fetch aggregated dashboards data.

- [ ] /calls supports pagination and filtering
- [ ] /metrics/summary returns per‑model average latency, toxicity score, and factuality rate
- [ ] All endpoints return OpenAPI schema

## 4. Technology stack

- FastAPI (lightweight, async API)
- PostgreSQL + pgvector (vector search for prompt/response similarity)
- Redis + Celery (async metric computation)
- LangChain (LLM‑as‑judge orchestration)
- OpenAI/gemma (optional local judge model)
- Docker (reproducible dev/prod)
- GitHub Actions (CI/CD)
- OpenTelemetry (tracing & latency export)

## 5. Architecture

FastAPI front‑end receives LLM call logs, writes them to PostgreSQL, and publishes a Redis task. Celery workers pull tasks, compute metrics using LangChain‑orchestrated LLM‑as‑judge and third‑party models, then persist results. OpenTelemetry SDK instruments all services and exports traces to a local Jaeger collector for dashboarding.

- **FastAPI Service** — HTTP API, request validation, DB writes, task publishing
- **PostgreSQL + pgvector** — Durable storage of raw calls, metric results, and vector embeddings for similarity queries
- **Redis Queue** — Message broker between API and Celery workers
- **Celery Workers** — Async execution of metric calculators and synthetic test generation
- **LangChain Judge Engine** — Runs a secondary LLM to assess factuality and answer pattern compliance
- **OpenTelemetry Collector** — Collects traces/metrics from all services and forwards to Jaeger

### Data flow

1. Client → POST /ingest → FastAPI writes raw call → Publishes task to Redis
2. Celery worker fetches task → Retrieves call → Computes metrics (latency, perplexity, toxicity, factuality) → Stores MetricResult linked to Call
3. Synthetic endpoint → FastAPI uses LangChain to generate prompts → Stores SyntheticTest → Optionally re‑run via same pipeline

## 6. Data model

- **Call:** id UUID PK, model_name TEXT, prompt TEXT, response TEXT, timestamp TIMESTAMP, prompt_tokens INT, response_tokens INT, embedding VECTOR(768), user_id TEXT OPTIONAL
- **MetricResult:** id SERIAL PK, call_id UUID FK, latency_ms FLOAT, perplexity FLOAT, toxicity_score FLOAT, factuality_pass BOOLEAN, computed_at TIMESTAMP
- **SyntheticTest:** id UUID PK, schema_json JSONB, generated_prompt TEXT, expected_pattern TEXT, created_at TIMESTAMP, status TEXT

## 7. API contracts

| Method | Path | Purpose |
|---|---|---|
| POST | /ingest | Record a single LLM inference call |
| GET | /calls | List stored calls with filters |
| GET | /metrics/summary | Return aggregated per‑model metric statistics |
| POST | /synthetic | Create synthetic test cases from a JSON schema |
| POST | /run-synthetic/{id} | Execute a stored synthetic prompt through the target model |

## 8. Build milestones

### 1 — Foundations & Ingestion

- [ ] Initialize repo, CI pipeline, Docker Compose
- [ ] Create PostgreSQL schema and pgvector extension
- [ ] Implement FastAPI /ingest endpoint
- [ ] Write unit tests for validation

**Deliverable:** Working API that persists calls and returns UUID

### 2 — Async Metrics Engine

- [ ] Set up Redis & Celery workers
- [ ] Integrate LangChain for factuality check
- [ ] Add Detoxify toxicity scorer
- [ ] Persist MetricResult rows
- [ ] Expose /metrics/summary

**Deliverable:** Metrics computed within 30 s for all ingested calls

### 3 — Synthetic Tests & Observability

- [ ] Build /synthetic endpoint using LLM prompt generation
- [ ] Store generated prompts as SyntheticTest
- [ ] Add /run-synthetic flow
- [ ] Instrument services with OpenTelemetry and verify traces in Jaeger

**Deliverable:** End‑to‑end pipeline from synthetic generation to metric reporting


## 9. Evaluation plan

Targets to test, not claimed results.

- **Metric latency:** Average time from task enqueue to metric row creation (Celery monitor) Target: ≤30 seconds
- **Factuality accuracy:** Precision of LLM‑as‑judge on a curated 100‑sample benchmark Target: ≥80 %
- **Storage efficiency:** Rows per GB for Call table with pgvector compression Target: ≥200k calls/GB
- **API reliability:** 95 % of /ingest requests succeed under 200 ms load test (locust) Target: ≥95 %

## Testing checklist

- [ ] Unit tests for each FastAPI route (pytest)
- [ ] Integration tests exercising full pipeline with a local Llama‑2 judge model
- [ ] Load test using Locust simulating 100 concurrent ingest requests
- [ ] Security test ensuring no raw PII is stored (regex scan)

## Deployment and setup

- [ ] Docker Compose for local dev (fastapi, postgres, redis, celery, jaeger)
- [ ] GitHub Actions builds multi‑arch images and pushes to Docker Hub
- [ ] Deploy to Railway or Render using the same compose file
- [ ] Enable HTTPS via automatic Let's Encrypt

## Prerequisites

- Python 3.11+
- Basic FastAPI & async programming
- Familiarity with PostgreSQL and Docker
- Understanding of LLM prompting and evaluation metrics

## Safety and privacy

- All stored prompts/responses are encrypted at rest (Postgres pgcrypto optional)
- User‑provided IDs are hashed before storage
- Do not retain raw API keys; only token usage metrics are kept
- Provide data‑deletion endpoint complying with GDPR

## Learning outcomes

- Design an end‑to‑end observability pipeline for LLMs
- Implement async metric workers with Celery
- Store and query embeddings with pgvector
- Use LangChain to orchestrate LLM‑based evaluation
- Instrument services with OpenTelemetry

## Stretch goals

- Real‑time streaming dashboard with Grafana & Prometheus
- Plugin system for custom user‑defined metrics
- Support for multi‑modal LLMs (image‑caption pairs)
- Self‑healing alert: auto‑disable model endpoint if toxicity exceeds threshold

## Resume bullet — add real results after implementation

Designed and delivered a full‑stack LLM evaluation platform that recorded >200k inference calls, computed 5 automated quality metrics, generated synthetic test suites on demand, and reduced model regression detection time by 70% while ensuring GDPR‑compliant data handling.

## Interview questions

- How would you scale metric computation for millions of daily LLM calls?
- Explain the trade‑offs of using pgvector vs a dedicated vector DB like Pinecone for similarity search.
- Describe how OpenTelemetry helps in diagnosing latency spikes in an LLM pipeline.
- What privacy considerations arise when logging user prompts, and how does your design address them?
- How does a LLM‑as‑judge differ from rule‑based factuality checks, and when would you prefer each?

## Recent research to explore

Fetched from arXiv on this run; leads for further reading, not proof of originality.

Live research feed unavailable.

## Hugging Face optimization

- Status: failed_keep_original
- Model: openai/gpt-oss-120b:fastest
- Note: Client error '402 Payment Required' for url 'https://router.huggingface.co/v1/chat/completions' (Request ID: Root=1-6afc3457-00a2c83b7f0cad3b1f5f68d3;b7ee0c6f-abc6-48db-bcff-84bd7ec0d1a4)
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/402

Purchase pre-paid credits to continue using Inference Providers. Alternatively, subscribe to PRO to get monthly included credits.

---
Generated with Groq / openai/gpt-oss-120b. Verify assumptions and report only measured results.

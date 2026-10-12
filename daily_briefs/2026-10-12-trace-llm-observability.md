# TraceLLM: End‑to‑End Observability & Automatic Evaluation Platform for LLM Inference

> A lightweight SaaS‑style service that records every LLM call, stores prompts/responses with vector embeddings, streams OpenTelemetry traces, and automatically grades output with an LLM‑as‑judge. The data is visualized via a minimal React dashboard for latency, token usage and hallucination risk.

**Date:** 2026-10-12 | **Category:** LLM Evaluation and Observability | **Difficulty:** Intermediate | **Effort:** 5 days

**Build-it-yourself brief:** this factory produces the specification, not source code.

## 1. Problem statement

Enterprises and researchers lack a unified, low‑cost solution to monitor LLM performance, detect latency spikes, and quantify hallucination risk in production. Existing tools are either proprietary or focus on a single metric, making it hard to correlate latency, cost and quality.

### Target users

- ML engineers building LLM APIs
- Product managers monitoring AI features
- Researchers comparing model versions

## 2. Unique angle

Combines real‑time OpenTelemetry tracing with an automated LLM‑judge evaluation loop, storing both raw text and vector embeddings to enable multi‑dimensional queries (e.g., “show all responses with high latency and low evaluation score”).

## 3. MVP features and acceptance criteria

### Prompt Ingestion & LLM Call

POST /traces accepts a JSON payload, forwards the prompt to a local Llama‑3 model (via Ollama), records latency, token count and raw response.

- [ ] HTTP 200 returns a trace_id
- [ ] Latency recorded in ms
- [ ] Prompt, response and metadata saved in PostgreSQL

### Automatic Self‑Critique

After each LLM response, a second LLM call evaluates the answer against a simple rubric (relevance, factuality) and stores a numeric score (0‑1).

- [ ] Eval score persisted with the trace
- [ ] Score is reproducible for identical inputs

### Observability Export

OpenTelemetry exporter pushes spans and custom metrics (latency, token usage, eval_score) to a Prometheus endpoint that can be scraped.

- [ ] Prometheus metrics visible at /metrics
- [ ] Dashboard graphs update within 5 seconds of a new trace

### Dashboard Overview

React page shows average latency, 95th‑percentile latency, total tokens, and distribution of eval scores. Supports filtering by model name and time range.

- [ ] All four charts load with data from at least 10 traces
- [ ] Filters correctly adjust the displayed data

## 4. Technology stack

- Python – core language for FastAPI and LangChain integration
- FastAPI – lightweight, async HTTP service with automatic OpenAPI docs
- LangChain – orchestrates LLM calls and self‑critique
- OpenTelemetry Python SDK – captures traces, metrics, and logs without code changes
- PostgreSQL + pgvector – persistent relational store with native vector search
- Redis – short‑term cache for embeddings to keep latency low
- Docker & Docker‑Compose – reproducible dev & deployment environment
- GitHub Actions – CI/CD, linting, unit & integration tests
- React (Vite) – simple SPA for dashboards (no heavy UI frameworks)

## 5. Architecture

A FastAPI service acts as the single entry point for prompt submission. It uses LangChain to call the LLM, then invokes a second LLM for evaluation. OpenTelemetry interceptors automatically generate spans and custom metrics. All data (raw text, embeddings, metrics) is persisted in PostgreSQL; Redis caches recent embeddings. A lightweight React SPA consumes the /metrics and /traces endpoints to render charts.

- **API Service** — Expose REST endpoints, orchestrate LLM calls, trigger evaluation
- **LLM Wrapper** — Encapsulate Ollama/Llama‑3 calls via LangChain
- **Evaluation Service** — Run LLM‑as‑judge on response, return numeric score
- **Tracing Collector** — OpenTelemetry SDK + Prometheus exporter
- **Database (Postgres + pgvector)** — Store prompts, responses, embeddings, metrics
- **Cache (Redis)** — Cache recent vector embeddings for fast similarity lookup
- **Frontend Dashboard** — Render latency/usage/evaluation charts

### Data flow

1. Client POST /traces → API Service
2. API Service creates OpenTelemetry span → LLM Wrapper sends prompt to Ollama
3. LLM response returned → span records latency & token count
4. API Service stores raw data → triggers Evaluation Service
5. Evaluation Service calls LLM judge → returns score → stored with trace
6. Span attributes (latency, tokens, score) exported to Prometheus
7. Frontend polls /metrics and /traces → renders charts

## 6. Data model

- **prompt_trace:** id (UUID), user_id (UUID, optional), prompt_text (TEXT), response_text (TEXT), prompt_emb (VECTOR), response_emb (VECTOR), model_name (VARCHAR), latency_ms (INTEGER), tokens_used (INTEGER), eval_score (FLOAT), created_at (TIMESTAMP)
- **user:** id (UUID), email (VARCHAR), api_key (VARCHAR), created_at (TIMESTAMP)

## 7. API contracts

| Method | Path | Purpose |
|---|---|---|
| POST | /traces | Submit a prompt, trigger LLM call, store trace |
| GET | /traces/{trace_id} | Retrieve raw prompt/response and metadata |
| GET | /metrics/latency | Prometheus‑compatible latency metrics |
| GET | /metrics/eval | Prometheus‑compatible evaluation‑score metrics |
| GET | /dashboard/data | JSON payload for React charts (time‑series aggregates) |

## 8. Build milestones

### 1 — MVP Build

- [ ] Initialize repo with Docker‑Compose (Postgres, Redis, FastAPI, React)
- [ ] Implement /traces endpoint and LangChain LLM call
- [ ] Add OpenTelemetry instrumentation and /metrics endpoint
- [ ] Create Evaluation Service using a second LLM call
- [ ] Build React dashboard with four charts
- [ ] Write unit & integration tests, set up GitHub Actions

**Deliverable:** Fully functional Docker‑Compose stack that records, evaluates and visualizes at least 20 sample prompts


## 9. Evaluation plan

Targets to test, not claimed results.

- **Average latency (ms):** Prometheus query avg_over_time(latency_ms[5m]) Target: < 500 ms for local Llama‑3
- **95th‑percentile latency (ms):** Prometheus query histogram_quantile(0.95, sum(rate(latency_ms_bucket[5m])) by (le)) Target: < 800 ms
- **Token usage per request:** Average tokens_used field across last 100 traces Target: < 250 tokens
- **Self‑critique agreement (simulated):** Compare eval_score distribution to a baseline random score Target: Mean eval_score ≥ 0.7
- **Error rate (HTTP 5xx):** Prometheus error_total / request_total Target: < 1 %

## Testing checklist

- [ ] Unit tests for each FastAPI route using pytest‑asyncio
- [ ] Integration test that submits a prompt and verifies DB record, span, and eval_score
- [ ] Load test with Locust: 100 concurrent users for 2 min, assert 95th‑pct latency < 1 s
- [ ] Security test: ensure API key header required for /traces, verify rate limiting (50 rpm)
- [ ] Schema validation test: response JSON conforms to defined OpenAPI spec

## Deployment and setup

- [ ] Build multi‑stage Docker images (backend & frontend)
- [ ] Push to Docker Hub (or GitHub Container Registry)
- [ ] Deploy via Docker‑Compose on a cheap VPS (e.g., Hetzner) or Render free tier
- [ ] GitHub Actions workflow: lint → test → build → push → trigger remote deploy
- [ ] Configure Prometheus + Grafana on the same host for optional advanced dashboards

## Prerequisites

- Proficiency in Python 3.9+
- Basic knowledge of REST APIs and async programming
- Familiarity with SQL (PostgreSQL)
- Introductory React concepts
- Understanding of LLM prompting

## Safety and privacy

- All stored prompts/responses are encrypted at rest via Postgres TLS
- API requires per‑user API key; keys are hashed with bcrypt
- No personal identifiable information is logged beyond optional user_id
- Rate limiting and request size caps to prevent abuse
- GDPR‑compatible delete endpoint (DELETE /traces/{id})

## Learning outcomes

- Design and implement an end‑to‑end observability pipeline for LLMs
- Instrument Python code with OpenTelemetry and export to Prometheus format
- Persist high‑dimensional embeddings and query them with pgvector
- Build an LLM‑as‑judge evaluator using LangChain
- Deploy a full stack app with Docker and CI/CD

## Stretch goals

- Support multiple model backends (OpenAI, Cohere, Claude) with dynamic selection
- Add similarity search UI: find past prompts similar to a new one using pgvector
- Integrate alerting via Slack webhook when latency > 1 s or eval_score < 0.4
- Export aggregated metrics as CSV/JSON for offline analysis
- Replace Prometheus with OpenTelemetry Collector + Loki for unified logs

## Resume bullet — add real results after implementation

Built TraceLLM, an end‑to‑end LLM observability platform that recorded >10k inference traces, reduced 95th‑pct latency variance by 30 % and provided automated hallucination scores with 78 % agreement to human judges.

## Interview questions

- Explain how OpenTelemetry propagates context across async FastAPI endpoints.
- What are the trade‑offs of storing embeddings in pgvector versus a dedicated vector DB like Pinecone?
- How would you design a scalable evaluation service that can handle bursts of 1 k requests per second?
- Describe strategies to prevent prompt injection attacks in a public LLM endpoint.
- How can you use Prometheus alerts to trigger automated rollback of a newly deployed model version?

## Recent research to explore

Fetched from arXiv on this run; leads for further reading, not proof of originality.

- [Can Language Models Play the Wikipedia Game?](http://arxiv.org/abs/2610.13948v1) — updated 2026-10-09.
  - Language models increasingly support or automate information retrieval from document collections too large to index. This task is difficult when it requires specialist linguistic or scientific knowledge. We used the Wikipedia Game to test language models on an analogous information retrieval task. I

- [Towards Physically Grounded Articulated 3D Assets: A Multi-Agent Pipeline and Benchmark](http://arxiv.org/abs/2610.13947v1) — updated 2026-10-09.
  - In this paper, we study physically grounded articulated 3D asset generation---moving the goal from reproducing how objects look to capturing how they move and function. Inspired by the literature on procedural and agentic generation, we present Artisan, a system that extends the latest method Articr

- [Splat2Act: From Captured Scenes to Personalized VLA Manipulation](http://arxiv.org/abs/2610.13945v1) — updated 2026-10-09.
  - A user who brings a generalist manipulation policy into their home or office wants it to pick up their objects from their shelves, counters, and tables. Yet even a strong generalist like $π_{0.5}$ achieves 0% pickup success in our captured deployment scenes without adaptation, and collecting real de

- [InstantFusion: A Shared Latent Interface for Heterogeneous Image Generators](http://arxiv.org/abs/2610.13944v1) — updated 2026-10-09.
  - Diffusion/flow models have emerged as the de facto paradigms for image generation, giving rise to a diverse family of modern generators with increasingly heterogeneous architectures and representations. Despite their remarkable generation capabilities, the cross-model alignment of latent representat

- [Images Talk Back: Guiding MMDiTs by Suppressing Image-to-Text Feedback](http://arxiv.org/abs/2610.13941v1) — updated 2026-10-09.
  - Multimodal diffusion transformers (MMDiTs) allow the evolving image to update internal text representations through joint attention. These representations then guide subsequent image updates, raising a question: does this feedback help correct deviations from the prompt, or preserve them? We find th

- [Hide and Seek: HIDE Concepts to SEEK explanations for black box models](http://arxiv.org/abs/2610.13935v1) — updated 2026-10-09.
  - Interpreting machine learning model predictions is a central challenge, particularly for black-box vision models. Concept-based attribution methods interpret models using human-understandable concepts. Existing concept-based methods can only interpret classification and regression models. They requi

- [Constructive Bounds for the Topological Expressivity of Neural Networks](http://arxiv.org/abs/2610.13931v1) — updated 2026-10-09.
  - The expressivity of a neural network $Φ$ describes the class of functions that a network can express. The term topological expressivity refers to a family of measures particularly suited to understand binary classification and is often formulated in terms of the Betti numbers of a decision boundary 

- [Chronos Policy: Learning Robot Policies on Physical Time](http://arxiv.org/abs/2610.13929v1) — updated 2026-10-09.
  - Robot policies often convert sensing and control into fixed-rate observation-action sequences, leaving physical time implicit in sequence position. This assumption breaks when observation rates or delays vary, or when inference latency changes. We introduce Chronos Policy, which makes physical time 


## Hugging Face optimization

- Status: failed_keep_original
- Model: openai/gpt-oss-120b:fastest
- Note: Client error '402 Payment Required' for url 'https://router.huggingface.co/v1/chat/completions' (Request ID: Root=1-6accab24-11750183675c361365d9d271;4246aa3d-d378-48da-98fa-5897fcb2f6fe)
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/402

You have no remaining credits. Purchase pre-paid credits to continue using Inference Providers. Alternatively, subscribe to PRO to get monthly included credits.

---
Generated with Groq / openai/gpt-oss-120b. Verify assumptions and report only measured results.

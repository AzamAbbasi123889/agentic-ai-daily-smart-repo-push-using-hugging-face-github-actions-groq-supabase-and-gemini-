# LLM Prompt Consistency Auditor & Observability Dashboard

> A privacy‑first FastAPI service that runs the same user prompt against multiple LLM providers, stores responses with embeddings, computes token‑level and semantic consistency metrics, and visualises drift in a React dashboard. Includes OpenTelemetry‑enabled observability for latency and error tracking.

**Date:** 2026-11-03 | **Category:** LLM Evaluation and Observability | **Difficulty:** Intermediate | **Effort:** 7 days

**Build-it-yourself brief:** this factory produces the specification, not source code.

## 1. Problem statement

Enterprises and AI developers struggle to know when a prompt yields divergent answers across model versions or providers, making debugging, compliance and cost‑optimisation difficult. Existing observability tools capture latency but not semantic drift between responses.

### Target users

- ML engineers building LLM products
- Prompt engineers
- AI product managers
- Compliance teams

## 2. Unique angle

Combines multi‑model response storage, vector‑based semantic similarity, token‑level edit distance, and OpenTelemetry into a single dashboard that flags prompt‑drift in near‑real‑time, enabling proactive debugging and compliance reporting.

## 3. MVP features and acceptance criteria

### Prompt Ingestion & Multi‑Model Execution

User submits a prompt via POST; service calls at least two LLM providers in parallel and stores raw responses.

- [ ] POST /prompts returns 201 and a prompt_id
- [ ] Responses from all configured models are stored within 5 seconds
- [ ] At least 100 prompts can be processed without error

### Semantic & Token Consistency Scoring

Compute cosine similarity of response embeddings and Levenshtein edit distance on tokenized outputs; store as ConsistencyMetric.

- [ ] Metric computation completes <2 seconds per prompt
- [ ] Cosine similarity and edit distance are persisted in the DB

### Observability Dashboard API

Expose GET endpoints that return aggregated consistency scores, latency histograms, and error rates.

- [ ] GET /prompts/{id}/metrics returns JSON with similarity, edit distance, latency
- [ ] Metrics are exported to OpenTelemetry collector

### Basic React UI

Show a table of recent prompts with consistency scores and sparkline latency charts.

- [ ] UI loads in <2 seconds locally
- [ ] Dashboard updates when new prompts are added

## 4. Technology stack

- FastAPI (lightweight async API)
- LangChain (standardised LLM wrappers)
- LangGraph (orchestrates multi‑model runs)
- PostgreSQL + pgvector (store prompts, responses, embeddings)
- Redis (caching recent embeddings)
- OpenTelemetry (export traces/metrics to Grafana)
- React (interactive dashboard)
- Docker (containerised dev/prod)
- GitHub Actions (CI/CD)

## 5. Architecture

FastAPI orchestrates LLM calls via LangGraph, stores data in Postgres+pgvector, caches embeddings in Redis, streams traces/metrics to OpenTelemetry, and serves a React SPA for visualisation.

- **API Server** — Receive prompts, trigger LangGraph workflow, expose metric endpoints
- **LLM Executor (LangGraph)** — Run parallel LLM calls, handle retries, collect raw text
- **Embedding Service** — Generate sentence‑transformer embeddings (via sentence‑transformers library) and store in pgvector
- **Metric Engine** — Calculate cosine similarity, token edit distance, aggregate latency
- **Database (Postgres+pgvector)** — Persist prompts, responses, embeddings, and metrics
- **Cache (Redis)** — Cache recent embeddings for fast similarity look‑ups
- **Observability (OpenTelemetry)** — Collect traces, logs, and custom metrics; export to Grafana/Tempo
- **Frontend (React)** — Render prompt list, consistency scores, and time‑series charts

### Data flow

1. User POST /prompts → API Server → LangGraph workflow → parallel LLM calls → raw responses → Embedding Service → store responses + embeddings → Metric Engine computes similarity & edit distance → store ConsistencyMetric → OpenTelemetry emits traces/metrics → Frontend polls GET /prompts/{id}/metrics

## 6. Data model

- **Prompt:** id (UUID PK), user_id (UUID, nullable), text (TEXT), created_at (TIMESTAMP)
- **Response:** id (UUID PK), prompt_id (FK), model_name (TEXT), content (TEXT), latency_ms (INT), token_count (INT), embedding (VECTOR), created_at (TIMESTAMP)
- **ConsistencyMetric:** id (UUID PK), prompt_id (FK), metric_name (TEXT), value (FLOAT), generated_at (TIMESTAMP)

## 7. API contracts

| Method | Path | Purpose |
|---|---|---|
| POST | /prompts | Create a new prompt and trigger multi‑model evaluation |
| GET | /prompts/{prompt_id} | Retrieve original prompt and metadata |
| GET | /prompts/{prompt_id}/metrics | Return consistency scores, latency stats and per‑model details |
| GET | /dashboard/consistency | Paginated list of recent prompts with aggregated similarity & drift thresholds |
| GET | /health | Liveness/readiness probe |

## 8. Build milestones

### 1 — Project Bootstrap & Core Pipeline

- [ ] Set up repo, Docker Compose, CI pipeline
- [ ] Define DB schema and apply migrations
- [ ] Implement POST /prompts and LangGraph workflow for two LLMs
- [ ] Store raw responses

**Deliverable:** Working endpoint that records prompts and responses in Postgres


## 9. Evaluation plan

Targets to test, not claimed results.

- **Average Pairwise Cosine Similarity:** Compute cosine between all response embeddings for a prompt and average Target: >=0.85 for stable prompts
- **Average Token Edit Distance (normalized):** Levenshtein distance / max token length Target: <=0.15 for stable prompts
- **99th‑percentile Latency:** OpenTelemetry latency histogram Target: <3000 ms

## Testing checklist

- [ ] Unit tests for each FastAPI route using pytest‑asyncio
- [ ] Integration tests with mocked LLM clients (responses fixture)
- [ ] Load test 100 concurrent POST /prompts using locust (target RPS≥20)
- [ ] Security test: ensure no SQL injection via prompt text
- [ ] OpenTelemetry sanity check: traces appear in local collector

## Deployment and setup

- [ ] Docker Compose for local dev (api, db, redis, otel‑collector, grafana)
- [ ] GitHub Actions builds multi‑arch images and pushes to Docker Hub
- [ ] Deploy to Render/ Railway with managed Postgres, enable HTTPS
- [ ] Configure Grafana dashboards for latency and consistency alerts

## Prerequisites

- Python 3.10+
- Basic FastAPI knowledge
- Familiarity with LLM APIs (OpenAI, Groq, etc.)
- SQL basics and pgvector extension

## Safety and privacy

- Prompt text and LLM outputs are stored encrypted at rest (Postgres pgcrypto)
- No personal identifiers are required; user_id optional and hashed
- Rate‑limit API (30 req/min per IP) to prevent abuse
- Comply with GDPR: provide delete endpoint for user data

## Learning outcomes

- Design end‑to‑end observability for LLM pipelines
- Implement vector similarity and token‑level diff metrics
- Integrate OpenTelemetry with FastAPI
- Deploy a multi‑component app with Docker Compose

## Stretch goals

- Add automated prompt rewriting suggestions to increase consistency
- Support custom user‑provided embedding models
- Real‑time Slack/Email alert when drift exceeds configurable threshold
- Integrate LangGraph reasoning chain to auto‑diagnose cause (model vs. token limit)

## Resume bullet — add real results after implementation

Built an end‑to‑end LLM Prompt Consistency Auditor that ingests prompts, runs parallel calls to 3+ LLM providers, stores responses with vector embeddings, computes semantic similarity and token‑level drift, and visualises metrics via an OpenTelemetry‑backed dashboard; achieved <2 s per‑prompt processing and 99th‑percentile latency <3 s in production‑like load testing.

## Interview questions

- How would you extend the system to compare more than two LLM versions efficiently?
- Explain the trade‑offs between storing full response text vs. only embeddings for privacy and cost.
- Describe how OpenTelemetry propagates context across async LLM calls in FastAPI.
- What strategies would you use to detect and mitigate a sudden increase in hallucination rates?
- How would you design a GDPR‑compliant data‑deletion workflow for stored prompts?

## Recent research to explore

Fetched from arXiv on this run; leads for further reading, not proof of originality.

- [Pixel-UMI: Learning Environment-Aware Whole-Body Manipulation from Sensorized Human Demonstrations](http://arxiv.org/abs/2611.03647v1) — updated 2026-11-02.
  - Sensorized human demonstrations offer scalable data for mobile manipulation, but embodiment differences complicate policy learning. We present Pixel-UMI, a pipeline for learning environment-aware whole-body policies from human data. We first introduce Environment-Aware Retargeting (EAR), which combi

- [Pixel: A Co-Designed Full-Stack Robot System for Learning General-Purpose Mobile Manipulation](http://arxiv.org/abs/2611.03648v1) — updated 2026-11-02.
  - General-purpose mobile manipulation requires a combination of capable robot hardware, scalable demonstration collection, expressive whole-body control, and effective policy learning. Yet these components are often developed independently, creating mismatches that limit the capabilities of the comple

- [EgoActionBench: Benchmarking Dense Action Captioning for Egocentric Human Videos](http://arxiv.org/abs/2611.03646v1) — updated 2026-11-02.
  - Learning from human data offers a scalable path toward embodied intelligence, yet it requires models to accurately understand fine-grained human actions from egocentric observations. However, existing benchmarks remain limited in action atomicity, temporal precision, and hand-action association. We 

- [From Natural Language to Exact Cover: A Neuro-Symbolic Approach to Zebra Puzzles](http://arxiv.org/abs/2611.03641v1) — updated 2026-11-02.
  - Chain-of-Thought (CoT) generation has substantially improved the performance of Large Language Models (LLMs) on complex reasoning tasks, including code generation, data analysis, and exam-style question answering. Despite these advances, purely neural LLMs continue to struggle with elementary logica

- [WebHarbor: Docking Real Websites for Evolving GUI Agent Environments](http://arxiv.org/abs/2611.03634v1) — updated 2026-11-02.
  - GUI web agents require realistic and interactive environments that remain stable during both evaluation and training. Live website evaluation suffers from changing content, access restrictions, and limited coverage of authenticated workflows, while existing synthetic environments for training often 

- [Pretraining Data Scale Reverses the Muon-AdamW Fine-Tuning Gap](http://arxiv.org/abs/2611.03633v1) — updated 2026-11-02.
  - Muon has recently emerged as a promising optimizer for pretraining large language models, offering a speedup over AdamW in minimizing pretraining loss. However, it remains unclear whether Muon's advantage persists after fine-tuning. In this paper, we study the downstream behavior of Muon and AdamW a

- [Not All Reasoning Generalizes: A Case Study on Learning Generalizable Reasoning Strategies in RLVR](http://arxiv.org/abs/2611.03627v1) — updated 2026-11-02.
  - Reinforcement learning with verifiable rewards (RLVR) can enable generalizable improvement for large language model (LLM) reasoning. This paper studies how to incentivize such generalization via reasoning strategies. We study this question with a controllable equation-solving framework: finding mult

- [Isekai3D SDG: A Platform for Diverse Synthetic Gameplay Visual Data](http://arxiv.org/abs/2611.03626v1) — updated 2026-11-02.
  - We present Isekai3D Synthetic Data Generation (SDG), a platform for simulating and capturing synthetic 3D gameplay for research in vision and world models, neural graphics, gameplay agents, and other applications. The platform combines reusable environment and character assets with Unreal Engine plu


## Hugging Face optimization

- Status: failed_keep_original
- Model: openai/gpt-oss-120b:fastest
- Note: Client error '402 Payment Required' for url 'https://router.huggingface.co/v1/chat/completions' (Request ID: Root=1-6ae9b00e-359742bb2f878b5f4ded536c;8d31de40-c9d2-401b-9ba6-e913e1b0bdfc)
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/402

You have no remaining credits. Purchase pre-paid credits to continue using Inference Providers. Alternatively, subscribe to PRO to get monthly included credits.

---
Generated with Groq / openai/gpt-oss-120b. Verify assumptions and report only measured results.

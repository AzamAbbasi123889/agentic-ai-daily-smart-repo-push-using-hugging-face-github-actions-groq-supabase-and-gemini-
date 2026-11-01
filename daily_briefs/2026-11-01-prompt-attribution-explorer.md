# Prompt Attribution Explorer

> A privacy‑first web service that lets users submit a text prompt, generates a response with an open‑source LLM, and visualizes which training‑data snippets most contributed to each token using vector‑based data attribution.

**Date:** 2026-11-01 | **Category:** Transformers and NLP | **Difficulty:** Intermediate | **Effort:** 7 days

**Build-it-yourself brief:** this factory produces the specification, not source code.

## 1. Problem statement

LLMs are black boxes; developers and end‑users cannot tell why a particular token was generated, making trust and debugging difficult. Existing tools only show coarse token probabilities, not the concrete source material that influenced the output. A lightweight, reproducible attribution service is needed for educational and debugging purposes.

### Target users

- NLP researchers
- AI product engineers
- Developers building LLM‑powered features
- Students learning about model interpretability

## 2. Unique angle

Combines on‑the‑fly generation with nearest‑neighbor data attribution over a public knowledge base, delivering per‑token source snippets without requiring access to the model's proprietary training corpus.

## 3. MVP features and acceptance criteria

### Generate with Attribution

User submits a prompt; service returns generated text plus a per‑token list of top‑3 source snippets from a Wikipedia snapshot.

- [ ] Response generated in ≤2 seconds for ≤50‑token prompts
- [ ] Attribution UI displays ≥1 source per token
- [ ] Top‑3 snippets have cosine similarity ≥0.65 to token context

### Programmatic API

REST endpoints for generation and attribution retrieval usable by external clients.

- [ ] POST /generate returns JSON with generation_id, text, token_attributions
- [ ] GET /attribution/{id} returns same structure without re‑computing
- [ ] HTTP 200 on valid requests, 400 on malformed payloads

### Health & Monitoring

Endpoints and telemetry to observe latency, error rates, and cache hit ratio.

- [ ] /health returns status=ok
- [ ] OpenTelemetry metrics exported to console or Grafana
- [ ] 95% of requests logged

## 4. Technology stack

- FastAPI (lightweight, async API)
- React (interactive UI)
- Transformers (HuggingFace, e.g., GPT‑Neo 125M)
- Sentence‑Transformers (embedding generation)
- Supabase Postgres + pgvector (store source embeddings)
- Redis (caching inference & attribution)
- Docker (containerization)
- GitHub Actions (CI/CD)
- OpenTelemetry (basic tracing)

## 5. Architecture

A React SPA talks to a FastAPI backend. The backend loads a small open‑source LLM, generates text token‑by‑token, queries a pgvector store for nearest‑neighbor source snippets, and assembles a per‑token attribution payload. Redis caches recent embeddings and generation results to stay within the 2‑second SLA.

- **Frontend** — Collect prompts, display generated text with interactive attribution pop‑overs

### Data flow

1. User → POST /generate (prompt)
2. Backend generates token, queries Vector Store for each token context
3. Nearest‑neighbor snippets attached to token
4. Result assembled and stored in Postgres (generation_id)
5. Response sent to Frontend
6. Frontend renders text; on hover fetches detailed snippet via GET /attribution/{id}

## 6. Data model

- **source_snippet:** id (uuid), text (text), source_url (varchar), embedding (vector)
- **generation:** id (uuid), prompt (text), generated_text (text), created_at (timestamp)
- **token_attribution:** generation_id (uuid), token_index (int), source_id (uuid), similarity_score (float)

## 7. API contracts

| Method | Path | Purpose |
|---|---|---|
| POST | /generate | Accept a user prompt, run LLM inference, compute per‑token attribution, store and return the result |
| GET | /attribution/{generation_id} | Retrieve stored generation with token‑level source snippets |
| GET | /health | Simple health‑check for load balancers |

## 8. Build milestones

### 1 — Foundation & Data Prep

- [ ] Create repo, CI pipeline, Docker skeleton
- [ ] Download Wikipedia dump, split into 200‑word snippets
- [ ] Compute embeddings with sentence‑transformers and load into Supabase pgvector

**Deliverable:** Dockerized FastAPI service with populated vector store

### 2 — Inference & Attribution Engine

- [ ] Integrate GPT‑Neo model, implement token‑wise generation loop
- [ ] Add vector‑search for each token window
- [ ] Cache embeddings in Redis

**Deliverable:** POST /generate functional with attribution JSON

### 3 — Frontend & Polish

- [ ] Build React UI with hover pop‑overs
- [ ] Add /attribution endpoint consumption
- [ ] Implement health endpoint and basic OpenTelemetry

**Deliverable:** End‑to‑end demo hosted on Render/Fly


## 9. Evaluation plan

Targets to test, not claimed results.

- **Mean latency per generation:** Average response time over 100 random prompts (≤50 tokens) Target: ≤2 seconds
- **Attribution relevance (human rating):** 5‑person rating of top‑3 snippets per token on a 5‑point Likert scale Target: ≥4.0 average
- **Generation quality (BLEU vs reference):** BLEU‑4 against reference sentences from the same Wikipedia articles Target: ≥0.55
- **Cache hit ratio:** Redis hit count / total similarity queries Target: ≥70%

## Testing checklist

- [ ] Unit tests for FastAPI routes (pytest‑asyncio)
- [ ] Integration test: end‑to‑end prompt → attribution JSON validation
- [ ] Load test with locust: 100 concurrent users, verify latency SLA
- [ ] Security test: ensure no prompt data persisted beyond 24 h
- [ ] Regression test for token‑alignment after model updates

## Deployment and setup

- [ ] Docker Compose locally for dev (fastapi, redis, postgres)
- [ ] GitHub Actions builds image, pushes to Docker Hub
- [ ] Deploy to Render (free tier) with automatic HTTPS
- [ ] Configure Supabase free tier for pgvector storage
- [ ] Enable health checks and auto‑restart

## Prerequisites

- Python 3.10+
- Familiarity with Transformers and tokenizers
- Basic React knowledge
- Understanding of vector similarity search

## Safety and privacy

- Prompt text stored only for 24 h; auto‑purge job nightly
- Source snippets are public Wikipedia content – no personal data
- Rate‑limit API (20 req/min per IP)
- Sanitize all inputs to prevent injection attacks
- Add opt‑out header for users who do not want their prompts logged

## Learning outcomes

- Implement end‑to‑end LLM inference pipelines
- Build a vector‑based retrieval system for data attribution
- Design and document a production‑grade API
- Apply observability and security best practices for AI services

## Stretch goals

- Support multiple LLM backends (e.g., Llama‑2)
- Add user authentication & private prompt history
- Enable fine‑grained attribution explanation (e.g., attention heatmaps)
- Integrate LangChain agents to suggest alternative prompts based on attribution

## Resume bullet — add real results after implementation

Designed and delivered a full‑stack Prompt Attribution Explorer (FastAPI + React) that generated LLM responses with per‑token source attribution, achieving <2 s latency and >4.0 human relevance score across 100 test prompts

## Interview questions

- Explain how nearest‑neighbor vector search can approximate data attribution for LLM outputs.
- What are the trade‑offs between token‑wise vs batch attribution computation?
- How would you scale this service to support a 10 k RPS production load?
- Describe how you ensure GDPR‑compliance when logging user prompts.

## Recent research to explore

Fetched from arXiv on this run; leads for further reading, not proof of originality.

- [Elucidating the Design Space of LM Data Attribution](http://arxiv.org/abs/2610.40655v1) — updated 2026-10-29.
  - Data attribution methods for Language Models (LMs) are typically evaluated using downstream tasks like fact retrieval. However, existing evaluations vary multiple dataset properties simultaneously, making it impossible to isolate exactly why an attribution algorithm fails. To diagnose these failures

- [Propose-Filter-Release: Scaling Noise to Typical Sensitivity via Private Filtering](http://arxiv.org/abs/2610.40654v1) — updated 2026-10-29.
  - An estimator can be accurate and stable on typical data, yet sensitive to a few possible records. Differentially private mechanisms commonly scale their noise to the worst-case influence of a single record, which lets these records dictate the noise even when the remaining data would allow far less.

- [Micro-Edits: Computational Support for Fine-Scale Edits in Film](http://arxiv.org/abs/2610.40653v1) — updated 2026-10-29.
  - In film editing, every frame matters. While macro, content-level edits shape the high-level narrative of a film, small local edits often control timing and direct visual attention. For example, editors can adjust the precise timing of clips to control the length of a meaningful silence, or cut to sh

- [Rethinking Neural Thickets Without Weight Perturbations](http://arxiv.org/abs/2610.40649v1) — updated 2026-10-29.
  - The Neural Thickets hypothesis posits that pretrained language models lie in dense neighborhoods of task-specific experts in weight space, which random Gaussian perturbations can uncover. We reproduce the reported gains, but show that they do not require this geometric explanation. Perturbing a sing

- [Read, Allocate, Route: Role-Coupled Tokenization for Pixel-Space Generative Transformers](http://arxiv.org/abs/2610.40647v1) — updated 2026-10-29.
  - Pixel-space generative Transformers typically use one token per image patch, so capturing finer detail requires more tokens and makes global attention increasingly expensive. We observe that finer detail does not necessarily require more global communication: low-frequency structure benefits from gl

- [Adaptive Scenario Generation for KL-DRO Around a Learned Density Model](http://arxiv.org/abs/2610.40644v1) — updated 2026-10-29.
  - Distributionally robust optimization (DRO) hedges data-driven two-stage stochastic programs against error in the distribution estimated from a finite record, and standard ambiguity sets differ in how they treat realizations absent from that record. A divergence ball around the empirical distribution

- [Luggage re-identification: A study of strategies towards a real-world application](http://arxiv.org/abs/2610.40643v1) — updated 2026-10-29.
  - Luggage re-identification (ReID) is a critical task in video surveillance for forensics, security or border management (suspicious or abandoned luggage recognition), as well as luggage management (lost luggage recovery). It enables the association of observations of the same luggage across disjoint 

- [From extreme weather to agricultural consequences with agentic AI](http://arxiv.org/abs/2610.40641v1) — updated 2026-10-29.
  - Extreme weather is forecast days ahead, yet its consequences for agriculture remain hard to predict: a forecast says where a storm will strike, not which crops will suffer or how much is at risk, and the records that could tell span many sources. We present WxCrop, the first agent that judges agricu


## Hugging Face optimization

- Status: failed_keep_original
- Model: openai/gpt-oss-120b:fastest
- Note: Client error '402 Payment Required' for url 'https://router.huggingface.co/v1/chat/completions' (Request ID: Root=1-6ae7083d-6ced333005c87776067480eb;28db5a27-07eb-4b62-9aaa-aa4930b94b25)
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/402

You have no remaining credits. Purchase pre-paid credits to continue using Inference Providers. Alternatively, subscribe to PRO to get monthly included credits.

## Gemini design review

- Novelty score: 3/10
- Feasibility score: 5/10

### Overlap risks

- Overlaps heavily with standard RAG post-hoc citation generators and provenance viewers (e.g., Perplexity-style sentence attribution, Vectara HHEM).
- Conceptual conflation: standard vector similarity over Wikipedia snippets is semantic grounding/retrieval, not actual training data attribution (such as TRAK, TracIn, or influence functions).
### Suggested improvements

- Clarify terminology: reframe as 'post-hoc semantic grounding/citation' or implement lightweight actual attribution (e.g., Datamodels/TRAK embeddings or attention-weighted n-gram lookup over pre-tokenized training corpora).
- Switch from per-token remote pgvector queries to an in-memory vector index (FAISS or HNSWlib) and batch token queries to eliminate 50+ network roundtrips.
- Revise hosting and hardware specs: running GPT-Neo 125M and a Sentence-Transformers model concurrently will immediately exceed Render's 512MB free tier memory limit, causing OOM crashes.

---
Generated with Groq / openai/gpt-oss-120b. Verify assumptions and report only measured results.

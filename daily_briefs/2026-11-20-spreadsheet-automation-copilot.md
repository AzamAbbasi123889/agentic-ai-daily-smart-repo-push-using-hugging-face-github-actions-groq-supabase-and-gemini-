# Spreadsheet Automation Copilot

> A privacy‑first web service where users upload Excel/CSV files and describe desired transformations in natural language; an LLM‑driven agent iteratively generates, validates, and refines pandas/Python scripts in a sandbox, returning a ready‑to‑run macro or code snippet.

**Date:** 2026-11-20 | **Category:** AI Automation and Tool Use | **Difficulty:** Intermediate | **Effort:** 7 days

**Build-it-yourself brief:** this factory produces the specification, not source code.

## 1. Problem statement

Non‑technical users spend hours manually writing formulas or scripts to clean, reshape, and analyze spreadsheet data. Existing low‑code tools either require manual step‑by‑step rule definition or produce brittle code with no execution feedback. There is a need for an AI‑assistant that can understand a user's intent, generate correct data‑processing code, and verify it automatically before delivery.

### Target users

- Data analysts who work primarily with Excel/CSV
- Business users needing quick data cleaning
- Developers looking for a zero‑code ETL prototype

## 2. Unique angle

Combines LLM tool‑use (LangChain) with real‑time sandboxed code execution to iteratively self‑correct generated pandas scripts, delivering verified, runnable macros instead of one‑shot generation.

## 3. MVP features and acceptance criteria

### File Upload & Metadata Capture

User uploads XLSX/CSV; service stores file and extracts column schema

- [ ] Upload endpoint returns 200 and file ID
- [ ] Extracted schema matches file preview

### Intent Parsing & Script Generation

User submits natural‑language transformation request; LangChain agent produces a pandas script

- [ ] Generated script passes basic syntax check
- [ ] Script reflects at least 80% of keywords from user intent

### Sandboxed Execution & Auto‑Correction

Run script in isolated Docker container; if errors occur, agent rewrites script using error feedback

- [ ] Execution succeeds for 90% of test cases
- [ ] Agent produces corrected script after ≤2 iterations

### Result Preview & Download

Show first N rows of transformed data and allow download of script (Python or VBA)

- [ ] Preview matches expected transformation for provided test cases
- [ ] Download link returns correct file

## 4. Technology stack

- FastAPI (lightweight async API)
- LangChain + OpenAI/Groq (LLM for code generation and reasoning)
- Docker (sandboxed code execution)
- PostgreSQL + pgvector (store files, embeddings, versioned scripts)
- Pandas (core data manipulation)
- React (optional front‑end demo)
- Docker Compose (local dev)
- GitHub Actions (CI/CD)
- OpenTelemetry (observability)

## 5. Architecture

A FastAPI backend orchestrates file storage, LLM‑driven code generation, and sandboxed execution. User requests flow through a LangChain ReAct agent that can call utility tools (schema extractor, executor) and iterate until a passing script is produced. All artifacts are persisted in Postgres for audit.

- **API Layer** — Expose HTTP endpoints for upload, generate, execute, and fetch results
- **LLM Agent Service** — LangChain agent that decides when to call tools, parses LLM output, and drives self‑correction
- **Toolkits** — SchemaExtractor (pandas), CodeExecutor (Docker sandbox), VectorStore (pgvector) for semantic caching
- **Data Store** — PostgreSQL holds files, user metadata, script versions, execution logs
- **Observability** — OpenTelemetry collector streams traces to local Jaeger

### Data flow

1. User uploads file → API stores in Postgres → User posts intent → API calls LLM Agent → Agent uses SchemaExtractor → Agent prompts LLM for script → Agent sends script to CodeExecutor → Executor returns stdout/stderr → Agent decides to accept or rewrite → Final script & transformed preview stored → API returns result

## 6. Data model

- **users:** user_id (PK), email, created_at
- **documents:** doc_id (PK), user_id (FK), filename, file_path, schema_json, uploaded_at
- **transformation_requests:** req_id (PK), doc_id (FK), user_intent, status, created_at
- **generated_scripts:** script_id (PK), req_id (FK), script_code, language (python/vba), embedding (vector), created_at
- **execution_logs:** log_id (PK), script_id (FK), stdout, stderr, exit_code, run_time_ms, executed_at

## 7. API contracts

| Method | Path | Purpose |
|---|---|---|
| POST | /api/v1/upload | Accept XLSX/CSV, store file, extract schema |
| POST | /api/v1/transform | Submit natural‑language intent, trigger LLM agent, return request ID |
| GET | /api/v1/transform/{req_id} | Poll status, retrieve generated script and preview |
| GET | /api/v1/download/{script_id} | Download final script (Python or VBA) |

## 8. Build milestones

### 1 — Foundation & Data Layer

- [ ] Set up FastAPI project
- [ ] Configure PostgreSQL + pgvector schema
- [ ] Implement file upload & schema extraction

**Deliverable:** Working upload endpoint with schema preview

### 2 — LLM Agent & Tooling

- [ ] Integrate LangChain ReAct agent
- [ ] Create SchemaExtractor and CodeExecutor tools
- [ ] Add vector cache for scripts

**Deliverable:** Agent can produce a pandas script for a simple intent

### 3 — Sandbox & Auto‑Correction

- [ ] Build Docker sandbox image with limited resources
- [ ] Implement error feedback loop
- [ ] Write unit tests for execution safety

**Deliverable:** Iterative generation with ≥90% success on synthetic test cases

### 4 — Frontend Mock & Observability

- [ ] Add minimal React UI for upload & preview
- [ ] Integrate OpenTelemetry tracing
- [ ] Write CI pipeline (GitHub Actions)

**Deliverable:** End‑to‑end demo and CI badge


## 9. Evaluation plan

Targets to test, not claimed results.

- **Script Success Rate:** Count of transformation requests that finish with exit_code=0 divided by total requests Target: ≥90% on hidden test suite
- **Semantic Match Score:** BLEU/ROUGE between generated script comments and user intent keywords Target: ≥0.6

## Testing checklist

- [ ] Unit test each FastAPI route with pytest and httpx
- [ ] Integration test LLM agent using a mock LLM (responses stored in fixtures)
- [ ] Security test: ensure Docker sandbox cannot access host filesystem
- [ ] Load test: simulate 10 concurrent requests with locust

## Deployment and setup

- [ ] Dockerize FastAPI app and sandbox image
- [ ] Compose services (api, db, sandbox, otel‑collector) for local dev
- [ ] Deploy to Render or Railway (managed Postgres) using Docker Compose
- [ ] Enable HTTPS via Let's Encrypt

## Prerequisites

- Python 3.10+
- Basic FastAPI knowledge
- Understanding of LangChain agents
- Familiarity with Docker security best practices
- SQL basics

## Safety and privacy

- All file processing occurs in-memory or within isolated Docker container; no external storage of raw data
- User files are encrypted at rest in Postgres (pgcrypto)
- LLM prompts are stripped of raw data; only column names and intent are sent
- Execution sandbox runs as non‑root user with seccomp profile

## Learning outcomes

- Design an LLM‑driven tool‑use agent
- Implement secure sandboxed execution of untrusted code
- Integrate vector search for semantic retrieval of past scripts
- Apply observability to async pipelines

## Stretch goals

- Add VBA macro generation for Excel Power‑Query users
- Support multi‑step workflows (chaining multiple transformations)
- Implement a retrieval‑augmented generation (RAG) that re‑uses previously successful scripts via pgvector similarity

## Resume bullet — add real results after implementation

Built a privacy‑first AI‑automation platform that converts natural‑language spreadsheet tasks into verified pandas/VBA scripts; achieved 92% automated success on a 200‑case benchmark and deployed via Docker‑Compose on Render with <200 ms latency per request

## Interview questions

- Explain how the ReAct pattern enables self‑correcting code generation.
- What security measures are required when executing untrusted Python code?
- How does pgvector improve reuse of previously generated scripts?
- Describe the trade‑offs between generating Python vs. VBA macros for end users.

## Recent research to explore

Fetched from arXiv on this run; leads for further reading, not proof of originality.

- [Posterior Matching Distillation](http://arxiv.org/abs/2611.26629v1) — updated 2026-11-19.
  - Diffusion distillation accelerates image and video generation by compressing a pretrained teacher's iterative sampling process into a few network evaluations. Distribution-based methods achieve this by matching the student's output distribution to the teacher's. This matching is often driven by reve

- [RL Post-Training in Diffusion Transformers Is Activation Steering](http://arxiv.org/abs/2611.26627v1) — updated 2026-11-19.
  - Reinforcement learning (RL) post-training substantially improves the visual quality, text rendering, and compositional accuracy of diffusion transformers. Because capabilities such as rendering requested text or composing multiple objects are inherently prompt-dependent, a natural hypothesis is that

- [PlayCraft: Designing Engaging Games from Agent Play Experience](http://arxiv.org/abs/2611.26624v1) — updated 2026-11-19.
  - Recent AI agents can generate playable games, but these games are not necessarily engaging. Mastery is a key source of engagement, yet designing for it requires extensive human play and tuning. We propose PlayCraft, an automated framework that uses a vision-based agent to play games and draws on its

- [TideCache: Efficient Hybrid LLM Serving with Transparent Cache Management and Layer-Wise Streaming](http://arxiv.org/abs/2611.26619v1) — updated 2026-11-19.
  - Hybrid architectures have become mainstream among open-weight language models. Their global-attention and bounded-state layers maintain heterogeneous caches whose demands vary with context length and concurrency. We present TideCache, a serving system on CPU--GPU superchips with three components for

- [One Prior, Two Dynamics: Repurposing Video Diffusion Transformers for Self-Supervised Latent Action Learning](http://arxiv.org/abs/2611.26617v1) — updated 2026-11-19.
  - Videos reveal how the world changes, but rarely the actions that cause those changes. Latent action learning recovers such supervision from visual transitions, yet often learns the underlying dynamics largely from scratch. We ask whether a pretrained video generator can instead provide the prior for

- [ScaleWorld: High-Resolution World Generation through Shared Prediction and Refinement](http://arxiv.org/abs/2611.26615v1) — updated 2026-11-19.
  - High-resolution generation enables video world models to render fine-grained scene structures and textures, but directly generating high-resolution video incurs substantial computational and memory costs. We present ScaleWorld, a causal video model that unifies low-resolution world prediction and hi

- [AgentRoboCritic: Understanding the Capability of Frontier Agents on Direct Robot Control](http://arxiv.org/abs/2611.26613v1) — updated 2026-11-19.
  - Frontier multimodal language agents such as GPT-6 Astra have demonstrated strong capabilities in controlling robots directly via low-level numerical actions without high-level primitives. However, existing benchmarks report only episode-level success rates, which show neither how these agents succee

- [Bio-PM-Guided Synthetic IMU Generation](http://arxiv.org/abs/2611.26607v1) — updated 2026-11-19.
  - Collecting and labeling inertial measurement unit (IMU) data for human activity recognition (HAR) is expensive, and models trained on one group of subjects often fail to generalize to unseen individuals. Even with balanced data, classifiers struggle to distinguish dynamically similar activity classe


## Hugging Face optimization

- Status: failed_keep_original
- Model: openai/gpt-oss-120b:fastest
- Note: Client error '402 Payment Required' for url 'https://router.huggingface.co/v1/chat/completions' (Request ID: Root=1-6b001f80-52cf093b31c9ee755cfdb8ae;d76e9697-f138-496f-bf89-4a3f8e82074d)
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/402

Purchase pre-paid credits to continue using Inference Providers. Alternatively, subscribe to PRO to get monthly included credits.

---
Generated with Groq / openai/gpt-oss-120b. Verify assumptions and report only measured results.

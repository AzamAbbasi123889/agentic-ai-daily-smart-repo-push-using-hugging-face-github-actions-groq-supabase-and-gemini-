# PromptGuard: Privacy‑First Prompt Injection & Leakage Auditor

> A lightweight web service that lets developers audit LLM prompts and responses for injection attacks and accidental privacy leaks. It combines contrastive prototype jailbreak detection with differential‑privacy‑aware leakage scoring, offering an API‑first experience that never stores raw user data long‑term.

**Date:** 2026-11-19 | **Category:** AI Safety, Privacy and Security | **Difficulty:** Intermediate | **Effort:** 6 days

**Build-it-yourself brief:** this factory produces the specification, not source code.

## 1. Problem statement

Developers increasingly rely on LLMs in production, yet they lack fast, privacy‑preserving tools to verify that prompts cannot be hijacked (prompt injection) and that model outputs do not unintentionally expose personal or proprietary information. Existing solutions are either heavyweight, store data centrally, or focus on only one safety aspect.

### Target users

- AI product engineers
- DevOps teams deploying LLM‑powered services
- Security auditors
- Privacy‑focused startups

## 2. Unique angle

First‑ever unified auditor that detects both prompt injection (jailbreak) and privacy leakage in a single pass, using a contrastive prototype model for zero‑shot jailbreak detection and a differential‑privacy‑inspired scoring function, all while guaranteeing that raw prompts are encrypted and purged after 24 hours.

## 3. MVP features and acceptance criteria

### Prompt Injection Scan

Runs the submitted prompt through a contrastive prototype model that flags potential jailbreak patterns

- [ ] Returns a numeric risk score 0‑100
- [ ] Risk > 70 triggers injection_flag=True
- [ ] False‑positive rate measured on the provided benchmark < 10%

### Privacy Leakage Scan

Analyzes model response for PII or proprietary tokens using regex, named‑entity detection and a leakage‑score algorithm

- [ ] Leakage score > 0.5 flags leakage_flag=True
- [ ] No raw PII is persisted beyond 24 h
- [ ] Detection precision ≥ 85% on synthetic test set

### Audit API (POST /audit)

Single endpoint that accepts {prompt, response, model_id} and returns {injection_flag, leakage_flag, scores}

- [ ] Response latency ≤ 500 ms for cold cache
- [ ] Proper HTTP 401 on missing/invalid API key
- [ ] Audit record written to PostgreSQL

### Dashboard‑Lite (optional)

Minimal HTML page showing recent audit logs and aggregate risk metrics

- [ ] Shows last 50 audits
- [ ] Aggregates average risk and leakage over time

## 4. Technology stack

- FastAPI – lightweight async API layer
- LangChain – orchestrates LLM calls and prompt templates
- Sentence‑Transformers (all‑MiniLM‑L6‑v2) – fast embedding for similarity checks
- PyTorch – host the contrastive prototype detector (from Jailbreak Detection paper)
- PostgreSQL + pgvector – stores audit metadata and vector embeddings for later analytics
- Redis – short‑term cache of recent embeddings to meet sub‑500 ms latency
- Docker & Docker‑Compose – reproducible dev/prod environment
- GitHub Actions – CI/CD with linting, unit tests and Docker image build

## 5. Architecture

FastAPI receives audit requests, forwards the prompt/response to two parallel safety pipelines (injection detector & leakage scorer). Results are merged, stored, and optionally displayed on a lightweight dashboard. All components run in Docker containers and communicate over internal network.

- **API Gateway (FastAPI)** — Validate API key, parse request, route to safety pipelines, aggregate results, store audit log
- **Injection Detector Service** — Load the contrastive prototype PyTorch model, compute embedding similarity against known jailbreak prototypes, output risk score
- **Leakage Scorer Service** — Run regex/NER checks, compute differential‑privacy‑inspired score, mask detected entities
- **Metadata Store (PostgreSQL+pgvector)** — Persist audit metadata, embeddings for later analytics
- **Cache Layer (Redis)** — Cache recent embeddings to meet latency SLA
- **Dashboard (React static build)** — Fetch aggregated metrics via /metrics endpoint

### Data flow

1. Client → FastAPI (auth) → Parallel calls to Injection Detector & Leakage Scorer → Scores merged → PostgreSQL write → Optional Redis cache update → Response to client
2. Dashboard → FastAPI /metrics → PostgreSQL query → JSON response → React render

## 6. Data model

- **audit_log:** id (UUID), user_id (UUID), timestamp (timestamptz), prompt (text), response (text), model_id (text), injection_score (float), injection_flag (bool), leakage_score (float), leakage_flag (bool), prompt_embedding (vector), response_embedding (vector)
- **user:** id (UUID), api_key (text, hashed), created_at (timestamptz), quota_daily (int), last_used (timestamptz)

## 7. API contracts

| Method | Path | Purpose |
|---|---|---|
| POST | /audit | Submit a prompt/response pair for safety auditing and receive risk scores |
| GET | /audit/{audit_id} | Retrieve a single audit record (admin only) |
| GET | /metrics | Return aggregate statistics (average risk, daily volume) for dashboard |

## 8. Build milestones

### 1 — Foundations & Core Pipelines

- [ ] Set up FastAPI skeleton with API‑key middleware
- [ ] Implement PostgreSQL schema + pgvector extension
- [ ] Containerize services with Docker‑Compose
- [ ] Integrate contrastive prototype detector (load pretrained weights)
- [ ] Build leakage scorer using spaCy + regex

**Deliverable:** Running /audit endpoint with both risk scores stored in DB


## 9. Evaluation plan

Targets to test, not claimed results.

- **Injection detection recall:** Run 200 synthetic jailbreak prompts from the Jailbreak Detection paper and compute true positive rate Target: ≥ 85%
- **Leakage detection precision:** Create 150 synthetic responses containing PII; compute precision of flagged leaks Target: ≥ 90%
- **API latency (p95):** Locust load test with 100 concurrent users for 5 min Target: ≤ 500 ms

## Testing checklist

- [ ] Unit tests for injection detector wrapper (pytest)
- [ ] Unit tests for leakage scorer functions
- [ ] Integration tests for /audit endpoint (requests)
- [ ] Security tests: verify API‑key enforcement and SQL injection resistance
- [ ] Load test with Locust to validate latency SLA

## Deployment and setup

- [ ] Build multi‑stage Docker images (builder + runtime)
- [ ] Push to GitHub Container Registry via GitHub Actions on each merge
- [ ] Deploy to Railway (free tier) using docker‑compose.yml
- [ ] Configure automated health checks and rolling restarts

## Prerequisites

- Python 3.10+
- Basic knowledge of FastAPI and async programming
- Familiarity with LLM prompting and prompt injection concepts
- Understanding of embeddings and vector similarity
- Intro to differential privacy concepts

## Safety and privacy

- All raw prompts and responses are encrypted at rest (PostgreSQL pgcrypto)
- Data retention policy: delete audit records older than 30 days (cron job)
- API keys are hashed with Argon2; rate‑limit per user to prevent abuse
- No third‑party telemetry; optional self‑hosted OpenTelemetry for internal metrics

## Learning outcomes

- Design and implement a privacy‑first microservice architecture
- Integrate a contrastive prototype model for zero‑shot jailbreak detection
- Apply differential‑privacy‑inspired scoring to text leakage detection
- Store and query vector embeddings with pgvector
- Secure API design with API‑key auth and data retention policies

## Stretch goals

- Support streaming audit for real‑time chat applications
- Add multi‑LLM support (OpenAI, Anthropic, Groq) with model‑specific risk baselines
- Interactive React dashboard with heatmaps of high‑risk tokens
- Fine‑tune the prototype detector on user‑submitted jailbreak examples

## Resume bullet — add real results after implementation

Built PromptGuard, a privacy‑first LLM prompt‑injection and leakage auditor; achieved ≥ 85% recall on jailbreak detection and ≤ 500 ms latency while enforcing GDPR‑compatible data retention

## Interview questions

- How does contrastive prototype learning differ from a traditional binary classifier for jailbreak detection?
- Explain how differential privacy concepts inspired your leakage scoring algorithm and how you enforce data minimization.
- What trade‑offs did you consider when choosing pgvector vs. a dedicated vector DB like Milvus?
- Describe how you would extend the system to detect hallucinations in model outputs.

## Recent research to explore

Fetched from arXiv on this run; leads for further reading, not proof of originality.

- [UltraTex: Aligning Physical Knowledge for High-Fidelity PBR Texture Generation](http://arxiv.org/abs/2611.24941v1) — updated 2026-11-18.
  - Generating physically based rendering (PBR) texture maps for a 3D mesh from a single reference image is highly ambiguous, as the observed appearance entangles material identity, surface reflectance, and illumination. While current generative methods produce realistic albedo maps, they still struggle

- [$Z$-sight: Unifying Vision-Language-Action and Latent World Modeling](http://arxiv.org/abs/2611.24940v1) — updated 2026-11-18.
  - We introduce $Z$-sight, a unified robot foundation model that couples vision-language-action (VLA) and generative latent world modeling. Video-based world action models (WAMs) show the value of joint future-and-action generation for control, yet inherit the heavy cost of video generators. Recent lat

- [Jailbreak Detection on Large Language Models via Contrastive Prototype Structures](http://arxiv.org/abs/2611.24936v1) — updated 2026-11-18.
  - Jailbreak attempts and harmful prompts remain a challenge for the safe deployment of large language models. We study whether contrastively learned representations can support safety detection without training an additional downstream classifier. We propose Jailbreak Detection with Prototype Inferenc

- [Knowing What You Know: A Trait Theory of Reviewer Value in Human-AI Cognitive Systems](http://arxiv.org/abs/2611.24932v1) — updated 2026-11-18.
  - When a capable model and a human reviewer cooperate on the same decision, which human still adds value? We argue this is a question about a single cognitive trait, metacognitive calibration: the alignment between a reviewer's behavioral confidence and the actual correctness of their judgments. We de

- [Mapping the AI Supply Chain: Dependencies, Vulnerabilities, and Market Concentration in the AI Ecosystem](http://arxiv.org/abs/2611.24927v1) — updated 2026-11-18.
  - AI systems are built across many organizations that contribute models, data, compute, capital, talent, and other assets. While the layers of the AI stack are relatively well understood, the relationships between actors and components across layers remains sparsely documented. In this work, we focus 

- [Agentic Harness Engineering Beta: Requirement-Centered Evolution of Agent Harnesses](http://arxiv.org/abs/2611.24924v1) — updated 2026-11-18.
  - Real-world harness engineering is driven by explicit and implicit user requirements, which guide development and validation. However, existing harness evolution methods often overlook implicit requirements and interaction needs, while using a single evolution agent to modify the harness and benchmar

- [Unified Law for Visual Tasks (The Four Laws of Computer Vision)](http://arxiv.org/abs/2611.24917v1) — updated 2026-11-18.
  - In this paper, we propose a Unified Law for Visual Tasks, which could be further divided into Four Laws of Computer Vision, with the goal of enabling a single framework or method to uniformly train on and perform nearly all visual tasks. Our starting point is an inspiration and hypothesis: if the wo

- [PrismRestore: A Compact Restoration Toolbox for Agentic Image Restoration](http://arxiv.org/abs/2611.24915v1) — updated 2026-11-18.
  - Agentic image restoration composes operations to handle mixed degradations, yet its toolbox often requires storing multiple restoration networks. We propose PrismRestore, which constructs a compact bank of callable restoration actions from a single frozen all-in-one model. Our approach builds on tas


## Hugging Face optimization

- Status: failed_keep_original
- Model: openai/gpt-oss-120b:fastest
- Note: Client error '402 Payment Required' for url 'https://router.huggingface.co/v1/chat/completions' (Request ID: Root=1-6afed27e-59b33579399df1075a9abf95;4e131e38-c2f5-471e-863a-ba42916de521)
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/402

Purchase pre-paid credits to continue using Inference Providers. Alternatively, subscribe to PRO to get monthly included credits.

## Gemini design review

- Novelty score: 4/10
- Feasibility score: 8/10

### Overlap risks

- Meta's official open-source model 'Llama Guard' and its predecessor 'Prompt Guard' (which directly overlaps in name and purpose).
- Existing guardrail frameworks such as NeMo Guardrails, Guardrails AI, and Lakera Gandalf API.
- Open-source PII detection suites like Microsoft Presidio.
### Suggested improvements

- Rename the project to avoid a direct trademark clash with Meta's existing 'Prompt Guard' model.
- Ground the 'differential-privacy-inspired leakage scoring' mechanism with a precise mathematical specification (e.g., membership inference risk scoring or re-identification probability via k-anonymity) rather than standard spaCy NER/regex heuristics.
- Clarify data retention discrepancies: the summary and unique angle claim raw data is purged after 24 hours, but the data safety section and schema state audit logs with raw text are stored for 30 days.

---
Generated with Groq / openai/gpt-oss-120b. Verify assumptions and report only measured results.

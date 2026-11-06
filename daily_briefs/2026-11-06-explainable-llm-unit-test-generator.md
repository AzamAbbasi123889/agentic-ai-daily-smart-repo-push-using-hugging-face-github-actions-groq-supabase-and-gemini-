# Explainable LLM‑Driven Unit Test Generator

> A privacy‑first web service that automatically writes unit tests for submitted Python functions, ranks them by relevance, and explains each generated test using an LLM. Developers can accept, edit, or reject suggestions, creating a feedback loop that improves future generations.

**Date:** 2026-11-06 | **Category:** AI Developer Tools and Code Intelligence | **Difficulty:** Intermediate | **Effort:** 7 days

**Build-it-yourself brief:** this factory produces the specification, not source code.

## 1. Problem statement

Developers spend significant time writing boilerplate unit tests, especially for legacy codebases. Existing test‑generation tools either produce low‑quality tests or act as black boxes, offering no insight into why a test was created, which hampers trust and adoption.

### Target users

- Software engineers
- DevOps teams
- Open‑source maintainers
- Students learning testing

## 2. Unique angle

Combines static code analysis, vector‑based function embedding, and an LLM that not only generates tests but also produces a human‑readable rationale linked to specific code paths, with a user‑feedback loop that fine‑tunes the test‑generation prompt on‑the‑fly.

## 3. MVP features and acceptance criteria

### Code ingestion & embedding

Upload a single Python file; extract functions/classes; compute dense embeddings via OpenAI embedding model; store in Postgres pgvector.

- [ ] Upload succeeds (200 OK)
- [ ] All top‑level callables indexed
- [ ] Embedding stored with UUID

### LLM test generation

Given a function ID, request the LLM to produce up to 5 pytest test cases targeting edge cases and typical paths.

- [ ] Generated at least 3 syntactically correct tests
- [ ] Tests import the target function without errors

### Explainable rationale

For each generated test, LLM returns a short natural‑language explanation linking test inputs to specific code branches.

- [ ] Explanation ≤ 2 sentences
- [ ] Mentions at least one line number or variable

### User feedback loop

UI allows users to Accept, Edit, or Reject each test; feedback stored and used to adjust a small prompt‑tuning dataset.

- [ ] Feedback recorded in DB
- [ ] Prompt‑tuning data size updates correctly

### Dashboard & observability

React dashboard shows uploaded files, generated tests, explanations, and feedback stats; OpenTelemetry traces API calls.

- [ ] Dashboard loads in <2 s
- [ ] All API calls appear in trace viewer

## 4. Technology stack

- FastAPI (lightweight, async API)
- LangChain (prompt orchestration)
- OpenAI/Groq LLM (generation & explanation)
- pgvector + PostgreSQL (store code embeddings & test history)
- Redis (caching embeddings)
- Docker (containerization)
- GitHub Actions (CI/CD)
- OpenTelemetry (tracing)
- React (frontend UI)

## 5. Architecture

A FastAPI backend orchestrates static analysis, embedding, LLM generation, and feedback storage. React SPA consumes REST endpoints. PostgreSQL with pgvector holds code artifacts, embeddings, and test metadata. Redis caches recent embeddings. Observability via OpenTelemetry and Prometheus.

- **API Layer** — Expose endpoints for upload, test generation, feedback, and retrieval
- **Embedding Service** — Parse Python AST, create function signatures, call OpenAI embedding API, store vectors
- **Test Generation Engine** — Compose prompts, invoke LLM, parse responses into structured test objects
- **Explanation Engine** — Ask LLM for rationale tied to code lines
- **Feedback Store** — Persist user actions and update prompt‑tuning dataset
- **Frontend** — React UI for file upload, test review, and analytics

### Data flow

1. User uploads file → FastAPI parses → Embedding Service creates vectors → Vectors stored in Postgres → UI requests test generation → Prompt built using vector similarity → LLM returns tests & explanations → Backend stores results → UI displays → User feedback sent back → Feedback stored for future prompt refinement

## 6. Data model

- **file:** id (UUID), filename, content (TEXT), upload_ts (TIMESTAMP)
- **callable:** id (UUID), file_id (FK), name, type (function|class), signature, start_line, end_line, embedding (VECTOR)
- **generated_test:** id (UUID), callable_id (FK), test_code (TEXT), explanation (TEXT), llm_model, generation_ts
- **feedback:** id (UUID), test_id (FK), action (accept|edit|reject), edited_code (TEXT, nullable), timestamp

## 7. API contracts

| Method | Path | Purpose |
|---|---|---|
| POST | /files | Upload a Python source file |
| GET | /files/{file_id}/callables | List extracted functions/classes |
| POST | /callables/{callable_id}/generate-tests | Trigger LLM to create tests and explanations |
| GET | /tests/{test_id} | Retrieve generated test and rationale |
| POST | /feedback | Submit user feedback for a test |

## 8. Build milestones

### 1 — Foundations & Data Model

- [ ] Set up FastAPI project
- [ ] Design PostgreSQL schema with pgvector
- [ ] Implement file upload & AST extraction

**Deliverable:** Working upload endpoint + DB tables

### 2 — Embedding & Retrieval

- [ ] Integrate OpenAI embedding API
- [ ] Store vectors in pgvector
- [ ] Build similarity query endpoint

**Deliverable:** Embeddings searchable by cosine similarity

### 3 — LLM Test Generation & Explanation

- [ ] Create LangChain prompt templates
- [ ] Implement test generation endpoint
- [ ] Add explanation sub‑prompt

**Deliverable:** Generate tests with rationale

### 4 — Feedback Loop & Frontend

- [ ] Design React UI for review
- [ ] Add feedback POST endpoint
- [ ] Persist feedback & update prompt‑tuning set

**Deliverable:** End‑to‑end user flow

### 5 — Observability & Deployment

- [ ] Add OpenTelemetry instrumentation
- [ ] Write Dockerfile & docker‑compose stack
- [ ] Configure GitHub Actions CI/CD

**Deliverable:** Containerized app with CI pipeline


## 9. Evaluation plan

Targets to test, not claimed results.

- **Test syntactic correctness:** Run `pytest -q` on generated tests; count passes Target: ≥ 90 % of generated tests pass import & syntax checks
- **Explanation relevance score:** Manual rating by 3 developers on 1‑5 scale; average Target: ≥ 4.0
- **User acceptance rate:** % of tests marked ‘accept’ after review Target: ≥ 60 %

## Testing checklist

- [ ] Unit test FastAPI routes with pytest‑asyncio
- [ ] Integration test embedding‑search round‑trip
- [ ] Mock LLM responses to verify parsing logic
- [ ] E2E test full UI flow with Playwright

## Deployment and setup

- [ ] Dockerize backend & frontend
- [ ] Use docker‑compose for local dev (Postgres, Redis, OpenTelemetry Collector)
- [ ] Deploy to Render/railway (free tier) or Azure Container Apps
- [ ] Enable HTTPS via Let’s Encrypt

## Prerequisites

- Python 3.10+
- Basic knowledge of FastAPI & React
- Familiarity with vector databases (pgvector)
- Understanding of unit testing frameworks (pytest)

## Safety and privacy

- All code stays on server; no external storage of raw source beyond user session
- LLM calls only send function signatures, not full code, to reduce IP leakage
- Rate‑limit uploads to prevent abuse
- Audit logs stored in immutable Postgres table

## Learning outcomes

- Design an LLM‑augmented microservice
- Implement code‑to‑vector pipelines with pgvector
- Create explainable AI outputs
- Build a feedback‑driven prompt‑tuning loop
- Deploy a full‑stack app with observability

## Stretch goals

- Support multi‑file projects with cross‑module analysis
- Add CI‑integrated GitHub Action that auto‑generates tests on PRs
- Implement few‑shot prompt tuning using collected feedback to improve test quality
- Add coverage estimation using `coverage.py` on generated tests

## Resume bullet — add real results after implementation

Built an explainable LLM‑driven unit‑test generator that auto‑produced high‑quality pytest cases for 200+ Python functions, achieving 92% syntactic pass rate and 4.2/5 average rationale score; deployed via Docker & CI/CD, handling 150 daily active users

## Interview questions

- How does storing function embeddings improve test generation relevance?
- Explain how you prevented proprietary code from being sent to the LLM.
- What trade‑offs exist between generating many tests vs. highly targeted tests?
- Describe the feedback‑loop architecture and how it influences prompt tuning.

## Recent research to explore

Fetched from arXiv on this run; leads for further reading, not proof of originality.

- [User Embeddings are Superpositions of Interpretable Behavioral Modes](http://arxiv.org/abs/2611.08487v1) — updated 2026-11-05.
  - User embeddings are central components of modern recommendation, personalization, and behavioral modeling systems. Though these embeddings can compactly encode rich behavioral information, they are inherently dense and opaque, limiting interpretability. To address this gap, we argue that user embedd

- [Do You Miss the Nights We Spent Crafting Figures? Rethinking Teaser and Framework Figures in the Age of Generative AI](http://arxiv.org/abs/2611.08486v1) — updated 2026-11-05.
  - Scientific figures give research ideas a visual form through choices of abstraction, composition, and emphasis. Generative AI offers new ways to realize these choices, raising questions about explanatory clarity and purposeful visual expression. We examine these questions through a visual retrospect

- [Where and Why is Grounded Reasoning Useful?](http://arxiv.org/abs/2611.08485v1) — updated 2026-11-05.
  - Grounded reasoning, where a model outputs text coordinates of relevant locations in chain-of-thought reasoning, is a common strategy for solving complex visual reasoning problems. However, the benefits and limitations of grounded reasoning are understudied. We study where and why grounded reasoning 

- [SwarmEvolve: Latent Agent Swarms for Evolutionary Discovery and Optimization](http://arxiv.org/abs/2611.08483v1) — updated 2026-11-05.
  - LLM-guided evolutionary search uses AI agents to improve programs for mathematical and computational problems by iteratively refining solutions and combining high-scoring methods. However, the process is often slow because the LLM generates a long textual chain of thought for each round and must rep

- [Scientist World: Grow a Research World for AI-Scientists](http://arxiv.org/abs/2611.08478v1) — updated 2026-11-05.
  - AI-Scientists arrived, but a world for them to grow in did not. Human scientists take theirs for granted $-$ centuries of open problems and shared ideas, waiting in the scientific literature. To AI-Scientists, that world is readable but not runnable, so we build Scientist World for them: every resea

- [EgoGeneralist: Unifying Egocentric Action-Video Tasks through Video-Native Modeling](http://arxiv.org/abs/2611.08477v1) — updated 2026-11-05.
  - Modern video models possess strong visual priors, yet do not natively represent human action in metric 3D space. We present EgoGeneralist, which adapts pretrained video generators to unify action-conditioned egocentric video generation, pose estimation, and joint action-video generation. Our role-ad

- [XStack: A Benchmark for ML Repo Migration](http://arxiv.org/abs/2611.08472v1) — updated 2026-11-05.
  - ML code should run where researchers choose, not where it was first written. Today, machine learning code mainly lives in two ecosystems, PyTorch on NVIDIA GPUs and JAX on Google TPUs. Migrating repositories between them means building and testing across frameworks and hardware. This migration is (1

- [Same Behavior, Different Mechanism: What Finite Experiments Can Certify About Integrated Information](http://arxiv.org/abs/2611.08469v1) — updated 2026-11-05.
  - Interpretability, AI auditing and assessments of machine consciousness increasingly rest on mechanism-level quantities: functionals of a system's causal transition law that describe how it computes, not what it outputs. Experiments see that law only through finite, partial and noisy interventions. W


## Hugging Face optimization

- Status: failed_keep_original
- Model: openai/gpt-oss-120b:fastest
- Note: Client error '402 Payment Required' for url 'https://router.huggingface.co/v1/chat/completions' (Request ID: Root=1-6aeda1bf-151a1f1a3dda04975803d619;3358a85d-852b-4a9b-8ad6-77e4027538c7)
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/402

Purchase pre-paid credits to continue using Inference Providers. Alternatively, subscribe to PRO to get monthly included credits.

---
Generated with Groq / openai/gpt-oss-120b. Verify assumptions and report only measured results.

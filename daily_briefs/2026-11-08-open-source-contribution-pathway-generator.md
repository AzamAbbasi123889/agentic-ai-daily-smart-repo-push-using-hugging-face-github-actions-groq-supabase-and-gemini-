# Open-Source Contribution Pathway Generator

> An agentic web service that ingests a student’s skill profile, builds a personal knowledge graph, matches it against open‑source repositories, and produces a step‑by‑step contribution roadmap with ready‑to‑use issue and PR templates.

**Date:** 2026-11-08 | **Category:** LangChain / LangGraph / CrewAI | **Difficulty:** Intermediate | **Effort:** 7 days

**Build-it-yourself brief:** this factory produces the specification, not source code.

## 1. Problem statement

Students and junior developers struggle to translate academic knowledge into real‑world open‑source contributions because they cannot discover suitable projects, understand contribution prerequisites, or generate the first pull‑request artefacts. A guided, automated pathway lowers the entry barrier and accelerates skill‑to‑impact conversion.

### Target users

- B.Tech AI/ML students
- Junior developers seeking open‑source experience
- University coding clubs

## 2. Unique angle

Combines a dynamic skill‑graph (LangGraph) with a multi‑agent crew (CrewAI) that queries the GitHub ecosystem, ranks projects by relevance, and auto‑generates issue‑selection and PR‑template artefacts, all while persisting session state for progressive learning.

## 3. MVP features and acceptance criteria

### Skill Profile Ingestion

User uploads a résumé or manually selects skills; system extracts/normalizes them into a vectorised skill node graph.

- [ ] User can upload a .txt/.pdf or fill a form
- [ ] Extracted skills appear as distinct nodes in the graph
- [ ] Each skill node has an embedding stored in pgvector

### Open‑Source Project Matching

Agent searches GitHub topics, filters by language/complexity, scores relevance against the skill graph.

- [ ] Top‑5 projects returned within 5 seconds
- [ ] Each project includes repo name, stars, primary language, and relevance score

### Roadmap Generation

CrewAI orchestrates agents to select an entry issue, draft a contribution guide, and produce a PR template tailored to the user’s skill gaps.

- [ ] Generated markdown includes: selected issue link, step‑by‑step actions, code snippet placeholders, and checklist
- [ ] Roadmap is persisted and retrievable via a unique ID

### Session Persistence

LangGraph stores the evolving skill graph and roadmap so users can resume later.

- [ ] User can close the browser and retrieve the same roadmap after 24 h
- [ ] State updates (e.g., after completing a step) reflect in the graph

## 4. Technology stack

- Python – core language for rapid prototyping
- FastAPI – lightweight async API layer
- LangChain – LLM prompting & retrieval utilities
- LangGraph – persistent graph state for user skill graph
- CrewAI – orchestrates skill‑analysis, repo‑search, and roadmap agents
- OpenAI/Claude API – LLM backbone
- PyGitHub – safe GitHub API client
- Supabase/Postgres with pgvector – stores user data and vector embeddings
- Redis – short‑term cache for token limits
- Docker – reproducible dev/runtime environment
- GitHub Actions – CI/CD pipeline
- React (optional) – minimal UI for demo

## 5. Architecture

A FastAPI backend hosts LangChain/LangGraph agents orchestrated by CrewAI. User data and embeddings live in Supabase/Postgres; Redis caches recent GitHub API responses. Optional React frontend consumes the REST API.

- **API Layer (FastAPI)** — Expose endpoints, handle auth, trigger crew runs
- **Agent Orchestrator (CrewAI)** — Coordinate skill‑extraction, repo‑search, and roadmap agents
- **State Graph (LangGraph)** — Persist user skill nodes, project nodes, and roadmap progress
- **Vector Store (pgvector)** — Store skill embeddings for similarity search
- **GitHub Integration (PyGitHub)** — Search repos, fetch issues, validate tokens
- **Cache (Redis)** — Throttle GitHub rate limits and speed up repeated queries
- **Frontend (React – optional)** — Collect user input, display roadmaps

### Data flow

1. User submits skills → FastAPI → Skill‑Extraction Agent → embeddings stored in pgvector → LangGraph updates skill nodes
2. Roadmap request → CrewAI triggers Repo‑Search Agent (queries GitHub) → scores → Roadmap Agent composes markdown → LangGraph persists roadmap → API returns result

## 6. Data model

- **users:** id (uuid), email, hashed_password, created_at
- **skills:** id, user_id, name, embedding (vector), created_at
- **projects:** id, github_full_name, description, primary_language, stars, relevance_score, vector_repr
- **roadmaps:** id, user_id, project_id, markdown_content, status (draft|in_progress|completed), created_at, updated_at
- **sessions:** id, user_id, graph_snapshot (jsonb), last_accessed

## 7. API contracts

| Method | Path | Purpose |
|---|---|---|
| POST | /auth/register | Create user account |
| POST | /auth/login | Issue JWT access token |
| POST | /profile/skills | Upload résumé or skill list; triggers skill graph creation |
| GET | /recommendations | Return top‑N matching open‑source projects |
| POST | /roadmap/generate | Launch CrewAI to build contribution roadmap |
| GET | /roadmap/{roadmap_id} | Retrieve persisted roadmap markdown |
| PATCH | /roadmap/{roadmap_id}/status | Update roadmap progress |

## 8. Build milestones

### 1 — Foundations & Data Layer

- [ ] Initialize repo, Docker, CI
- [ ] Design Postgres schema + pgvector
- [ ] Implement JWT auth

**Deliverable:** Running FastAPI skeleton with DB migrations

### 1 — Skill Extraction Agent

- [ ] Create LangChain prompt chain
- [ ] Integrate OpenAI embedding model
- [ ] Store skill nodes

**Deliverable:** /profile/skills endpoint returns graph summary

### 2 — Repo Matching & Roadmap Crew

- [ ] Build GitHub search agent
- [ ] Define relevance scoring logic
- [ ] Implement Roadmap agent (markdown generation)
- [ ] Wire CrewAI orchestrator

**Deliverable:** /recommendations and /roadmap/generate functional

### 2 — State Persistence & UI Demo

- [ ] Persist roadmaps in LangGraph
- [ ] Add Redis caching
- [ ] Create minimal React page to view roadmap

**Deliverable:** End‑to‑end demo with persistent sessions

### 3 — Testing, Security, Deployment

- [ ] Write unit & integration tests
- [ ] Run OWASP‑ASVS checklist for token handling
- [ ] Docker‑Compose production stack, GitHub Actions CI/CD

**Deliverable:** Deployable Docker image on Railway/Render


## 9. Evaluation plan

Targets to test, not claimed results.

- **Relevance@5:** Manually label top‑5 returned projects for 20 test users; compute proportion of truly suitable repos Target: ≥0.7
- **Roadmap Completion Time:** Time from generation to user marking roadmap as completed (simulated in test suite) Target: ≤30 min
- **API Latency:** Average response time for /recommendations under load (10 concurrent users) Target: ≤2 s
- **User Satisfaction (Survey):** Post‑demo Likert score (1‑5) on usefulness Target: ≥4

## Testing checklist

- [ ] Pytest unit tests for each FastAPI route (status codes, schema validation)
- [ ] Mocked GitHub responses to verify Repo‑Search scoring logic
- [ ] LangGraph state rollback tests (add/remove skill nodes)
- [ ] CrewAI orchestration integration test with deterministic LLM responses (using OpenAI’s test mode)
- [ ] Security test: ensure JWT token is not logged and GitHub PAT is stored only in env
- [ ] Load test with locust for /recommendations endpoint

## Deployment and setup

- [ ] Dockerfile builds slim python:3.11‑slim image; multi‑stage for dependencies
- [ ] docker‑compose.yml defines services: api, postgres, redis, supabase‑studio (optional)
- [ ] GitHub Actions workflow: lint → unit tests → build image → push to Docker Hub → Deploy to Railway (free tier) on push to main
- [ ] Environment variables: OPENAI_API_KEY, GITHUB_PAT, JWT_SECRET, DATABASE_URL
- [ ] Enable HTTPS via Railway/Render automatic TLS

## Prerequisites

- Python 3.10+
- Familiarity with FastAPI or Flask
- Basic understanding of LLM prompting
- GitHub personal access token basics
- Intro to graph databases (Neo4j optional)
- Docker basics

## Safety and privacy

- Store only hashed passwords (bcrypt) and minimal profile data
- GitHub personal access tokens never persisted; used only for runtime API calls and cleared after request
- All user‑generated embeddings are encrypted at rest via Postgres pgcrypto extension
- Rate‑limit GitHub queries; fall back to cached results
- Comply with GDPR: provide endpoint DELETE /users/{id} to purge all personal data

## Learning outcomes

- Design and implement multi‑agent LLM workflows
- Persist and query mutable graph state with LangGraph
- Coordinate agents using CrewAI’s crew pattern
- Integrate vector similarity search with pgvector
- Securely handle external API credentials

## Stretch goals

- Add multilingual skill extraction using HuggingFace multilingual models
- Integrate Issue‑label auto‑selection based on user’s preferred contribution type (docs, code, tests)
- Real‑time mentorship chat agent that answers follow‑up questions using the persisted LangGraph state
- Deploy to a serverless platform (AWS Lambda + API Gateway) with DynamoDB vector store

## Resume bullet — add real results after implementation

Designed and delivered a multi‑agent LLM platform (LangChain, LangGraph, CrewAI) that auto‑generates personalized open‑source contribution roadmaps, achieving 75% relevance@5 and sub‑2‑second API latency for 10‑concurrent‑user loads.

## Interview questions

- Explain how LangGraph differs from a traditional relational database for storing mutable graph state.
- Describe the role of CrewAI in orchestrating multiple LangChain agents. How do you handle failures between agents?
- What strategies did you use to keep GitHub API usage within rate limits?
- How would you extend the system to support real‑time feedback loops after a user submits a PR?
- Discuss security considerations when handling third‑party API tokens in a multi‑tenant SaaS.

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
- Note: Client error '402 Payment Required' for url 'https://router.huggingface.co/v1/chat/completions' (Request ID: Root=1-6af03fe3-4f3950bd09db0fa81cf36a94;c106a483-465f-4c47-aa84-bfc2076e1165)
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/402

Purchase pre-paid credits to continue using Inference Providers. Alternatively, subscribe to PRO to get monthly included credits.

## Gemini design review

- Novelty score: 6/10
- Feasibility score: 8/10

### Overlap risks

- GoodFirstIssue.dev and Up-For-Grabs already provide filtered beginner-friendly GitHub discovery.
- Standard LLM resume parsers and job matchers use identical architecture patterns (Resume -> Embedding -> pgvector -> LLM recommendations).
### Suggested improvements

- Choose either LangGraph or CrewAI instead of nesting both; mixing both for workflow and agent orchestration adds unnecessary cognitive overhead and debugging complexity for a 7-day project.
- Integrate GitHub issue-level analysis (e.g., checking if 'good first issue' tickets are stale or already have open PRs) rather than stopping at repo-level matching.
- Auto-fork the target repo and initialize a customized local branch setup script via git CLI integration to make the roadmap immediately actionable.

---
Generated with Groq / openai/gpt-oss-120b. Verify assumptions and report only measured results.

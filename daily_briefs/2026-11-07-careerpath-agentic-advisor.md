# CareerPath Agentic Advisor

> An agentic web service that ingests a user's education, experience, and interests, pulls real‑time public job market data, and produces a personalized, step‑by‑step career roadmap with skill‑gap analysis and resource recommendations using LangChain, LangGraph and CrewAI.

**Date:** 2026-11-07 | **Category:** Agentic AI Systems | **Difficulty:** Intermediate | **Effort:** 5 days

**Build-it-yourself brief:** this factory produces the specification, not source code.

## 1. Problem statement

Students and professionals often cannot map their current skills and aspirations onto concrete, market‑aligned career trajectories, leading to inefficient up‑skilling and missed job opportunities.

### Target users

- College graduates
- Career switchers
- Professional development coaches

## 2. Unique angle

Leverages user‑behavior embedding decomposition to surface interpretable skill‑mode vectors and orchestrates specialized agents (skill extractor, market analyzer, roadmap planner) via LangGraph, delivering a transparent, privacy‑first roadmap that updates automatically with market trends.

## 3. MVP features and acceptance criteria

### Profile Ingestion

User uploads a JSON or fills a form with education, experience, interests, and self‑rated skill levels.

- [ ] API returns 200 with stored user_id
- [ ] Data persisted in Postgres with a generated embedding vector
- [ ] Validation errors returned for missing fields

### Market Retrieval & Embedding

System pulls the latest 500 public job postings from a free dataset (e.g., Kaggle's remote‑jobs) and stores vector embeddings for similarity search.

- [ ] Job posting pipeline runs nightly via GitHub Actions
- [ ] >95% of postings have non‑null embedding vectors
- [ ] Embeddings indexed in pgvector and searchable

### Roadmap Generation

Orchestrated agents produce a 12‑month skill‑gap analysis, prioritized learning modules, and milestone dates, returned as structured JSON.

- [ ] Response includes at least 5 roadmap steps
- [ ] Each step lists skill, resource URL, and estimated weeks
- [ ] Overall confidence score >0.7 for the generated plan

## 4. Technology stack

- FastAPI – lightweight, async API layer
- LangChain – prompt engineering, retrieval augmentation
- LangGraph – state‑graph orchestration of multi‑agent workflow
- CrewAI – task decomposition and collaborative agent execution
- OpenAI/Groq LLMs – inference (free tier for MVP)
- Postgres + pgvector – store user profiles, job embeddings, similarity search
- Redis – short‑term cache for API responses
- Docker – reproducible container environment
- GitHub Actions – CI/CD pipeline with linting and testing
- React – minimal SPA to visualize roadmap (optional)

## 5. Architecture

A FastAPI gateway receives user data, stores it, then triggers a LangGraph workflow that coordinates three specialized agents. Each agent uses LangChain for LLM calls and accesses the vector store. Results are aggregated and persisted as a Roadmap entity, which the frontend visualizes.

- **Frontend SPA** — Collects user input, displays roadmap, and polls status
- **API Gateway (FastAPI)** — Validate requests, CRUD on Postgres, trigger orchestrator
- **Orchestrator (LangGraph)** — Manage state machine, invoke agents, handle retries
- **Skill Extraction Agent (CrewAI)** — Parse profile, generate skill embedding
- **Market Analysis Agent** — Retrieve job postings, compute market skill demand vectors
- **Roadmap Planner Agent** — Compare user vs market embeddings, generate timeline
- **Vector Store (Postgres + pgvector)** — Store embeddings for similarity search
- **Cache (Redis)** — Speed up repeated similarity queries

### Data flow

1. User submits profile → API stores profile & enqueues LangGraph workflow
2. Skill Extraction Agent creates user embedding → stored in vector DB
3. Market Analysis Agent refreshes job embeddings → stored in vector DB
4. Roadmap Planner Agent queries nearest market skills, computes gaps, builds JSON roadmap → saved in Postgres
5. Frontend fetches roadmap via GET endpoint

## 6. Data model

- **UserProfile:** user_id (uuid), name, education, experience (list), interests (list), skill_vector (vector), created_at
- **JobPosting:** job_id (uuid), title, company, description, required_skills (list), embedding (vector), posted_at
- **RoadmapStep:** step_id (uuid), user_id (fk), skill, resource_url, estimated_weeks, order_index, confidence

## 7. API contracts

| Method | Path | Purpose |
|---|---|---|
| POST | /api/v1/profile | Create or update a user profile |
| GET | /api/v1/roadmap/{user_id} | Retrieve the generated career roadmap for a given user |
| POST | /api/v1/refresh-market | Manually trigger job posting ingestion and embedding refresh |

## 8. Build milestones

### 1 — Foundations & Data Pipeline

- [ ] Set up FastAPI skeleton
- [ ] Create Postgres schema with pgvector
- [ ] Implement job‑posting ingestion script (Kaggle dataset)
- [ ] Write unit tests for data layer

**Deliverable:** Running API with persistent storage and nightly data refresh


## 9. Evaluation plan

Targets to test, not claimed results.

- **Skill‑Gap Coverage:** Percentage of high‑demand market skills present in the generated roadmap Target: ≥80%
- **Roadmap Completion Estimate Accuracy:** Compare estimated weeks vs actual weeks taken by a pilot group (self‑reported) Target: Mean absolute error ≤2 weeks
- **User Satisfaction Score:** 5‑point Likert survey after demo Target: ≥4.0

## Testing checklist

- [ ] Unit test each FastAPI endpoint with pytest and httpx
- [ ] Integration test LangGraph state transitions using mock LLM responses
- [ ] Contract test vector similarity queries (FAISS‑like behavior)
- [ ] Load test GET /roadmap with 100 concurrent users (locust)

## Deployment and setup

- [ ] Containerize API, Redis, Postgres using Docker Compose
- [ ] Deploy to Railway or Render free tier for MVP
- [ ] Configure GitHub Actions to build, test, and push Docker images
- [ ] Enable HTTPS via automatic Let’s Encrypt

## Prerequisites

- Python 3.10+
- Fundamentals of FastAPI
- Basic LangChain usage
- Understanding of graph‑based workflows (LangGraph)
- Intro to vector databases (pgvector)

## Safety and privacy

- All user data stored encrypted at rest (Postgres TLS)
- No external data sent beyond LLM inference (use local OpenAI/Groq endpoints)
- Retention policy: delete profiles after 90 days of inactivity
- Provide explicit consent UI before storing profile

## Learning outcomes

- Design and implement a multi‑agent system with LangGraph
- Apply CrewAI for coordinated task execution
- Create and query dense embeddings in Postgres/pgvector
- Build a privacy‑first API with FastAPI
- Containerize and CI‑CD a full‑stack AI product

## Stretch goals

- Add real‑time scraping of remote job boards via RSS (with rate‑limit handling)
- Integrate a recommendation engine (e.g., Coursera, Udemy) using their public APIs
- Expose a LangGraph dashboard to visualize agent state transitions
- Allow multi‑language profiles and translate roadmap steps via a translation LLM

## Resume bullet — add real results after implementation

Designed and shipped a privacy‑first multi‑agent career‑roadmap SaaS (LangChain, LangGraph, CrewAI) that generated personalized 12‑month up‑skilling plans for 200+ users, achieving 85% skill‑gap coverage and 4.2/5 user satisfaction

## Interview questions

- Explain how LangGraph manages state across multiple agents and why it’s preferable to a simple sequential chain.
- What are the trade‑offs of using pgvector in Postgres vs a dedicated vector DB like Pinecone for this project?
- How would you mitigate hallucinations in the Roadmap Planner Agent when suggesting learning resources?
- Describe how you would implement a zero‑trust data pipeline for the job‑posting ingestion step.

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
- Note: Client error '402 Payment Required' for url 'https://router.huggingface.co/v1/chat/completions' (Request ID: Root=1-6aeeeada-7f9901dd1065796052986f9b;84594b21-a613-4fba-82d8-4caf1f54e325)
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/402

Purchase pre-paid credits to continue using Inference Providers. Alternatively, subscribe to PRO to get monthly included credits.

---
Generated with Groq / openai/gpt-oss-120b. Verify assumptions and report only measured results.

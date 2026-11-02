# Personal Finance Goal Agentic Advisor

> A privacy‑first web service that ingests a user's transaction feed, builds a graph of financial behaviors, and orchestrates multiple LLM agents to generate personalized budgeting advice, savings plans, and goal‑driven forecasts.

**Date:** 2026-11-02 | **Category:** Agentic AI and Multi-Agent Systems | **Difficulty:** Intermediate | **Effort:** 7 days

**Build-it-yourself brief:** this factory produces the specification, not source code.

## 1. Problem statement

Individuals lack a transparent, autonomous assistant that can continuously analyze their spending, anticipate future cash‑flow, and recommend actionable financial goals while keeping sensitive banking data local.

### Target users

- College students managing limited budgets
- Young professionals planning savings
- Financial‑literacy educators

## 2. Unique angle

Combines a hierarchical world‑model agent that simulates future financial states with a graph‑based expense ontology, enabling long‑horizon goal planning rather than single‑shot budgeting suggestions.

## 3. MVP features and acceptance criteria

### Transaction Ingestion & Normalization

Upload CSV/JSON bank statements; system parses, categorizes via LLM and stores in Postgres + Neo4j.

- [ ] User can upload a file and see 95%+ of transactions stored
- [ ] Categories auto‑assigned with confidence >0.8
- [ ] No raw data leaves the local Docker container

### Goal‑Driven Planner Agent

User defines a financial goal (e.g., “save $5k for a laptop in 6 months”). Agent simulates cash‑flow, suggests monthly budgets and alerts.

- [ ] Planner returns a month‑by‑month budget plan
- [ ] Projected savings meet goal within ±5% tolerance
- [ ] Plan updates when new transactions are ingested

### Budget Review Agent

Periodically (daily) generates a concise summary of overspend, savings opportunities, and actionable tips.

- [ ] Summary delivered via API endpoint within 2 seconds
- [ ] Contains at least three concrete suggestions
- [ ] Uses only data stored locally

## 4. Technology stack

- FastAPI (lightweight API layer)
- LangGraph (orchestrates multi‑agent workflow)
- OpenAI GPT‑4o-mini via Azure OpenAI (LLM core)
- pgvector in PostgreSQL (semantic search of transaction descriptions)
- Neo4j (expense category graph & relationship reasoning)
- Redis (task queue & short‑term cache)
- Docker (containerization)
- GitHub Actions (CI/CD)

## 5. Architecture

A FastAPI front‑end receives user data, stores it in Postgres (raw & vectorized) and Neo4j (category graph). LangGraph orchestrates three specialized agents—Ingestion, Planner, Reviewer—communicating via Redis task queues. All components run in Docker compose for easy local deployment.

- **API Layer** — Expose endpoints for file upload, goal creation, and budget reports
- **Data Store** — Postgres with pgvector for semantic search; Neo4j for hierarchical category graph
- **Agent Orchestrator** — LangGraph workflow managing state, retries, and agent chaining
- **Redis Queue** — Async task dispatch and result caching
- **LLM Service** — Calls Azure OpenAI for reasoning and natural‑language generation

### Data flow

1. User uploads statement → API stores raw rows → Ingestion Agent categorizes & updates Neo4j → Vector embeddings stored in pgvector → User creates goal → Planner Agent reads graph & embeddings, simulates future cash‑flow → Planner writes plan to DB → Reviewer Agent runs nightly, reads new transactions, generates summary → API serves report

## 6. Data model

- **Transaction:** id (UUID), date, amount (float), merchant, category_id (FK), description, embedding (vector)
- **Category:** id (UUID), name, parent_id (FK), keywords (list)
- **FinancialGoal:** id (UUID), user_id, target_amount, target_date, created_at, plan (JSON)
- **BudgetPlan:** goal_id (FK), month (YYYY‑MM), budgeted_amount, projected_savings, adjustments (JSON)

## 7. API contracts

| Method | Path | Purpose |
|---|---|---|
| POST | /upload-transactions | Accept CSV/JSON bank statements and trigger ingestion |
| POST | /goals | Create a new financial goal |
| GET | /goals/{goal_id}/plan | Retrieve the generated month‑by‑month budget plan |
| GET | /reports/summary | Get latest budget review summary |

## 8. Build milestones

### 1 — Foundations & Data Pipeline

- [ ] Set up FastAPI skeleton
- [ ] Configure Postgres + pgvector
- [ ] Create Neo4j schema
- [ ] Implement CSV upload & basic parsing

**Deliverable:** Working API that stores raw transactions

### 2 — Ingestion & Categorization Agent

- [ ] Build LangGraph node for categorization
- [ ] Prompt design for LLM‑based category assignment
- [ ] Persist results to Neo4j

**Deliverable:** Transactions auto‑tagged with >90% accuracy on test data

### 3 — Goal Planner Agent

- [ ] Design financial simulation model
- [ ] Implement planner LangGraph node
- [ ] Expose goal creation endpoint

**Deliverable:** Dynamic budget plan generated for user‑defined goals

### 4 — Review Agent & UI Mock

- [ ] Schedule nightly reviewer via Redis
- [ ] Generate natural‑language summary
- [ ] Create minimal React dashboard (optional)

**Deliverable:** End‑to‑end MVP demo


## 9. Evaluation plan

Targets to test, not claimed results.

- **Category Assignment Accuracy:** Compare LLM categories against a manually labeled validation set of 200 transactions Target: ≥90%
- **Goal Achievement Forecast Error:** Absolute difference between projected savings and actual savings after 30 days in a simulated dataset Target: ≤5%

## Testing checklist

- [ ] Unit tests for each FastAPI route (pytest)
- [ ] Integration tests for LangGraph workflow using mock LLM responses
- [ ] Load test ingestion of 10k transactions (Locust)
- [ ] Security test: ensure no outbound network calls for raw data

## Deployment and setup

- [ ] Dockerfile for API & worker services
- [ ] docker‑compose.yml with Postgres, Neo4j, Redis, and worker containers
- [ ] GitHub Actions workflow: lint → test → build image → push to Docker Hub → deploy to Render (free tier)

## Prerequisites

- Python 3.10+
- Basic knowledge of FastAPI and REST
- Familiarity with LLM prompting and LangChain/LangGraph
- Understanding of relational & graph databases

## Safety and privacy

- All raw financial data processed inside user‑controlled Docker container; no third‑party logging
- LLM calls only send anonymized transaction embeddings and goal metadata
- Environment variables protect Azure OpenAI keys
- Provide data‑deletion endpoint to purge user records

## Learning outcomes

- Design and deploy a multi‑agent LLM system
- Integrate vector stores and graph databases for hybrid retrieval
- Implement privacy‑first data handling for financial data
- Build CI/CD pipelines for AI services

## Stretch goals

- Integrate Plaid sandbox for live banking feed
- Add a Reinforcement Learning based optimizer that iteratively improves budgeting policy
- Support multi‑currency & exchange‑rate forecasting

## Resume bullet — add real results after implementation

Built an end‑to‑end multi‑agent financial advisor (FastAPI + LangGraph) that auto‑categorizes 10k+ transactions, generates goal‑driven budget plans with <5% forecast error, and deploys via Docker on Render (CI/CD with GitHub Actions).

## Interview questions

- How does LangGraph enable stateful coordination between the Ingestion, Planner, and Reviewer agents?
- Why combine pgvector and Neo4j instead of using a single datastore?
- Explain the privacy considerations when sending financial data to an LLM and how your design mitigates them.
- What trade‑offs did you consider when choosing a simulation‑based planner over a simple rule‑based budget calculator?

## Recent research to explore

Fetched from arXiv on this run; leads for further reading, not proof of originality.

- [GazeRIB: Systematic Evaluation of Multi-Reader Gaze-Guided Chest X-ray Learning](http://arxiv.org/abs/2610.42152v1) — updated 2026-10-30.
  - Radiologists' visual attention can supervise medical image learning, but how reader panel composition affects its value remains untested. We evaluated GazeRIB (Gaze-guided Radiologist-Informed Blackout), which masks unviewed regions during training and uses unmasked images at inference. Eight expert

- [Latent Reasoning in Continuous Space for Unified Multimodal Models](http://arxiv.org/abs/2610.42149v1) — updated 2026-10-30.
  - Unified Multimodal Models (UMMs) achieve remarkable success on diverse multimodal understanding and generation tasks, yet they still struggle to effectively leverage language-based chain-of-thought reasoning for image generation. As a result, existing reasoning-augmented UMMs often fail to inherit t

- [Flide: Accelerating Decision Inference with Exact State Forking](http://arxiv.org/abs/2610.42148v1) — updated 2026-10-30.
  - Decision models such as Jev have emerged as a highly promising paradigm for LLM agent systems, providing lightweight and reliable categorical reasoning for rapid System One execution. However, existing generation-oriented inference engines fail to support these workloads effectively, suffering from 

- [Latent Sparse Attention: Towards Subquadratic Ultra-Long Context Attention](http://arxiv.org/abs/2610.42147v1) — updated 2026-10-30.
  - Agentic workflows are increasingly shifting towards long-horizon tasks, such as open-ended scientific work, where models benefit from long context windows. However, at ultra-long context (above 1M tokens), full attention is prohibitively expensive. A promising approach is sparse attention, in which 

- [Hierarchical World Models with Implicit Dynamics](http://arxiv.org/abs/2610.42146v1) — updated 2026-10-30.
  - Planning with world models enables test-time adaptation for embodied agents, offering superior generalization over direct policy learning. However, long-horizon tasks remain hindered by cumulative errors and search complexity. Existing hierarchical methods often use rigid macro-actions or latent ski

- [SemEllipsoid: Semantic-aware Shape Abstraction with Ellipsoid](http://arxiv.org/abs/2610.42145v1) — updated 2026-10-30.
  - Representing 3D shapes using a set of primitives - known as shape abstraction - is an actively studied problem in computer graphics with wide applications in shape understanding, analysis, and simulation due to the compactness and computational efficiency of the primitive-based representation. Prior

- [RoboArchitect: Automating the Design of Robotic Agents with Persistent Memory](http://arxiv.org/abs/2610.42141v1) — updated 2026-10-30.
  - Recent work shows that a frozen robot policy performs far better inside an agent harness, where control code decides when to query the policy, consult vision tools, or command the arm directly. Yet today these harnesses are built by hand and redesigned for each new robot or benchmark. We show that h

- [Counting on Dummies: Privacy Amplification with Observable Counts and Truncated Batches](http://arxiv.org/abs/2610.42139v1) — updated 2026-10-30.
  - In many practical deployments of Differentially Private Stochastic Gradient Descent (DP-SGD), the server processes data in batches. Randomly sampling these batches allows for better privacy bounds via privacy amplification results. Most sampling schemes with provable privacy amplification, including


## Hugging Face optimization

- Status: failed_keep_original
- Model: openai/gpt-oss-120b:fastest
- Note: Client error '402 Payment Required' for url 'https://router.huggingface.co/v1/chat/completions' (Request ID: Root=1-6ae85d7a-6b785ec41beef30c478b3a9c;aeab9314-d6b1-4783-b509-f9c99d7ddefa)
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/402

You have no remaining credits. Purchase pre-paid credits to continue using Inference Providers. Alternatively, subscribe to PRO to get monthly included credits.

---
Generated with Groq / openai/gpt-oss-120b. Verify assumptions and report only measured results.

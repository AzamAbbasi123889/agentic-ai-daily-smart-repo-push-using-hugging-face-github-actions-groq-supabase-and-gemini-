# AI Debate Coach and Argumentation Simulator

> A multi‑agent web service that ingests a debate topic, generates balanced pro and con arguments with citations, and lets users practice a turn‑based debate while receiving AI‑driven critique.

**Date:** 2026-11-11 | **Category:** LangChain, LangGraph, CrewAI | **Difficulty:** Intermediate | **Effort:** 7 days

**Build-it-yourself brief:** this factory produces the specification, not source code.

## 1. Problem statement

Students, speakers and content creators often lack structured, evidence‑backed arguments and a safe environment to rehearse debates. Existing tools provide static outlines or single‑agent generators but do not simulate a dynamic, role‑playing debate with iterative feedback.

### Target users

- Students preparing for debate competitions
- Public speakers and trainers
- Content creators needing balanced viewpoints
- Educators designing critical‑thinking exercises

## 2. Unique angle

Combines LangGraph‑driven iterative refinement, CrewAI role orchestration, and LangChain citation retrieval to produce two opposing, source‑backed argument trees and an interactive turn‑based debate that offers real‑time critique and improvement suggestions.

## 3. MVP features and acceptance criteria

### Topic Ingestion & Citation Retrieval

User submits a debate topic; system extracts key claims and retrieves supporting documents using LangChain and pgvector.

- [ ] POST /sessions returns a session_id
- [ ] At least 3 relevant citations per side are stored
- [ ] Response latency <2 seconds

### Pro/Con Argument Generation

Two agents generate balanced arguments, each argument linked to retrieved citations.

- [ ] Each side has ≥5 distinct argument nodes
- [ ] Every argument includes a non‑empty citations list
- [ ] Arguments are stored and retrievable via GET /sessions/{id}/arguments

### Interactive Debate & Critique

Turn‑based chat where user alternates speaking as Pro/Con; after each turn a Critic agent provides feedback and suggests improvements.

- [ ] Chat UI shows alternating turns
- [ ] Critique is generated within 2 seconds
- [ ] User can request a summary of strengths/weaknesses

## 4. Technology stack

- FastAPI (lightweight async API)
- LangChain (retrieval‑augmented generation for citations)
- LangGraph (state‑machine workflow for multi‑turn refinement)
- CrewAI (role‑based agents: Researcher, ArgumentBuilder, Critic)
- OpenAI/Groq LLMs (LLM backend)
- PostgreSQL + pgvector (persist sessions & vector‑search citations)
- Redis (caching retrieval results)
- Docker (containerization)
- GitHub Actions (CI/CD)
- React (minimal UI for chat‑style debate)

## 5. Architecture

FastAPI serves as the HTTP front‑end. A LangGraph workflow orchestrates CrewAI agents that retrieve evidence, build arguments, and critique user turns. Persistent storage is PostgreSQL with pgvector for citation embeddings; Redis caches retrieval results. React SPA provides a chat‑style UI.

- **API Layer** — Expose REST endpoints, handle authentication, session management
- **Orchestrator (LangGraph)** — Manage state transitions: ingest → retrieve → build arguments → debate loop → critique
- **Agents (CrewAI)** — ResearchAgent (search & embed), ArgumentAgent (generate structured arguments), CriticAgent (evaluate user input)
- **Knowledge Store** — Postgres tables for users, sessions, arguments, citations; pgvector index for semantic search
- **Cache** — Redis stores recent retrieval results to meet latency SLA
- **Frontend** — React chat interface communicating with FastAPI

### Data flow

1. User POST /sessions → Orchestrator creates session record
2. Orchestrator triggers ResearchAgent → LangChain fetches docs → embeddings stored in pgvector
3. ArgumentAgent consumes citations → generates argument trees → saved in DB
4. Frontend polls GET /sessions/{id}/arguments → displays Pro/Con lists
5. During debate, each user message POST /sessions/{id}/turn → CriticAgent evaluates → response sent back

## 6. Data model

- **User:** id (UUID), email (string), created_at (timestamp)
- **DebateSession:** id (UUID), user_id (FK), topic (string), created_at, status (enum)
- **Citation:** id (UUID), session_id (FK), source_url (string), title (string), embedding (vector)
- **Argument:** id (UUID), session_id (FK), side (enum: pro/con), content (text), citation_ids (array of UUID)
- **Turn:** id (UUID), session_id (FK), speaker (enum: user/pro_agent/critique), content (text), timestamp

## 7. API contracts

| Method | Path | Purpose |
|---|---|---|
| POST | /sessions | Create a new debate session with a topic |
| GET | /sessions/{session_id} | Retrieve session metadata and current status |
| POST | /sessions/{session_id}/start | Trigger the LangGraph workflow to generate arguments |
| GET | /sessions/{session_id}/arguments | Fetch generated Pro and Con arguments with citations |
| POST | /sessions/{session_id}/turn | Submit a user utterance for the current debate turn |
| GET | /sessions/{session_id}/turns | Stream or list all turns and AI critiques |

## 8. Build milestones

### 1 — Foundations & Core API

- [ ] Set up repo, Docker, CI
- [ ] Define PostgreSQL schema + pgvector index
- [ ] Implement FastAPI endpoints for session CRUD

**Deliverable:** Running API with session creation and persistence

### 2 — Retrieval & Argument Generation

- [ ] Integrate LangChain with public web search (SerpAPI mock)
- [ ] Build ResearchAgent to store embeddings
- [ ] Create ArgumentAgent using CrewAI to produce structured arguments

**Deliverable:** POST /sessions/{id}/start returns populated argument trees

### 3 — Debate Loop & Critique

- [ ] Design LangGraph state machine for turn‑based flow
- [ ] Implement CriticAgent (feedback generation)
- [ ] Connect Redis cache for low latency

**Deliverable:** Interactive debate endpoint functional with AI critique

### 4 — Frontend, Testing & Deployment

- [ ] Develop React chat UI
- [ ] Write unit & integration tests (pytest, httpx)
- [ ] Configure GitHub Actions for Docker image push
- [ ] Deploy to Railway/Render with PostgreSQL add‑on

**Deliverable:** End‑to‑end deployed MVP accessible via web


## 9. Evaluation plan

Targets to test, not claimed results.

- **Argument relevance:** Human rating on 5‑point Likert scale for 10 sampled arguments Target: ≥4.0 average
- **Citation coverage:** % of argument sentences linked to at least one citation Target: ≥90%
- **Debate coherence latency:** Average response time per turn measured in load test Target: <2 seconds
- **Cost per session:** Sum of LLM token usage multiplied by provider rates Target: <$0.10

## Testing checklist

- [ ] Unit tests for each FastAPI route (pytest)
- [ ] Mocked LangChain retrieval tests to verify citation count
- [ ] LangGraph workflow unit tests with simulated states
- [ ] Integration test: full session lifecycle from creation to critique
- [ ] Load test 20 concurrent sessions using locust to verify latency

## Deployment and setup

- [ ] Dockerfile builds multi‑stage image (Python runtime)
- [ ] docker‑compose.yml defines api, postgres, redis services
- [ ] GitHub Actions workflow builds image, runs tests, pushes to Docker Hub
- [ ] Deploy on Railway (free tier) linking managed Postgres and Redis

## Prerequisites

- Python 3.10+
- Basic FastAPI knowledge
- Familiarity with LangChain concepts
- Understanding of graph‑based workflows (LangGraph)
- Intro to CrewAI agent patterns

## Safety and privacy

- No personally identifiable data stored beyond optional email (hashed)
- All user‑generated text is stored only for session duration and deleted after 30 days
- LLM calls use OpenAI safety settings (content filter)
- Rate‑limit API to 10 requests/sec per IP
- Provide clear terms of service and opt‑out endpoint

## Learning outcomes

- Design and implement a graph‑based LLM workflow
- Integrate retrieval‑augmented generation for citation grounding
- Orchestrate multiple specialized agents with CrewAI
- Persist and query vector‑embeddings in Postgres
- Deploy a full‑stack async service with CI/CD

## Stretch goals

- Voice interface via Web Speech API for spoken debate
- Real‑time fact‑checking using external APIs (Wolfram Alpha)
- Personalization: adapt argument style based on user’s prior performance
- Export debate transcript with citations as PDF

## Resume bullet — add real results after implementation

Built an AI‑driven multi‑agent debate coach (LangChain + LangGraph + CrewAI) that auto‑generates balanced, citation‑backed arguments and provides turn‑based critique; achieved <2 s latency and <$0.10 cost per session, deployed on Railway with CI/CD

## Interview questions

- Explain how LangGraph helped you manage the stateful debate flow compared to a simple sequential script.
- What trade‑offs did you consider when choosing pgvector over a dedicated vector DB like Pinecone?
- How does CrewAI enable role specialization, and how did you prevent agents from colluding or repeating content?
- Describe your strategy for ensuring citation relevance and preventing hallucinated sources.
- How would you scale the system to support 1,000 concurrent debates?

## Recent research to explore

Fetched from arXiv on this run; leads for further reading, not proof of originality.

- [Medical Image Segmentation: Foundation Model Adaptation versus Task-Specific Training](http://arxiv.org/abs/2611.14519v1) — updated 2026-11-10.
  - Foundation models pretrained on large natural-image collections are increasingly adapted for medical image segmentation, in the expectation that they will replace models trained for each task. Most comparisons, however, use data from the training distribution and a single task-specific baseline whos

- [Toward Foundation Detection Models via Example-Based Grounding in EM-DETR](http://arxiv.org/abs/2611.14518v1) — updated 2026-11-10.
  - DeepLearning (DL)-based Computer-Aided Diagnostic (CAD) systems have shown great promise in supporting clinicians, but their performance heavily depends on the availability of large, well-annotated datasets. In medical lesion detection, the scarcity of comprehensive, stan dardized annotations and th

- [TorchCurves: Differentiable Parametric Curves](http://arxiv.org/abs/2611.14516v1) — updated 2026-11-10.
  - We present TorchCurves, a PyTorch library that treats vector-valued parametric curves as learnable primitives. Its central operation maps batches of scalar inputs to points on curves represented in B-spline or Legendre polynomial bases, with differentiation through both inputs and coefficients. Curv

- [AutoScaffold: AI-Guided Scaffolding for Reinforcement Learning of Language Models](http://arxiv.org/abs/2611.14515v1) — updated 2026-11-10.
  - Reinforcement learning with verifiable rewards (RLVR) produces rich training experience, yet outcome rewards reduce each attempt to a single number and leave most of this information unused. Training-time scaffolds, such as strategies or hints added to the prompt during training, offer a natural way

- [Contrastive Discovery: Open-Ended Scientific Discovery over Competing Explanations](http://arxiv.org/abs/2611.14514v1) — updated 2026-11-10.
  - LLM agents are increasingly used for open-ended, data-driven scientific discovery, yet most of them evaluate hypotheses pointwise, testing an empirical claim $h$ only against its complement $\neg h$. When evidence rejects $h$, the agent learns that one explanation is unlikely but not which alternati

- [Pyrite: Building and Benchmarking Protein-Ligand Pose Ranking Agents](http://arxiv.org/abs/2611.14511v1) — updated 2026-11-10.
  - Predicting how a ligand binds to its target is central to small-molecule drug discovery. Modern cofolding models can generate diverse candidate poses, but reliably ranking these candidates remains challenging. We introduce Pyrite, a pairwise pose-ranking benchmark comprising 1,500 pose pairs across 

- [When Does the Real Wiring Win? Testing connectome structure-function claims against unmeasured physiology](http://arxiv.org/abs/2611.14508v1) — updated 2026-11-10.
  - Connectome-constrained models are often used to argue that a measured wiring diagram outperforms shuffled or rewired wiring, and hence that structure shapes function. Such comparisons can confound wiring with how the models are tuned: a connectome fixes who connects to whom, not the excitability, ga

- [Continual-ARC: Measuring Skill Acquisition over a Working Lifetime](http://arxiv.org/abs/2611.14505v1) — updated 2026-11-10.
  - Agent harnesses have emerged as a promising mechanism for continual learning, alongside test-time parametric learning. However, the current benchmarks have several limitations: they generally focus on a single applied domain, serve each instance only once, and assume a single family of learner, so m


## Hugging Face optimization

- Status: failed_keep_original
- Model: openai/gpt-oss-120b:fastest
- Note: Client error '402 Payment Required' for url 'https://router.huggingface.co/v1/chat/completions' (Request ID: Root=1-6af439c5-79e17b54517c97ae5a7b42e7;05916287-66e6-4fca-b8f8-61dca637c9be)
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/402

Purchase pre-paid credits to continue using Inference Providers. Alternatively, subscribe to PRO to get monthly included credits.

## Gemini design review

- Novelty score: 5/10
- Feasibility score: 7/10

### Overlap risks

- Common LLM tutorial concept (debate simulator / Pro-Con generator)
- Significant architectural overlap between LangGraph and CrewAI (often redundant to use both simultaneously for state orchestration)
- Standard RAG implementations using SerpAPI/Tavily and pgvector
### Suggested improvements

- Streamline the agent framework: choose either LangGraph or CrewAI rather than combining both, as mixing their execution runtimes introduces unnecessary complexity and debugging overhead.
- Adjust unrealistic latency acceptance criteria: achieving <2s end-to-end response time for multi-agent RAG + citation retrieval + evaluation with OpenAI LLMs is unrealistic without aggressive streaming or faster models like Groq/Llama-3.
- Incorporate structured competitive debate scoring rubrics (e.g., Parliamentary, Policy, or Lincoln-Douglas formats) with specific metrics like rebuttals, logical fallacies, and impact calculus to stand out from generic chatbot debaters.

---
Generated with Groq / openai/gpt-oss-120b. Verify assumptions and report only measured results.

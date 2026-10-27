# DecisionRAG‑Powered Enterprise Policy Navigator

> A privacy‑first FastAPI service that ingests corporate policy PDFs, builds a Neo4j knowledge graph of clauses, and uses Retrieval‑Free DecisionRAG to answer employee queries without a separate vector store.

**Date:** 2026-10-27 | **Category:** Advanced RAG and GraphRAG | **Difficulty:** Advanced | **Effort:** 7 days

**Build-it-yourself brief:** this factory produces the specification, not source code.

## 1. Problem statement

Enterprises struggle to retrieve relevant policy information quickly; traditional RAG relies on static vector indexes that become stale and consume storage, while graph‑based policy navigation lacks LLM‑driven decision making.

### Target users

- HR & compliance teams
- Legal analysts
- Enterprise employees seeking policy guidance

## 2. Unique angle

Combines the newest Retrieval‑Free DecisionRAG paradigm with a dynamic Neo4j policy graph, enabling on‑the‑fly clause selection without pre‑computed embeddings and providing traceable reasoning paths for each answer.

## 3. MVP features and acceptance criteria

### Policy Ingestion

Upload a PDF, extract sections, create nodes and relationships in Neo4j, store optional fallback embeddings.

- [ ] User can POST a PDF and receive a 202 response
- [ ] All top‑level sections appear as nodes in Neo4j with correct parent links
- [ ] Fallback embeddings are stored in pgvector if extraction fails

### DecisionRAG Query Engine

User asks a natural‑language policy question; LLM decides next node to explore, traverses graph, and returns answer with citation path.

- [ ] GET /query returns answer within 2 seconds
- [ ] Answer includes a list of traversed node IDs and clause excerpts
- [ ] No vector store lookup is performed for 80% of test queries

### Explanation Endpoint

Expose the reasoning trace (node sequence, LLM prompts, scores) for auditability.

- [ ] GET /explain/{query_id} returns JSON with ordered node IDs, prompt/response pairs, and confidence scores
- [ ] Trace can be visualized in Neo4j Bloom

## 4. Technology stack

- FastAPI – lightweight async API layer
- LangChain + LangGraph – orchestrate DecisionRAG reasoning and graph traversal
- Neo4j – native graph storage for policy hierarchy
- pgvector (Postgres) – fallback dense store for ambiguous queries
- pypdf / pdfminer – PDF ingestion
- Docker – reproducible containerization
- GitHub Actions – CI/CD pipeline
- OpenTelemetry – request tracing
- DVC – version control for policy document snapshots

## 5. Architecture

FastAPI receives documents/queries, LangChain agents invoke DecisionRAG logic to dynamically pick graph nodes, Neo4j stores the policy graph, pgvector holds optional embeddings, OpenTelemetry streams traces to a local Jaeger UI.

- **API Layer** — HTTP request validation, authentication, response formatting
- **Ingestion Service** — PDF parsing, node/relationship creation, optional embedding generation
- **DecisionRAG Engine** — LLM prompt generation, node‑selection policy, confidence scoring
- **Graph Store (Neo4j)** — Persist policy hierarchy and enable fast traversals
- **Fallback Vector Store (Postgres + pgvector)** — Similarity search when LLM confidence is low
- **Observability Stack (OpenTelemetry + Jaeger)** — Collect spans for each reasoning step

### Data flow

1. User POST /ingest → Ingestion Service → Neo4j (nodes/edges) + pgvector (embeddings)
2. User GET /query → API → DecisionRAG Engine → Neo4j traversal loop → Answer assembled → Response
3. User GET /explain → API fetches stored trace → Returns JSON

## 6. Data model

- **Document:** id (UUID), title, upload_timestamp, source_uri
- **PolicyNode:** id (UUID), type (section|clause|definition), title, text, order_index
- **Relation:** source_id, target_id, type (parent|references)
- **Embedding:** node_id, vector (float[] ), model_name
- **QueryLog:** id, user_id, question, answer, trace_id, timestamp

## 7. API contracts

| Method | Path | Purpose |
|---|---|---|
| POST | /ingest | Upload PDF policy document and create graph nodes |
| GET | /query | Ask a natural‑language question about policies |
| GET | /explain/{query_id} | Retrieve LLM reasoning trace for a given query |

## 8. Build milestones

### 1 — MVP Delivery

- [ ] Set up repo, CI, Docker base image
- [ ] Implement PDF ingestion → Neo4j nodes
- [ ] Build DecisionRAG loop with LangGraph
- [ ] Expose /query and /explain endpoints
- [ ] Write unit & integration tests

**Deliverable:** Working FastAPI service deployed locally with end‑to‑end policy Q&A


## 9. Evaluation plan

Targets to test, not claimed results.

- **Answer Exact Match:** Compare answer text against curated gold answers for 20 benchmark questions Target: ≥85% exact match
- **Latency:** Average response time for /query over 100 random queries Target: ≤2 seconds
- **DecisionRAG Retrieval Ratio:** % of queries where no fallback vector lookup occurs Target: ≥80%
- **Trace Completeness:** Each answer must include ≥3 node IDs and confidence scores Target: 100%

## Testing checklist

- [ ] Unit tests for PDF parser and Neo4j CRUD operations
- [ ] Integration tests for end‑to‑end query flow using a small synthetic policy corpus
- [ ] Load test 50 concurrent /query requests with Locust
- [ ] Security test: ensure uploaded PDFs are scanned for malware and stored encrypted

## Deployment and setup

- [ ] Dockerize the FastAPI app and Neo4j (docker‑compose)
- [ ] Deploy to Render.com (free tier) or Railway with Postgres addon
- [ ] Configure HTTPS via Let’s Encrypt
- [ ] Set environment variables for LLM API keys (OpenAI/Groq)
- [ ] Enable OpenTelemetry exporter to Jaeger UI

## Prerequisites

- Python 3.10+
- Basic Neo4j knowledge
- Familiarity with LLM prompting (OpenAI or Groq)
- Understanding of RAG pipelines

## Safety and privacy

- All uploaded PDFs are encrypted at rest in Neo4j using built‑in encryption
- No data is sent to third‑party storage; only LLM calls (prompt & selected node text) are transmitted
- Rate‑limit /query per user to prevent abuse
- GDPR‑compliant delete endpoint for user‑uploaded documents

## Learning outcomes

- Design a Retrieval‑Free RAG workflow
- Model hierarchical policy documents as a graph
- Integrate LangGraph for multi‑step LLM orchestration
- Implement traceable reasoning with OpenTelemetry

## Stretch goals

- Add OCR support for scanned policy PDFs using Tesseract
- Implement RL‑based node‑selection fine‑tuning on user feedback
- Multi‑modal policy search (embed images of signage)
- Deploy as a SaaS with tenant isolation using Supabase for auth

## Resume bullet — add real results after implementation

Built a DecisionRAG‑powered GraphRAG policy navigator that reduced average query latency to 1.6 s and achieved 88% exact‑match accuracy on a 200‑question corporate policy benchmark; engineered end‑to‑end CI/CD, Docker deployment, and OpenTelemetry tracing for auditability.

## Interview questions

- Explain how DecisionRAG differs from classic vector‑based retrieval and why it suits a policy graph.
- Describe how you would model hierarchical policies in Neo4j and query them efficiently.
- What challenges arise when mixing LLM‑driven node selection with deterministic graph traversals?
- How does OpenTelemetry help you debug multi‑step LLM reasoning?
- If a user uploads a confidential policy document, what steps ensure privacy and compliance?

## Recent research to explore

Fetched from arXiv on this run; leads for further reading, not proof of originality.

- [Retriever-Free Retrieval: Navigating Documents with Decision Models](http://arxiv.org/abs/2610.35868v1) — updated 2026-10-26.
  - While language models have become dramatically more capable, retrieval still largely relies on lexical matching or similarity in fixed embedding spaces. This creates a capability asymmetry: what the retriever fails to find, even the strongest generator cannot recover. We propose DecisionRAG, which b

- [Center-of-Mass Interpretation of Evolution Strategies](http://arxiv.org/abs/2610.35865v1) — updated 2026-10-26.
  - Evolution strategies (ES) update a model by sampling a population of perturbed copies, scoring each one, and moving in the reward-weighted direction of the perturbations. This update is usually presented as an estimate of a smoothed gradient. We present a geometrical interpretation of this update in

- [Auto-Research Arena: Benchmarking and Advancing Auto-Research in Language Modeling](http://arxiv.org/abs/2610.35866v1) — updated 2026-10-26.
  - As autonomous research systems become more capable, benchmarks must both evaluate their performance and support meaningful research progress. We introduce Auto-Research Arena, a multi-target benchmark for evaluating autonomous research systems and discovering ideas in language modeling. Arena suppor

- [VibeVideoBench:Evaluating Multimodal Agents on Code-Driven Video Generation](http://arxiv.org/abs/2610.35864v1) — updated 2026-10-26.
  - Diffusion video models produce striking clips, but they cannot reliably render an exact formula, a correct chart, a ruleconsistent game or narration synchronized to on-screen events. A different route is emerging: multimodal agents that write code to render every frame and synthesize every sound. We

- [Learning Force-Reactive Humanoid Loco-Manipulation](http://arxiv.org/abs/2610.35862v1) — updated 2026-10-26.
  - Many everyday tasks require controlling contact force as well as motion. On a humanoid, this force must often be coordinated across both hands and the whole body, and cannot be specified by kinematic trajectories alone. Therefore, we present FLORE, a framework for learning force-reactive humanoid lo

- [Do vision models know that three is three?](http://arxiv.org/abs/2610.35857v1) — updated 2026-10-26.
  - Do vision models encode the transition $2{\to}3$ the same way whether it appears in handwritten digits or in hand gestures, and do they "understand" that clean${\to}$dirty is the same transformation regardless of whether it is applied to a kitchen or a carpet? The linear representation hypothesis (L

- [On the stability of learning](http://arxiv.org/abs/2610.35856v1) — updated 2026-10-26.
  - Learning algorithms are usually analyzed under the assumption that informative gradients are continuously available. But this is not always true---learning signals in biological neural networks, for example, may be sparse, local, and only intermittently available at any given synapse. In this work, 

- [FL4N: Feed-forward Latent Model for 4D Novel View Synthesis](http://arxiv.org/abs/2610.35854v1) — updated 2026-10-26.
  - 4D novel view synthesis (NVS) aims to render dynamic scenes across viewpoints and timestamps, which requires jointly inferring 3D structure and temporal dynamics. Existing monocular feed-forward methods often rely on explicit 4D Gaussian representations, which are prone to temporal inconsistency and


## Hugging Face optimization

- Status: failed_keep_original
- Model: openai/gpt-oss-120b:fastest
- Note: Client error '402 Payment Required' for url 'https://router.huggingface.co/v1/chat/completions' (Request ID: Root=1-6ae05e89-2bb01e255d5074397433d21a;f26e2d9e-bf8b-4637-896d-e2c5f5f86a11)
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/402

You have no remaining credits. Purchase pre-paid credits to continue using Inference Providers. Alternatively, subscribe to PRO to get monthly included credits.

## Gemini design review

- Novelty score: 6/10
- Feasibility score: 6/10

### Overlap risks

- High overlap with ubiquitous 'GraphRAG with Neo4j and LangChain' boilerplate projects and corporate policy QA bots.
- The concept of 'Retrieval-Free DecisionRAG' closely mirrors standard agentic tree/graph traversal (e.g., Tree-of-Thought, hierarchical policy routing) under branded terminology.
### Suggested improvements

- Reconcile the architectural contradiction between pitching a 'Retrieval-Free / no vector store' paradigm and simultaneously configuring pgvector and an Embedding entity in the core stack.
- Recalibrate the <=2s latency SLA or specify high-throughput fast-inference tooling (e.g., Groq Llama 3 8B with function calling), as multi-step agentic graph traversals typically incur multiple seconds of round-trip latency.
- Standardize input documents initially on structured Markdown or HTML rather than arbitrary PDFs to avoid spending the majority of the 7-day budget debugging parsing and clause-boundary chunking heuristics.
- Formally define the DecisionRAG heuristic (e.g., greedy hierarchical descent via Table-of-Contents nodes vs. beam search) instead of relying on an ambiguous LLM prompt loop.

---
Generated with Groq / openai/gpt-oss-120b. Verify assumptions and report only measured results.

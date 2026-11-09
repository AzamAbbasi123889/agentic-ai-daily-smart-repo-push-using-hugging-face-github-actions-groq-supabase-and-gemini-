# LegalClauseGraphRAG: Contract Clause Comparison Copilot

> An interactive web service that ingests multiple contracts, builds a clause‑level knowledge graph, and uses hybrid dense‑vector + graph retrieval to answer comparative legal questions with provenance at clause granularity.

**Date:** 2026-11-09 | **Category:** Advanced RAG and GraphRAG | **Difficulty:** Advanced | **Effort:** 7 days

**Build-it-yourself brief:** this factory produces the specification, not source code.

## 1. Problem statement

Legal teams spend hours manually locating, comparing, and reasoning about specific clauses across dozens of contracts. Existing document‑search tools return flat snippets without relationship context, leading to missed obligations and inconsistent risk assessments.

### Target users

- In‑house counsel
- Legal operations analysts
- Compliance officers
- Law firm associates

## 2. Unique angle

Combines clause‑level Neo4j relationship graphs with pgvector semantic search, enabling LLMs to retrieve not only the most relevant text but also the logical connections (e.g., amendment, inheritance, conflict) between clauses across contracts, and to generate answers that cite exact clause IDs and graph paths.

## 3. MVP features and acceptance criteria

### Contract Ingestion & Chunking

Upload PDF/DOCX contracts; automatic clause detection, embedding generation, and graph node creation.

- [ ] User can upload up to 10 contracts in a single session
- [ ] Each uploaded contract yields ≥95% clause extraction accuracy vs. manual annotation
- [ ] All clause nodes are searchable via vector index and appear in Neo4j with proper relationships

### Hybrid Retrieval Endpoint

FastAPI endpoint that accepts a natural‑language query, performs vector retrieval, expands results via graph hops, and returns top‑k passages with provenance.

- [ ] Response latency ≤ 1.5 s for 5‑clause queries
- [ ] Returned result includes clause ID, contract name, and graph path (e.g., "Amendment → inherits from")
- [ ] Confidence score is provided

### Answer Generation UI

React UI where users type questions, view LLM‑generated answer with inline citations linking to clause nodes.

- [ ] Answer shows clickable clause IDs that open a modal with full clause text
- [ ] Citations are accurate for ≥90% of test queries (manual verification)

## 4. Technology stack

- FastAPI (lightweight async API)
- LangChain (chain orchestration & RAG)
- OpenAI GPT‑4o (LLM inference)
- Neo4j (graph storage of clause entities & relationships)
- PostgreSQL + pgvector (dense vector store for clause embeddings)
- Supabase Auth (OAuth & row‑level security)
- Docker (containerization)
- GitHub Actions (CI/CD)
- OpenTelemetry (tracing & observability)
- React + Vite (frontend UI)

## 5. Architecture

A three‑layer system: (1) Data layer – PostgreSQL+pgvector for embeddings & Neo4j for clause graph; (2) Service layer – FastAPI orchestrates LangChain chains (vector retriever → graph expander → LLM); (3) Presentation layer – React SPA communicates via REST and receives streaming answers.

- **Ingestion Service** — Parse documents, detect clause boundaries, compute embeddings (sentence‑transformers), store vectors in pgvector, create clause nodes & relationships in Neo4j
- **Hybrid Retriever** — Given a query, fetch top‑k vector matches, then traverse Neo4j to fetch related clauses up to 2 hops
- **Answer Generator** — Construct prompt with retrieved context, invoke LLM, post‑process to insert citations
- **Auth & API Gateway** — Supabase JWT verification, tenant isolation, rate limiting
- **Observability** — OpenTelemetry traces for each request, exported to Loki/Prometheus

### Data flow

1. User uploads contract → Ingestion Service parses & populates PostgreSQL+Neo4j
2. User sends query → Auth validates → Hybrid Retriever returns enriched context → Answer Generator creates LLM prompt → LLM response streamed back → UI renders answer with clickable citations

## 6. Data model

- **Contract:** contract_id (UUID), name, upload_timestamp, owner_user_id
- **Clause:** clause_id (UUID), contract_id, clause_number, text, embedding (vector)
- **ClauseRelation:** src_clause_id, dst_clause_id, relation_type (e.g., amendment, inherits, conflict)

## 7. API contracts

| Method | Path | Purpose |
|---|---|---|
| POST | /api/v1/contracts | Upload a contract file for ingestion |
| GET | /api/v1/contracts/{contract_id} | Retrieve metadata of a stored contract |
| POST | /api/v1/query | Submit a natural‑language legal question and receive streamed answer with citations |
| GET | /api/v1/clauses/{clause_id} | Fetch full clause text and its immediate graph neighbors |

## 8. Build milestones

### 1 — Foundation & Ingestion

- [ ] Set up repo, Docker compose with Postgres, Neo4j, FastAPI skeleton
- [ ] Implement PDF/DOCX upload & clause splitter (regex + spaCy)
- [ ] Generate embeddings via sentence‑transformers and store in pgvector
- [ ] Create Neo4j nodes & basic "belongs_to" relationship

**Deliverable:** Working ingestion pipeline that can process 3 sample contracts

### 2 — Hybrid Retrieval & API

- [ ] Build LangChain vector retriever
- [ ] Integrate Neo4j traversal to enrich results
- [ ] Expose /api/v1/query endpoint with streaming response
- [ ] Add Supabase JWT auth

**Deliverable:** Functional query endpoint returning context objects

### 3 — Frontend & Evaluation

- [ ] Create React UI with query box & answer display
- [ ] Implement citation modals linking to clause view
- [ ] Write unit & integration tests (pytest, playwright)
- [ ] Add OpenTelemetry instrumentation

**Deliverable:** End‑to‑end demo with 5‑question test suite


## 9. Evaluation plan

Targets to test, not claimed results.

- **Clause Extraction F1:** Compare auto‑extracted clauses against manually annotated ground‑truth for 3 contracts Target: ≥0.92
- **Retrieval Precision@5:** Manual relevance assessment of top‑5 retrieved clauses per query Target: ≥0.85
- **Answer Citation Accuracy:** % of citations that correctly point to source clause used in LLM context Target: ≥0.90
- **Latency (99th percentile):** Locust load test with 50 concurrent users Target: ≤2 s

## Testing checklist

- [ ] Unit tests for document parser, embedding generator, and Neo4j writer
- [ ] Integration tests for /api/v1/query verifying response schema and citation links
- [ ] End‑to‑end UI tests with Playwright covering upload → query → citation click flow
- [ ] Security tests: JWT validation, SQL/graph injection attempts

## Deployment and setup

- [ ] Dockerize services; use docker‑compose for local dev
- [ ] Push images to GitHub Container Registry via Actions
- [ ] Deploy to Fly.io (or Render) with managed Postgres & Neo4j add‑on
- [ ] Configure HTTPS via Fly.io certificates; environment variables for API keys

## Prerequisites

- Python 3.11+
- Fundamentals of LLM prompting
- Basic Neo4j Cypher knowledge
- Understanding of vector embeddings

## Safety and privacy

- All data encrypted at rest (Postgres & Neo4j TLS)
- Supabase row‑level security isolates each tenant’s contracts
- No LLM prompts are logged beyond hashed identifiers; raw text kept in private VPC
- Compliance checklist: GDPR‑ready deletion endpoint for contracts

## Learning outcomes

- Design hybrid RAG pipelines that fuse vector similarity with graph traversal
- Model contract structures as a knowledge graph with clause provenance
- Implement secure multi‑tenant authentication for sensitive legal data
- Deploy a full‑stack AI service with observability

## Stretch goals

- Implement clause‑level versioning to track amendments over time
- Add multi‑modal support: ingest scanned contracts via OCR (Tesseract)
- Integrate a small‑scale local LLM (e.g., Llama‑3‑8B) for offline deployment
- Provide a “what‑if” scenario generator that rewrites clauses and re‑evaluates risk

## Resume bullet — add real results after implementation

Built a full‑stack LegalClauseGraphRAG (FastAPI + LangChain + Neo4j + pgvector) that ingests contracts, creates a clause‑level knowledge graph, and delivers LLM‑generated comparative answers with 90%+ citation accuracy; deployed via Docker on Fly.io and instrumented with OpenTelemetry.

## Interview questions

- Explain how you combined dense‑vector retrieval with graph traversal to improve relevance for legal queries.
- What challenges did you face when extracting clause boundaries from heterogeneous contract formats, and how did you address them?
- How does row‑level security in Supabase protect multi‑tenant legal data?
- Describe the prompt engineering technique you used to force the LLM to emit structured citations.
- Which metrics would you monitor in production to detect degradation of the retrieval component?

## Recent research to explore

Fetched from arXiv on this run; leads for further reading, not proof of originality.

- [Video-Coder: Reinforcing Agentic Coding for Video Generation](http://arxiv.org/abs/2611.09894v1) — updated 2026-11-06.
  - Recent years have witnessed remarkable progress in video generation in terms of visual quality and temporal consistency. However, generating videos with precise spatial structure, coherent motion dynamics, and controllable scene composition remains challenging. In this paper, we introduce Video-Code

- [On Agentic Manipulation Policies](http://arxiv.org/abs/2611.09892v1) — updated 2026-11-06.
  - Recent work on robot manipulation has focused on specialist policies trained on demonstrations. We show that generalist AI models can control manipulators more reliably than specialist policies such as vision-language-action models (VLAs) and world-action models (WAMs). We systematically analyze age

- [CPU-ARC: Agentic Reasoning Caching for on-CPU Reasoning Reuse](http://arxiv.org/abs/2611.09891v1) — updated 2026-11-06.
  - Large language models reinvent the wheel all the time. They conflate task-solving with the execution of the solutions, which forces them to solve every problem from scratch. We show that once a task has been reasoned through, the application of its solution to a new problem instance can be done very

- [On the (non-)closedness of the set of ReLU networks](http://arxiv.org/abs/2611.09887v1) — updated 2026-11-06.
  - We prove that the set $\mathcal{N}_N$ of ReLU networks with one hidden layer and at most $N\in\mathbb N$ neurons is weakly closed in $W^{1,p}(Ω)$, for a bounded connected open set $Ω\subset\mathbb R^d$. Consequently, every coercive, weakly lower semicontinuous energy on this space attains its minimu

- [FlowMoP: Stochastic Multi-Person Motion Prediction](http://arxiv.org/abs/2611.09882v1) — updated 2026-11-06.
  - Predicting the future motion of multiple people is inherently stochastic: the same observed history admits many plausible continuations depending on intent, coordination, and social context. Yet the dominant paradigm in multi-person 3D motion prediction remains deterministic, with existing methods p

- [ZeoBench: A Benchmark for Self-Supervised Learning on 3D Zeolite Representations](http://arxiv.org/abs/2611.09880v1) — updated 2026-11-06.
  - Zeolites are an important class of porous crystalline materials with broad applications in gas storage, separations, and catalysis. Although hundreds of thousands of experimentally realized and hypothetical zeolite structures are known, identifying materials optimized for a target application remain

- [Graded convolutional networks: scale invariance without the scale and robustness to unknown blur](http://arxiv.org/abs/2611.09878v1) — updated 2026-11-06.
  - The Gaussian jet of an image is a graded vector space: a dilation by $λ$ multiplies derivatives of order $k$ by $λ^{-k}$. Local graded convolutions are exactly homogeneous differential operators, and a local feature is dilation-invariant if and only if it factors through the scale-normalized jet or,

- [On the Reliability of Majority-Vote Pseudo-Labels in Test-Time Reinforcement Learning](http://arxiv.org/abs/2611.09872v1) — updated 2026-11-06.
  - Test-time reinforcement learning (TTRL) adapts pretrained language models to unlabeled target-domain data using self-generated pseudo-labels, whose reliability remains poorly understood. We analyze majority-vote supervision for TTRL with online Direct Preference Optimization (DPO) and decompose its 


## Hugging Face optimization

- Status: failed_keep_original
- Model: openai/gpt-oss-120b:fastest
- Note: Client error '402 Payment Required' for url 'https://router.huggingface.co/v1/chat/completions' (Request ID: Root=1-6af19da6-713209f7732643a43851fbf4;2d6509e8-d4e8-4612-b5c2-34d12e518390)
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/402

Purchase pre-paid credits to continue using Inference Providers. Alternatively, subscribe to PRO to get monthly included credits.

## Gemini design review

- Novelty score: 6/10
- Feasibility score: 7/10

### Overlap risks

- Standard GraphRAG pattern using Neo4j + Vector DB
- Numerous commercial and open-source legal AI / contract review tools (e.g., Robin AI, LexisNexis, Harvey, open-source contract RAG repos)
### Suggested improvements

- Specify how cross-contract clause relationships (e.g., 'conflict', 'amendment', 'inherits') are extracted, as standard regex/spaCy parser alone cannot reliably identify semantic legal graph edges without an LLM-based relation extraction step
- Consolidate the dual-database architecture: Neo4j natively supports vector search and embeddings storage, eliminating the need to sync pgvector and Neo4j for clause embeddings
- Adjust the estimated timeline: 7 days is extremely tight for building multi-format contract parsing, Neo4j graph modeling, pgvector indexing, multi-tenant Supabase auth, React UI, and OpenTelemetry instrumentation

---
Generated with Groq / openai/gpt-oss-120b. Verify assumptions and report only measured results.

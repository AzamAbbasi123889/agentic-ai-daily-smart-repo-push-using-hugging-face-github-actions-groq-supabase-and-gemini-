# Contextual GraphRAG for Academic Literature Exploration

> An LLM‑augmented retrieval system that combines dense vector search with a Neo4j knowledge graph of research papers, enabling multi‑hop, citation‑aware answers to complex scholarly queries.

**Date:** 2026-10-10 | **Category:** Advanced RAG and GraphRAG | **Difficulty:** Intermediate | **Effort:** 5 days

**Build-it-yourself brief:** this factory produces the specification, not source code.

## 1. Problem statement

Students and researchers struggle to synthesize information across large collections of papers, often needing to trace concepts through citations and related works. Traditional keyword or flat vector search cannot capture the rich relational structure of scientific knowledge, leading to fragmented or out‑of‑context answers.

### Target users

- Graduate students
- Research analysts
- Science journalists
- Product managers evaluating tech trends

## 2. Unique angle

Integrates a citation‑and‑concept knowledge graph with LLM‑driven reasoning, allowing the agent to explicitly traverse citation chains and infer implicit relationships before generating answers—going beyond flat semantic similarity.

## 3. MVP features and acceptance criteria

### Paper Ingestion Pipeline

Upload a PDF or URL; extract text, chunk, embed, store embeddings in Postgres and metadata in Neo4j.

- [ ] Upload succeeds for at least 10 sample arXiv PDFs
- [ ] Embeddings stored with <0.5 s latency per chunk
- [ ] Citation edges created correctly (>=90% of detected citations)

### Hybrid Retrieval API

Given a natural‑language query, retrieve top‑k relevant chunks via vector search, then expand context by traversing up to 2 hops in the graph (citations, concept links).

- [ ] API returns combined results within 2 s for queries on 5 k papers
- [ ] At least 1 citation hop is included for 70% of queries

### LLM Answer Generation

Pass retrieved context to gpt‑4o-mini with a structured prompt; return answer plus cited source IDs.

- [ ] Answers include a "Sources" section with correct paper IDs
- [ ] Human evaluator rates relevance ≥4/5 on 20 test questions

## 4. Technology stack

- FastAPI (lightweight HTTP API)
- LangChain (LLM orchestration)
- LangGraph (stateful graph‑based agent)
- OpenAI gpt‑4o-mini (cheap LLM)
- Sentence‑Transformers (embedding model)
- Postgres + pgvector (store paper embeddings)
- Neo4j (property graph for citations, entities, sections)
- Docker (containerization)
- GitHub Actions (CI/CD)
- OpenTelemetry (observability)

## 5. Architecture

A FastAPI front‑end receives documents and queries. Ingestion writes to Postgres (embeddings) and Neo4j (graph). Query handling first performs vector retrieval, then a GraphRAG expansion step orchestrated by LangGraph, finally invoking the LLM for answer synthesis. Observability hooks emit traces to OpenTelemetry.

- **FastAPI Service** — HTTP endpoint layer, request validation, auth

### Data flow

1. User uploads PDF → Ingestion Worker → Text chunks stored in Postgres; metadata & citations stored in Neo4j
2. User sends query → FastAPI → LangGraph starts: vector retrieval → graph hop expansion → LLM call → response returned

## 6. Data model

- **Paper:** paper_id (UUID), title (text), authors (text[]), year (int), doi (text), embedding (vector)
- **Citation:** src_paper_id (FK), dst_paper_id (FK), context_sentence (text)
- **Concept:** concept_id (UUID), name (text), embedding (vector)
- **PaperConcept:** paper_id (FK), concept_id (FK)

## 7. API contracts

| Method | Path | Purpose |
|---|---|---|
| POST | /ingest | Upload PDF or URL for processing |
| GET | /search | Hybrid query endpoint; parameters: q (string), k (int, default 5) |

## 8. Build milestones

### 1 — Setup & Ingestion

- [ ] Create repo, CI pipeline, Dockerfile
- [ ] Implement PDF text extraction (pdfminer)
- [ ] Build Neo4j schema & citation parser
- [ ] Generate embeddings with sentence‑transformers

**Deliverable:** Ingestion API functional for 10 sample papers


## 9. Evaluation plan

Targets to test, not claimed results.

- **Mean Reciprocal Rank (MRR) of retrieved chunks vs. ground‑truth relevance set:** Manual relevance judgments on 30 queries Target: ≥0.65

## Testing checklist

- [ ] Unit tests for PDF parsing and citation extraction
- [ ] Integration tests for vector‑graph pipeline using pytest‑asyncio
- [ ] Load test: 100 concurrent /search requests with locust (target <2 s latency)
- [ ] Security test: OWASP API Top 10 scan

## Deployment and setup

- [ ] Containerize with Docker Compose (api, postgres, neo4j)
- [ ] Deploy to Railway or Render (free tier) for MVP
- [ ] Configure HTTPS via Let's Encrypt
- [ ] Set up GitHub Actions to build, test, and push Docker images

## Prerequisites

- Python 3.10+
- Basic knowledge of LLM prompting
- Familiarity with graph databases (Cypher)
- Understanding of vector similarity search

## Safety and privacy

- Store only metadata and public abstracts; no full‑text PDFs beyond 30 days unless user consents
- Sanitize LLM prompts to prevent prompt injection
- Rate‑limit /search to 30 rpm per IP
- Log access for audit with OpenTelemetry

## Learning outcomes

- Design a hybrid retrieval pipeline (vector + graph)
- Model citation graphs and entity extraction from PDFs
- Orchestrate multi‑step LLM reasoning with LangGraph
- Deploy a production‑grade FastAPI service with observability

## Stretch goals

- Implement feedback loop: user up‑votes helpful citations → re‑rank graph edges
- Add cross‑language support via multilingual sentence‑transformers
- Replace OpenAI model with an open‑source LLaMA‑3 via vLLM for cost reduction

## Resume bullet — add real results after implementation

Designed and delivered a GraphRAG prototype that merged vector similarity with a Neo4j citation graph, achieving ≥0.65 MRR and 4/5 average answer relevance on a 30‑query benchmark; deployed end‑to‑end service on Render with CI/CD and OpenTelemetry tracing.

## Interview questions

- Explain how GraphRAG differs from pure vector RAG and why you chose Neo4j for citations.
- Describe the state management in LangGraph for multi‑step retrieval.
- How would you mitigate hallucinations when the LLM cites a source not present in the retrieved context?
- What trade‑offs did you consider when selecting pgvector vs. dedicated vector DBs?
- How does your ingestion pipeline handle ambiguous citation strings?

## Recent research to explore

Fetched from arXiv on this run; leads for further reading, not proof of originality.

- [Dex-One2Many: Learning Dexterous Manipulation from a Single Human Demonstration](http://arxiv.org/abs/2610.12470v1) — updated 2026-10-08.
  - While learning dexterous manipulation from a single human video offers a promising alternative to costly robot demonstrations, many recent methods predominantly imitate demonstrated motions. Such strict motion matching often limits generalization to initial object poses, goal poses, and grasps not s

- [Rubric-CEPR: Self-Evolving Image Editing via Reward-Verified Self-Distillation](http://arxiv.org/abs/2610.12469v1) — updated 2026-10-08.
  - Instruction-guided image editors have become highly capable, yet improving them further still depends on human-edited training pairs or external reward models. Such supervision is costly to obtain and can reward plausible failures: a realistic output may leave the requested change undone or alter co

- [DreamTrue: Action-Faithful Robot World Model with Counterfactual Post-Training](http://arxiv.org/abs/2610.12468v1) — updated 2026-10-08.
  - We present DreamTrue, a multi-view, cross-embodiment robot world model for action-faithful and physically plausible video prediction. Training such a model on existing robot datasets faces two obstacles: imprecise calibration can impair action following, while limited coverage of unsuccessful intera

- [CSF: Contextual Safety Filtering for Motion Generators](http://arxiv.org/abs/2610.12467v1) — updated 2026-10-08.
  - Text-conditioned motion generators produce trackable whole-body motion, but they have no notion of scene-dependent safety: the same action may target an object or a person. Existing safeguards either inspect the prompt, require labeled motion data, or enforce geometric constraints; therefore, they d

- [On the estimation and validity of AI time horizons---a statistical look at the METR plot](http://arxiv.org/abs/2610.12466v1) — updated 2026-10-08.
  - METR's 50\% time horizon measures the human completion time of software tasks that an AI solves with 50\% probability, allowing AI capabilities to be expressed in interpretable units. On 228 tasks and 26 AIs, we recompute the time horizons using splines and item-response theory to relax the assumpti

- [A Balanced Data Diet: Addressing the Exploration Bottleneck in Mega-Scale RL for Robot Control](http://arxiv.org/abs/2610.12465v1) — updated 2026-10-08.
  - General-purpose robots must perform a wide range of tasks from agile locomotion to dexterous manipulation. While sim-to-real reinforcement learning (RL) has proven to be a useful tool for this goal, current RL pipelines depend on engineering-heavy, per-task structural priors such as shaped rewards a

- [From Reactive Containment to Proactive Assurance: Lessons from OpenAI, Anthropic, and Google Agent Security Incidents](http://arxiv.org/abs/2610.12463v1) — updated 2026-10-08.
  - In 2026, cybersecurity evaluations involving OpenAI, Anthropic, and Google agents reached real systems outside their authorized test scope. The paths were different. OpenAI agents exploited research infrastructure, coordinated across runs, and compromised parts of Hugging Face's production environme

- [What 30,000 Hours of Ego-centric Video Does Not Teach](http://arxiv.org/abs/2610.12464v1) — updated 2026-10-08.
  - World models offer a promising alternative to physics-based simulators, yet remain far from practical deployment. We ask how far scaling ego-centric human video takes them, using a dataset of 30,000 hours spanning over 1,000 scene types and 14,000 contributors. Rather than relying on opaque downstre


## Hugging Face optimization

- Status: failed_keep_original
- Model: openai/gpt-oss-120b:fastest
- Note: Client error '402 Payment Required' for url 'https://router.huggingface.co/v1/chat/completions' (Request ID: Root=1-6aca71a3-3956152d28670c37446762ce;5e92c4a0-55d2-4f80-aedb-c67cdf4238d7)
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/402

You have no remaining credits. Purchase pre-paid credits to continue using Inference Providers. Alternatively, subscribe to PRO to get monthly included credits.

## Gemini design review

- Novelty score: 4/10
- Feasibility score: 7/10

### Overlap risks

- High similarity to standard Neo4j GenAI templates and LlamaIndex Knowledge Graph / Property Graph tutorials.
- Existing commercial and open-source tools already implement academic citation exploration (e.g., Semantic Scholar, Connected Papers, Litmaps, ResearchRabbit).
- Standard multi-hop GraphRAG patterns overlap heavily with Microsoft GraphRAG and LangChain/LangGraph cookbook examples.
### Suggested improvements

- Leverage OpenAlex or Semantic Scholar APIs for structured citation networks and metadata instead of parsing raw PDF reference sections from scratch within a 5-day timeline.
- Incorporate community detection algorithms (e.g., Leiden or Louvain clustering) to support hierarchical macro-level topic synthesis alongside micro citation hops.
- Implement citation disambiguation (entity resolution) with author/year validation to avoid noisy edges in the Neo4j graph.
- Consolidate the storage layer by evaluating Neo4j's native vector index to avoid split-brain state synchronization between Postgres+pgvector and Neo4j.

---
Generated with Groq / openai/gpt-oss-120b. Verify assumptions and report only measured results.

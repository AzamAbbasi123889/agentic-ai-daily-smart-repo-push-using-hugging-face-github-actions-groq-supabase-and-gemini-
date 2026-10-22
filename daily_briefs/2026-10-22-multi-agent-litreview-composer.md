# Multi‑Agent Literature Review Composer

> An agentic web service that automatically generates a structured, citation‑rich literature review on a user‑specified topic by coordinating specialized LLM agents for search, extraction, citation graph building, gap analysis, and drafting, all orchestrated with LangGraph and CrewAI.

**Date:** 2026-10-22 | **Category:** LangChain, LangGraph, CrewAI | **Difficulty:** Advanced | **Effort:** 7 days

**Build-it-yourself brief:** this factory produces the specification, not source code.

## 1. Problem statement

Researchers spend excessive time manually collecting papers, extracting key contributions, mapping citations, and identifying research gaps; a privacy‑first, reproducible assistant that performs these steps end‑to‑end can dramatically speed up the early phases of scholarly work.

### Target users

- Graduate students
- Academic researchers
- R&D analysts

## 2. Unique angle

Leverages a dynamic multi‑agent workflow to not only summarize papers but also construct a citation graph, perform automated gap detection, and output a ready‑to‑cite, markdown‑formatted review, all running locally without external data leakage.

## 3. MVP features and acceptance criteria

### Topic Intake & Paper Retrieval

User submits a research topic; system queries arXiv/Semantic Scholar via public APIs, stores PDFs and metadata.

- [ ] API returns at least 10 relevant papers within 30 seconds
- [ ] Metadata (title, authors, abstract, DOI) saved in Postgres
- [ ] PDFs downloaded and indexed for embedding

### Citation Graph Construction

Extract reference lists from PDFs, normalize citations, and populate a Neo4j graph linking papers.

- [ ] Graph contains nodes for all retrieved papers
- [ ] Edges represent citation relationships
- [ ] Cypher query can retrieve upstream/downstream citations

### Key Insight Extraction Agent

Agent reads each paper’s abstract & conclusion, produces a concise 3‑sentence summary and a list of contributions.

- [ ] Each paper has a JSON record with "summary" and "contributions" fields
- [ ] Summaries pass a regex check for length (150‑250 characters)

### Gap‑Analysis Agent

Analyzes the citation graph and extracted contributions to highlight under‑explored sub‑topics.

- [ ] Produces a markdown list of at least 3 research gaps
- [ ] Each gap is linked to supporting papers via citations

### Review Drafting Agent

Combines summaries, citation graph, and gap analysis into a structured markdown literature review.

- [ ] Output contains sections: Introduction, Summary Table, Thematic Synthesis, Gaps, References
- [ ] References are properly formatted and hyperlinked

## 4. Technology stack

- FastAPI (lightweight HTTP API)
- LangChain (LLM wrappers, document loaders)
- LangGraph (state‑machine orchestration of agents)
- CrewAI (role‑based agent definitions)
- Postgres with pgvector (store paper metadata & embeddings)
- Neo4j (citation graph)
- OpenAI/gpt‑4o-mini (free tier LLM)
- Docker (containerisation)
- GitHub Actions (CI/CD)

## 5. Architecture

A FastAPI front‑end receives a topic, triggers a LangGraph workflow that coordinates CrewAI agents; data persists in Postgres (metadata & embeddings) and Neo4j (citation graph). The final markdown is returned to the client.

- **FastAPI Gateway** — Expose REST endpoints, handle auth, start workflow
- **LangGraph Orchestrator** — Manage state transitions between agents, retry logic
- **CrewAI Agents** — Perform specialized tasks (search, extraction, gap detection, drafting)
- **Postgres + pgvector** — Store paper metadata, embeddings for semantic search
- **Neo4j** — Persist and query citation relationships
- **LLM Service** — Generate summaries, gaps, and draft text

### Data flow


## 6. Data model

- **paper:** id (UUID), title, authors (JSON), abstract, doi, pdf_path, embedding (vector), retrieved_at
- **citation:** source_paper_id, target_paper_id
- **summary:** paper_id, summary_text, contributions (JSON)

## 7. API contracts

| Method | Path | Purpose |
|---|---|---|
| POST | /review | Accept a research topic and launch the review generation workflow |
| GET | /review/{job_id} | Poll the status and retrieve the final markdown when ready |
| GET | /healthz | Liveness probe for deployment |

## 8. Build milestones

### 1 — MVP Delivery

- [ ] Set up FastAPI skeleton and Dockerfile
- [ ] Implement paper retrieval using arXiv API
- [ ] Create Postgres schema + pgvector indexing
- [ ] Build LangGraph workflow with Search and Extraction agents
- [ ] Persist results and expose /review endpoint

**Deliverable:** Working service that returns a markdown review for a topic with at least 5 papers


## 9. Evaluation plan

Targets to test, not claimed results.

- **End‑to‑end latency:** Time from POST /review to 200 response Target: < 60 seconds for 10 papers
- **Citation graph completeness:** Percentage of retrieved papers that have at least one outgoing or incoming edge Target: ≥ 80%
- **Summary quality (BLEU‑like proxy):** Compare agent summaries to human‑written abstracts on a 5‑sample set using sentence‑bert cosine similarity Target: ≥ 0.78

## Testing checklist

- [ ] Unit tests for each agent’s tool usage
- [ ] Integration test that runs the full LangGraph pipeline on a mock topic
- [ ] Schema validation tests for Postgres and Neo4j entries
- [ ] Contract tests for all API endpoints (status codes, JSON schema)

## Deployment and setup

- [ ] Docker‑compose for local development (fastapi, postgres, neo4j)
- [ ] GitHub Actions CI builds image and runs tests
- [ ] GitHub Actions CD pushes to Docker Hub and deploys to Railway (free tier)
- [ ] Environment variables for LLM API keys, DB credentials

## Prerequisites

- Python 3.10+
- Basic knowledge of FastAPI and SQLAlchemy
- Familiarity with LangChain abstractions
- Understanding of graph databases (Neo4j)

## Safety and privacy

- All data stored locally; no external logging of PDFs or summaries
- Rate‑limit external arXiv calls to respect API policy
- LLM prompts sanitized to avoid prompt injection
- Provide option to delete a job and its associated data via DELETE /review/{job_id}

## Learning outcomes

- Design and implement a multi‑agent workflow with LangGraph
- Use CrewAI to define role‑specific prompts and tool usage
- Integrate dense‑vector retrieval with pgvector
- Build and query a citation graph in Neo4j
- Deploy a reproducible FastAPI service with Docker

## Stretch goals

- Add a citation‑impact ranking using Semantic Scholar citation counts
- Allow user‑provided PDFs to be merged with auto‑retrieved set
- Integrate a UI built with React for interactive editing of the generated review

## Resume bullet — add real results after implementation

Designed and shipped a privacy‑first multi‑agent literature review composer that auto‑generated structured reviews for 10+ papers in <60 s, achieving 0.78 avg. semantic similarity to human summaries

## Interview questions

- Explain how LangGraph differs from a simple sequential script and why it was chosen for this project.
- Describe the role of CrewAI in defining agent responsibilities and how tool usage is controlled.
- How does the citation graph in Neo4j enable automated gap detection?
- What strategies did you employ to keep user data private while using a hosted LLM?
- If the arXiv API rate‑limits you, how would you redesign the retrieval component?

## Recent research to explore

Fetched from arXiv on this run; leads for further reading, not proof of originality.

- [LongZero: Enhancing Long-Context Reasoning in LLMs from Zero Data](http://arxiv.org/abs/2610.30132v1) — updated 2026-10-21.
  - Reinforcement learning (RL) is an effective way to strengthen the long-context reasoning of large language models (LLMs), but it needs training data that are long, diverse, challenging, and verifiable. Human annotation of such data is expensive, naturally occurring data are too scarce to sustain RL,

- [Rethinking Video Autoencoders for Interactive World Models](http://arxiv.org/abs/2610.30129v1) — updated 2026-10-21.
  - Video world models predict future frames from past frames and actions. They serve as simulators in which agents train, plan or are evaluated, and that humans can control interactively. They generate in the latent space of a video autoencoder, whose compression sets their cost per frame and how long 

- [Think Harder Where It Matters: Item-Level Adaptive Recursion for Sequential Recommendation](http://arxiv.org/abs/2610.30128v1) — updated 2026-10-21.
  - Existing sequential recommenders usually allocate a fixed computational budget to every item in a user's interaction history, regardless of the item's contribution to the final prediction. We challenge this de facto design with two diagnostic findings. (1) Non-uniform computational need: items withi

- [VoxProg: 3D Spatial Reasoning through Voxel Programming](http://arxiv.org/abs/2610.30127v1) — updated 2026-10-21.
  - Language models' abilities to interpret tasks and generate programs offer a promising basis for 3D spatial reasoning. Yet following spatial instructions in 3D scenes requires programs to construct geometric references that language leaves implicit. In this work, we introduce VoxProg, which formulate

- [PhysiCalWorld: In-Context Physics Calibration for World Models](http://arxiv.org/abs/2610.30125v1) — updated 2026-10-21.
  - Existing world models typically perceive a scene through current visual frame or a narrow history window. However, these observations may not reveal the physics properties that determine transition dynamics, such as an object's mass distribution, joint damping, or surface friction. Without calibrati

- [A Quasipolynomial Algorithm for $\ell_\infty$ Contractions](http://arxiv.org/abs/2610.30122v1) — updated 2026-10-21.
  - We give an algorithm for computing an $\eps$-approximate fixed point of any $d$-dimensional nonexpansion with respect to the $\ell_\infty$ norm in time $\log(1/\eps)^{O(\log^2 d)}$. At its core, our method uses a boosting argument to geometrically shrink a search region. Among other consequences, ou

- [ALPS: Visual State Encoders for World Models](http://arxiv.org/abs/2610.30120v1) — updated 2026-10-21.
  - World models turn visual representations into predictions and actions. We argue that their visual foundation should combine physical-state information, native language alignment, and pixel reconstruction, so that a single representation can support prediction, instruction, and inspection. However, e

- [Self-normalized Bernstein Inequalities for Regenerative Processes and Applications to Learning Without Independence](http://arxiv.org/abs/2610.30119v1) — updated 2026-10-21.
  - We prove a self-normalized Bernstein inequality for bounded functions of a regenerative process with independent, identically distributed marked cycles of finite mean length. The bound uses observed cycle lengths and retains explicit terms for truncation and the cycle ending after the observation ho


## Hugging Face optimization

- Status: failed_keep_original
- Model: openai/gpt-oss-120b:fastest
- Note: Client error '402 Payment Required' for url 'https://router.huggingface.co/v1/chat/completions' (Request ID: Root=1-6ad9c127-45199f82195da6fc272cafaf;22e468f3-5903-4876-9f7f-058865f50514)
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/402

You have no remaining credits. Purchase pre-paid credits to continue using Inference Providers. Alternatively, subscribe to PRO to get monthly included credits.

---
Generated with Groq / openai/gpt-oss-120b. Verify assumptions and report only measured results.

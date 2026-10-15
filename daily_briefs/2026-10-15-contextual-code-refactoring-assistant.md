# Contextual Code Refactoring Assistant

> A privacy‑first web service that builds a lightweight code‑entity graph from a user’s repository and uses an LLM to suggest context‑aware refactorings, supporting one‑click apply via a REST API.

**Date:** 2026-10-15 | **Category:** AI Developer Tools and Code Intelligence | **Difficulty:** Intermediate | **Effort:** 7 days

**Build-it-yourself brief:** this factory produces the specification, not source code.

## 1. Problem statement

Developers often spend time identifying repetitive patterns and unsafe code smells across large codebases. Existing linters provide rule‑based suggestions but lack semantic understanding, while generic LLM assistants ignore project‑specific context, leading to noisy or unsafe recommendations.

### Target users

- Software engineers looking to improve code quality
- Students learning best‑practice refactoring
- Teams wanting an on‑premise AI code‑assistant

## 2. Unique angle

First open‑source tool that merges a Neo4j code‑entity graph (functions, classes, imports) with LLM‑driven suggestions, delivering project‑specific refactorings without sending code to external services.

## 3. MVP features and acceptance criteria

### Upload Repository

POST endpoint that accepts a zip of a Python project, extracts AST, populates Neo4j nodes/relationships, and creates vector embeddings for each function/method.

- [ ] API returns 202 with job_id
- [ ] Graph contains at least 90% of functions detected
- [ ] Embeddings stored in Neo4j property 'embedding'

### Suggest Refactoring

GET endpoint that takes a file path and line range, retrieves surrounding graph context, queries LLM, and returns a ranked list of refactoring suggestions with diff patches.

- [ ] Returns ≥3 suggestions
- [ ] Each suggestion includes a valid unified diff
- [ ] Confidence score >0.6 for at least one suggestion

### Apply Patch

POST endpoint that receives a suggestion id, validates diff safety, and returns the updated source file.

- [ ] Patch applies cleanly with no syntax errors
- [ ] Git‑style response includes changed lines

## 4. Technology stack

- FastAPI – lightweight async API server
- Neo4j – stores code graph for fast traversal and context retrieval
- LangChain – orchestrates LLM prompts with retrieved graph context
- Sentence‑Transformers (all‑MiniLM) – embeds code snippets for similarity search
- Docker – reproducible container for local deployment
- GitHub Actions – CI/CD pipeline with unit & integration tests
- OpenTelemetry – optional tracing for performance monitoring

## 5. Architecture

FastAPI receives requests, invokes the CodeGraph Service (Neo4j + embedding store) to fetch context, then calls LLM via LangChain. Results are formatted as diffs and sent back. All components run in Docker containers for easy local deployment.

- **API Layer** — Validate requests, orchestrate workflow, expose HTTP endpoints
- **CodeGraph Service** — Parse uploaded code, build Neo4j graph, compute embeddings
- **LLM Engine** — Generate context‑aware refactoring suggestions using LangChain prompts
- **Diff Engine** — Render LLM output into unified diffs and perform safety checks

### Data flow

1. User uploads zip → API triggers async parser → AST → Neo4j nodes/relationships + embeddings → User requests suggestion → API queries Neo4j for surrounding entities → LangChain builds prompt with retrieved context → LLM returns suggestion → Diff Engine formats → Response

## 6. Data model

- **File:** id (UUID), path (string), content (text)
- **Function:** id (UUID), name (string), start_line (int), end_line (int), code (text), embedding (float[] ), file_id (FK)
- **Import:** id (UUID), module (string), line (int), file_id (FK)
- **CallRelation:** caller_id (FK), callee_id (FK)

## 7. API contracts

| Method | Path | Purpose |
|---|---|---|
| POST | /api/v1/upload | Upload a zip of a Python project for indexing |
| GET | /api/v1/suggest | Get refactoring suggestions for a given file and line range (query params: file_path, start, end) |
| POST | /api/v1/apply | Apply a selected diff patch (body: suggestion_id) |

## 8. Build milestones

### 1 — Foundations & Graph Construction

- [ ] Set up FastAPI skeleton
- [ ] Implement zip upload & async extraction
- [ ] Parse AST to generate Neo4j nodes
- [ ] Compute embeddings with Sentence‑Transformers
- [ ] Write CI pipeline with unit tests

**Deliverable:** Working /upload endpoint that populates Neo4j for a sample repo


## 9. Evaluation plan

Targets to test, not claimed results.

- **Suggestion Relevance:** Manual rating of top‑3 suggestions on 10 open‑source projects (scale 1‑5) Target: Average rating ≥4
- **Patch Safety:** Run flake8 & pytest on applied patches Target: Zero new lint failures in 95% of patches

## Testing checklist

- [ ] Unit tests for AST parser and Neo4j insertion
- [ ] Integration tests for each endpoint using pytest‑asyncio
- [ ] Mock LLM responses to verify prompt composition
- [ ] Security test: ensure uploaded zip cannot escape sandbox

## Deployment and setup

- [ ] Dockerfile builds multi‑stage image (Python runtime + Neo4j community edition)
- [ ] docker‑compose.yml defines api and neo4j services with persisted volume
- [ ] GitHub Actions workflow builds image, runs tests, pushes to GitHub Packages
- [ ] Optional: Deploy to Render or Railway for public demo

## Prerequisites

- Python 3.11+
- Basic knowledge of AST parsing (ast module)
- Familiarity with Neo4j Cypher queries
- Understanding of prompt engineering for LLMs

## Safety and privacy

- All processing occurs locally; no code is sent to external services
- Uploaded archives are stored in a temporary directory and deleted after indexing
- LLM provider accessed via secure HTTPS with API key stored in env variable
- Diff engine rejects patches that introduce import of unsafe modules (e.g., os.system)

## Learning outcomes

- Parse Python code into an entity graph
- Integrate vector embeddings with graph traversal
- Design context‑aware LLM prompts
- Build a production‑ready FastAPI service
- Apply CI/CD and observability to an AI tool

## Stretch goals

- Support multi‑language codebases (JavaScript, Go) via tree‑sitter parsers
- Add a VS Code extension that calls the API directly from the editor
- Implement RL‑based fine‑tuning where user‑acceptance feedback improves future suggestions

## Resume bullet — add real results after implementation

Built a privacy‑first Contextual Code Refactoring Assistant (FastAPI + Neo4j + LangChain) that generated project‑aware refactoring diffs with 92% relevance rating and zero safety regressions across 10 open‑source repos, packaged in Docker and CI‑tested with 95% coverage.

## Interview questions

- How does combining a graph database with vector embeddings improve LLM prompt relevance?
- Describe how you ensured that generated patches are syntactically safe before applying them.
- What trade‑offs did you consider when choosing Neo4j over a pure vector store like FAISS?
- Explain how you would extend the system to support incremental indexing for large monorepos.

## Recent research to explore

Fetched from arXiv on this run; leads for further reading, not proof of originality.

- [Can Learning to Answer Spatial Questions Improve Novel-View Generation?](http://arxiv.org/abs/2610.20610v1) — updated 2026-10-14.
  - Generating novel views from limited observations requires preserving both the appearance and spatial structure of a scene. Although recent approaches exploit fine-grained geometric cues, they do not explicitly model high-level semantic and spatial properties such as object identity, attributes, and 

- [Modeling and Understanding Neural Weights of Humanoid Policies with Diffusion](http://arxiv.org/abs/2610.20606v1) — updated 2026-10-14.
  - Recent advances in robot learning have driven rapid progress in humanoid control, enabling increasingly agile behaviors in the real world. However, humanoid control networks are typically obtained through conventional training procedures, while comparatively little attention has been given to direct

- [Representation Conditioning for Generation](http://arxiv.org/abs/2610.20608v1) — updated 2026-10-14.
  - Representation-alignment methods effectively accelerate the diffusion transformer training. REPA, for example, uses a pretrained vision encoder to supervise an intermediate layer through an MLP projection head which is discarded after training. It aims to import semantics from the vision encoder to 

- [Hierarchical Residual Policy Learning for Real-World Mobile Manipulation with Sparse Human Guidance](http://arxiv.org/abs/2610.20607v1) — updated 2026-10-14.
  - Mobile Manipulation (MoMa) is a cornerstone of autonomous robotic systems, yet real-world fine-tuning remains a formidable challenge because of high-dimensional action spaces and intricate coupling between heterogeneous modules. In this paper, we propose HiRe-MoMa (Hierarchical Residual Mobile Manip

- [VITAL: From Visual Motion to Precise Action](http://arxiv.org/abs/2610.20604v1) — updated 2026-10-14.
  - World-action models aim to turn visual anticipation into driving decisions, yet typically train action experts on trajectory representations defined independently of visual dynamics. This motivates deriving action targets directly from visual motion. We first examine a simpler setting in which traje

- [CommerceGen-Studio: An End-to-End Framework for Commercial-Grade Main-Image Generation](http://arxiv.org/abs/2610.20603v1) — updated 2026-10-14.
  - We present CommerceGen-Studio, an end-to-end framework for generating commercial-grade main images for e-commerce Stock Keeping Units (SKUs). Our framework is organized along a three-stage pipeline of information extraction, semantic rewriting, and multi-condition generation: Prompt-Eval-Refine-Loop

- [DynThinker: Unifying Static 3D and Dynamic 4D Spatial Reasoning](http://arxiv.org/abs/2610.20598v1) — updated 2026-10-14.
  - Achieving general spatial intelligence requires a unified understanding of both static 3D and dynamic 4D. However, we find that existing models struggle to excel at both: 3D post-training can weaken dynamic understanding, while 4D-specialized models often lack strong static 3D reasoning. Our analysi

- [Co-Evolving Acting and Forecasting for Language Agents](http://arxiv.org/abs/2610.20597v1) — updated 2026-10-14.
  - Training language agents is bottlenecked by the high cost of long-horizon rollouts, yet standard agentic reinforcement learning (RL) learns only from a terminal scalar reward, leaving the supervision in intermediate steps largely unused. Prior work exploits this supervision through value targets tha


## Hugging Face optimization

- Status: failed_keep_original
- Model: openai/gpt-oss-120b:fastest
- Note: Client error '402 Payment Required' for url 'https://router.huggingface.co/v1/chat/completions' (Request ID: Root=1-6ad083db-226dbc10353d9b981e3ec98b;b9cb5a2d-42b8-4a9d-9f9b-f1e2df426bba)
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/402

You have no remaining credits. Purchase pre-paid credits to continue using Inference Providers. Alternatively, subscribe to PRO to get monthly included credits.

## Gemini design review

- Novelty score: 5/10
- Feasibility score: 7/10

### Overlap risks

- High overlap with existing code intelligence and autonomous refactoring tools such as Aider (repo-map via ctags/tree-sitter), Sourcegraph Cody, Cursor, and Qodo (formerly Codium).
- Graph-RAG for codebases is a well-established pattern in both research and commercial dev tools (e.g., Bloop, Greptile, Sweep).
### Suggested improvements

- Resolve privacy contradiction: the brief claims code is not sent to external services, but also states LLM providers are accessed via HTTPS with an API key; explicitly integrate local inference runtimes (e.g., Ollama or vLLM) to fulfill the on-premise privacy pledge.
- Replace standard Python 'ast' with 'tree-sitter' and a symbol indexer (such as Jedi or Pyright SCIP) because pure AST parsing cannot reliably resolve cross-module dynamic call graphs in Python.
- Adopt AST-aware rewriting libraries like LibCST instead of raw unified text diffs from LLM completions, which frequently hallucinate line numbers and whitespace indentation.

---
Generated with Groq / openai/gpt-oss-120b. Verify assumptions and report only measured results.

# LLM Hallucination Guard (Local)

> A privacy‑first FastAPI service that detects and mitigates factual hallucinations in LLM responses by cross‑checking generated statements against a locally stored knowledge base with vector search and a lightweight consistency classifier.

**Date:** 2026-10-20 | **Category:** AI Safety, Privacy and Security | **Difficulty:** Intermediate | **Effort:** 5 days

**Build-it-yourself brief:** this factory produces the specification, not source code.

## 1. Problem statement

LLMs frequently generate plausible‑looking but factually incorrect statements, posing risks for downstream applications that rely on trustworthy information. Users need an easy‑to‑integrate safety layer that flags potential hallucinations without sending proprietary data to external services.

### Target users

- AI product developers
- Enterprises handling confidential data
- Researchers building LLM‑driven assistants

## 2. Unique angle

Combines retrieval‑augmented verification (local Wikipedia snapshot + pgvector) with a self‑consistency score from multiple LLM sampled replies, delivering real‑time hallucination warnings while keeping all data on‑premise.

## 3. MVP features and acceptance criteria

### Hallucination Detection Endpoint

POST /detect receives a user prompt, returns LLM answer, a confidence score, and a hallucination flag.

- [ ] Returns JSON with fields: answer, confidence (0‑1), hallucination (bool)
- [ ] Confidence <0.6 when at least one factual claim is unsupported by the knowledge base
- [ ] Response latency ≤2 seconds for a 7B model on a consumer GPU

### Local Knowledge Base Loader

CLI tool to ingest a Wikipedia dump, embed passages with a sentence‑transformer, and store vectors in pgvector.

- [ ] Loads ≥10 k passages in ≤5 minutes
- [ ] Embeddings stored with metadata (title, url)
- [ ] Search returns top‑5 passages within 100 ms

### Self‑Consistency Sampler

Generates N=3 alternative answers and computes agreement metric.

- [ ] Agreement score correlates with confidence (higher agreement → higher confidence)
- [ ] Sampler can be toggled via request flag

## 4. Technology stack

- FastAPI (lightweight async API)
- Python 3.11
- Transformers (local Llama‑3 or Mistral model)
- LangChain (retrieval & prompting)
- Postgres + pgvector (dense vector store for knowledge base)
- Redis (caching recent queries)
- Docker (containerisation)
- GitHub Actions (CI/CD)
- OpenTelemetry (observability)

## 5. Architecture

A stateless FastAPI front‑end orchestrates three subsystems: (1) LLM inference, (2) Retrieval‑augmented verification, and (3) Consistency scoring. All components run in Docker containers and communicate via HTTP/Redis.

- **API Layer** — Validate requests, invoke pipeline, return unified JSON response
- **LLM Service** — Generate primary answer and N‑sampled alternatives using a local transformer model
- **Retrieval Engine** — Perform dense vector search against pgvector‑backed Wikipedia passages
- **Scoring Engine** — Compute self‑consistency, compare claims with retrieved evidence, output confidence

### Data flow

1. Client POST /detect → API Layer → parallel calls to LLM Service and Retrieval Engine → Scoring Engine aggregates results → API Layer returns response

## 6. Data model

- **passage:** id (uuid), title (text), url (text), content (text), embedding (float[] vector)
- **request_log:** id (uuid), timestamp (datetime), prompt (text), answer (text), confidence (float), hallucination (bool)

## 7. API contracts

| Method | Path | Purpose |
|---|---|---|
| POST | /detect | Detect hallucinations in a single user prompt |

## 8. Build milestones

### 1 — Foundations & Data Ingestion

- [ ] Set up repo, CI pipeline, Docker skeleton
- [ ] Create CLI to download & preprocess small Wikipedia dump (~10 k articles)
- [ ] Generate embeddings with sentence‑transformers and load into Postgres pgvector

**Deliverable:** Populated local knowledge base and reproducible Docker compose


## 9. Evaluation plan

Targets to test, not claimed results.

- **Hallucination Detection Accuracy:** Manually label 100 LLM answers (ground‑truth factuality) and compute F1 of the hallucination flag Target: F1 ≥ 0.75
- **Latency:** Average response time measured over 200 random prompts Target: ≤2 seconds
- **Confidence Calibration:** Reliability diagram / Expected Calibration Error (ECE) on the same 100 samples Target: ECE ≤ 0.10

## Testing checklist

- [ ] Unit tests for CLI loader, vector search, and scoring functions (pytest)
- [ ] Integration test: end‑to‑end POST /detect returns schema‑valid JSON
- [ ] Load test with locust: 50 concurrent users for 5 min

## Deployment and setup

- [ ] Build multi‑stage Docker image
- [ ] Deploy with Docker Compose on a single‑GPU VM (e.g., AWS g4dn.xlarge)
- [ ] Expose API via Traefik with TLS termination
- [ ] Add OpenTelemetry collector to ship traces to Grafana Cloud

## Prerequisites

- Python programming
- Basics of REST APIs
- Familiarity with LLM inference (HuggingFace)
- Understanding of vector similarity search

## Safety and privacy

- All data (knowledge base and user prompts) remain on‑premise; no external API calls
- Redis cache is configured with volatile‑ttl to avoid persistence of raw prompts
- Logs are anonymised (hash prompt before storage)

## Learning outcomes

- Design a privacy‑preserving LLM safety microservice
- Implement retrieval‑augmented generation with LangChain
- Apply self‑consistency sampling to estimate answer confidence
- Instrument services with OpenTelemetry

## Stretch goals

- Add multi‑modal verification (OCR text from uploaded images)
- Support dynamic knowledge base updates via a web UI
- Implement RL‑based policy to automatically rewrite hallucinated answers

## Resume bullet — add real results after implementation

Designed and delivered a privacy‑first LLM Hallucination Guard service that reduced factual errors by X% (measured on 200 test prompts) and achieved sub‑2‑second latency on consumer‑grade GPU.

## Interview questions

- How does self‑consistency improve hallucination detection?
- Why store the knowledge base locally instead of using a hosted vector DB?
- Explain the trade‑off between number of sampled answers and latency.
- How would you extend the system to detect PII leakage in LLM outputs?

## Recent research to explore

Fetched from arXiv on this run; leads for further reading, not proof of originality.

- [Text-to-Image Generative Modeling Without Language Pretraining](http://arxiv.org/abs/2610.26863v1) — updated 2026-10-19.
  - Modern text-to-image (T2I) systems use internet-scale language pretraining for text-conditioned image generation. We ask whether language pretraining is necessary for strong T2I generation. We introduce Halcyon, a family of early-fusion multimodal autoregressive models pretrained entirely from scrat

- [OpenVLHarness: Real World Visual Agentic Tool-Use with Multimodal Memory](http://arxiv.org/abs/2610.26860v1) — updated 2026-10-19.
  - Multimodal large language models (MLLMs) have made rapid progress on visual reasoning, yet many tasks require evidence that is difficult to obtain through internal reasoning alone: our controlled study on 22 benchmarks shows that simply increasing the inference budget of the base model yields only m

- [Can It Actually Work? Synthesizing Functional CAD Mechanisms](http://arxiv.org/abs/2610.26861v1) — updated 2026-10-19.
  - While LLM agents can generate visually plausible CAD assemblies, these designs often fail to fulfill their intended physical functions. We study functional CAD design, a setting where agents interpret underspecified requests to construct and iteratively revise mechanisms that satisfy functional requ

- [Reinforcement Learning with Visually Attributable On-Policy Self-Distillation](http://arxiv.org/abs/2610.26856v1) — updated 2026-10-19.
  - Multimodal reinforcement learning with verifiable rewards (RLVR) provides reliable task-level supervision, yet offers limited guidance for localizing errors in visual reasoning. On-policy self-distillation (OPSD) complements this supervision with dense token-level corrections from a privileged teach

- [VideoMaMa++: Temporally Consistent Video Matting via Preserve-and-Refine Token](http://arxiv.org/abs/2610.26857v1) — updated 2026-10-19.
  - Diffusion-based video matting has recently emerged as a leading approach, leveraging video diffusion priors from internet-scale pretraining to achieve strong zero-shot generalization from limited synthetic data. However, the heavy compute of these diffusion backbones limits inference to a short chun

- [Ropedia W0: Scaling Loco-Manipulation World Models across Embodiments with Human Experience](http://arxiv.org/abs/2610.26855v1) — updated 2026-10-19.
  - World models enable embodied agents to anticipate action consequences, yet jointly modeling locomotion and manipulation across diverse embodiments remains challenging due to heterogeneous action spaces and limited multimodal supervision. We present Ropedia W0, the first egocentric loco-manipulation 

- [InfiniDream: Open-Ended Photorealistic 3D Worlds Through Procedural Generation](http://arxiv.org/abs/2610.26853v1) — updated 2026-10-19.
  - Procedural generation plays a key role in synthetic data creation and game development, offering greater controllability, editability, and diversity than static mesh representations. However, VLM-based code generation often produces relatively simple 3D assets, while sophisticated photorealistic pro

- [CoopUQ: Robust Multi-Robot Social Navigation via Uncertainty-Aware Cooperative Forecasting](http://arxiv.org/abs/2610.26852v1) — updated 2026-10-19.
  - Reinforcement learning enables mobile robots to make fast and scalable navigation decisions in constrained human-shared environments. However, directly extending single-robot approaches to multi-robot settings often fails to ensure safety and efficiency, especially under occlusions and out-of-distri


## Hugging Face optimization

- Status: failed_keep_original
- Model: openai/gpt-oss-120b:fastest
- Note: Client error '402 Payment Required' for url 'https://router.huggingface.co/v1/chat/completions' (Request ID: Root=1-6ad71e1d-2f5cd82572c69bf53b2552a3;0d38a838-3718-4ed0-afeb-fbdc06a057f9)
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/402

You have no remaining credits. Purchase pre-paid credits to continue using Inference Providers. Alternatively, subscribe to PRO to get monthly included credits.

## Gemini design review

- Novelty score: 4/10
- Feasibility score: 6/10

### Overlap risks

- High overlap with established open-source guardrail frameworks such as NeMo Guardrails, Guardrails AI, and TruLens.
- Methodology strongly mirrors SelfCheckGPT (sampling multiple generations to measure consistency) combined with standard RAG claim verification.
- Abundant existing tutorials covering local pgvector + LangChain fact-checking pipelines.
### Suggested improvements

- Replace vanilla HuggingFace Transformers with an optimized inference engine like vLLM or TensorRT-LLM to make batched sampling viable.
- Relax the <=2 second latency SLA or replace full 7B generation sampling with a dedicated lightweight NLI model (e.g., DeBERTa-v3-small) evaluating decomposed atomic claims.
- Incorporate established hallucination evaluation benchmarks (e.g., HaluEval or FactCC) rather than relying solely on 100 manually annotated samples.
- Add an explicit claim extraction step (breaking answers into atomic propositions) before vector search to avoid noisy whole-text semantic similarity mismatches.

---
Generated with Groq / openai/gpt-oss-120b. Verify assumptions and report only measured results.

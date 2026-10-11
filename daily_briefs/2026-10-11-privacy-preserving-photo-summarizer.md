# Privacy-Preserving Personal Photo Summarizer

> A local‑only web service that clusters a user's personal photos, extracts event‑level descriptions, and generates concise natural‑language summaries (with optional audio) while guaranteeing zero data leaves the device.

**Date:** 2026-10-11 | **Category:** Computer Vision & Multimodal AI | **Difficulty:** Intermediate | **Effort:** 7 days

**Build-it-yourself brief:** this factory produces the specification, not source code.

## 1. Problem statement

People accumulate thousands of personal images but lack tools to quickly recall events or create shareable highlights; existing cloud‑based organizers trade convenience for privacy, exposing sensitive visual data to third‑party services.

### Target users

- Individuals with personal photo archives
- Privacy‑conscious users
- Travel bloggers
- Family album curators

## 2. Unique angle

All processing (visual embedding, clustering, and narrative generation) runs on‑device using open‑source models (CLIP + a 7B LLM via Ollama) with a local pgvector store, ensuring images never leave the user's machine.

## 3. MVP features and acceptance criteria

### Photo Ingestion & Embedding

User uploads a batch of JPEG/PNG files; each image is processed by CLIP and its embedding stored locally.

- [ ] Upload of ≥50 images succeeds without error
- [ ] Embedding vector (512‑dim) stored in PostgreSQL
- [ ] Processing time ≤0.3 s per image on a typical laptop

### Event Clustering

Embeddings are clustered into events using MiniBatchKMeans; each cluster is labeled with a representative thumbnail.

- [ ] Clusters count auto‑adjusts between 3‑10 for 50‑200 images
- [ ] Silhouette score ≥0.25 on the local test set
- [ ] User can view cluster thumbnails in UI

### Narrative Generation

For each cluster, the system prompts the local LLM to produce a 2‑3 sentence summary.

- [ ] Generated summary ≤80 characters
- [ ] No external API call logged (verified via network capture)
- [ ] Summaries pass a basic grammar check (>90% pass)

### Web Dashboard

React UI lets users browse clusters, read summaries, and optionally export a PDF storybook.

- [ ] Dashboard loads <2 s after backend start
- [ ] Exported PDF contains all images and generated text
- [ ] All UI actions work offline

## 4. Technology stack

- FastAPI – lightweight async API for image upload and retrieval
- React – responsive UI for drag‑drop photo upload and story browsing
- CLIP (open‑source ViT‑B/32) – extracts 512‑dim visual embeddings locally
- Sentence‑Transformers (all‑MiniLM‑L6‑v2) – optional text embedding for captions
- PostgreSQL + pgvector – persists embeddings and enables fast ANN search
- Ollama running Llama‑3‑8B – generates event narratives without external API calls
- Docker & Docker‑Compose – reproducible dev and production environments
- GitHub Actions – CI linting and test automation
- OpenTelemetry – end‑to‑end tracing for performance debugging
- DVC – versioning of sample photo datasets and model checkpoints

## 5. Architecture

A browser‑based React front‑end communicates with a FastAPI back‑end. The back‑end runs CLIP to embed photos, stores vectors in PostgreSQL/pgvector, clusters them, and calls a locally hosted LLM (via Ollama) to write narratives. All components run in Docker containers, isolated from the host network except for user‑initiated uploads.

- **FastAPI Service** — Handle file uploads, run CLIP, manage pgvector DB, trigger clustering and LLM calls
- **PostgreSQL+pgvector** — Persist raw metadata and high‑dimensional embeddings; provide ANN search for future extensions
- **Ollama LLM Container** — Serve Llama‑3‑8B for zero‑shot prompt‑based narrative generation
- **React SPA** — Provide drag‑and‑drop upload, cluster gallery, narrative view, and PDF export

### Data flow

1. User drops photos → FastAPI receives multipart request → CLIP computes embedding → Embedding saved to pgvector → MiniBatchKMeans runs on stored vectors → Cluster IDs written back → For each cluster FastAPI builds prompt → Ollama generates summary → Summary stored and returned to React → UI displays

## 6. Data model

- **photo:** id (uuid), filename (text), upload_ts (timestamp), embedding (vector[512]), cluster_id (int, nullable)
- **cluster:** id (int), centroid (vector[512]), representative_image_id (uuid), summary (text), created_ts (timestamp)

## 7. API contracts

| Method | Path | Purpose |
|---|---|---|
| POST | /api/photos/upload | Accept multi‑part image batch, compute embeddings, and store them |
| GET | /api/clusters | Return list of clusters with thumbnail URLs and summaries |
| GET | /api/cluster/{id} | Fetch detailed info for a specific cluster (image list, summary) |

## 8. Build milestones

### 1 — MVP Delivery

- [ ] Set up Docker‑Compose with FastAPI, PostgreSQL, Ollama
- [ ] Implement CLIP ingestion endpoint
- [ ] Create clustering script and integrate with API
- [ ] Add LLM prompt flow for summaries
- [ ] Build React upload & gallery UI
- [ ] Write unit tests for ingestion and clustering

**Deliverable:** A runnable Docker‑Compose stack where a user can upload photos and receive clustered event summaries via the web UI


## 9. Evaluation plan

Targets to test, not claimed results.

- **Clustering Silhouette Score:** sklearn.metrics.silhouette_score on the embedded vectors of the sample dataset Target: ≥0.25
- **Narrative Readability:** Automated grammar check (LanguageTool) pass rate Target: ≥90%
- **End‑to‑End Latency (upload + summary for 50 images):** Measure wall‑clock time from POST to GET /api/clusters Target: ≤20 seconds on a typical 2022 laptop

## Testing checklist

- [ ] Unit tests for CLIP embedding function (mock image inputs)
- [ ] Integration test: upload 10 images → verify DB rows count
- [ ] Clustering test: known synthetic embeddings produce expected number of clusters
- [ ] LLM mock test: intercept prompt and assert required placeholders are present
- [ ] Privacy test: capture network traffic during full run and assert no outbound connections

## Deployment and setup

- [ ] Docker‑Compose for local development (ports 8000 & 3000)
- [ ] Optional Kubernetes manifest for self‑hosted deployment on a private server
- [ ] Environment variables to toggle GPU usage for CLIP/Ollama
- [ ] CI pipeline builds Docker images and runs the full test suite on push

## Prerequisites

- Python 3.11+
- Basic knowledge of FastAPI and React
- Understanding of vector embeddings and K‑means clustering
- Familiarity with Docker

## Safety and privacy

- All image data and embeddings remain on the host filesystem; no cloud storage or API keys are used
- PostgreSQL data directory encrypted with filesystem‑level encryption (e.g., ecryptfs)
- Ollama runs in an isolated container with no network egress
- GDPR‑compatible delete endpoint (DELETE /api/photos/{id}) removes raw file and associated vectors
- OpenTelemetry logs are scrubbed of PII before export

## Learning outcomes

- Build and serve vision embeddings with CLIP
- Store and query high‑dimensional vectors in pgvector
- Integrate a local LLM for multimodal text generation
- Design a privacy‑first architecture that never streams user data
- Deploy a full‑stack app via Docker Compose

## Stretch goals

- Add video clip summarization (extract key frames, generate storyboard)
- Multi‑language summary generation via local mBART model
- Voice‑over generation using a local TTS model (e.g., Coqui TTS)
- User‑controlled privacy layers: on‑device differential privacy for embeddings

## Resume bullet — add real results after implementation

Implemented a privacy‑first multimodal photo summarizer that clustered 1,000+ personal images into events with 0.3 s per‑image processing, generated AI‑crafted narratives using a local 8B LLM, and delivered a Docker‑Compose deployment achieving <20 s end‑to‑end latency for full batch uploads.

## Interview questions

- How does pgvector enable fast similarity search compared to storing raw embeddings in a traditional table?
- Explain the trade‑offs of using MiniBatchKMeans vs. hierarchical clustering for on‑device photo grouping.
- What steps would you take if a user wanted to enable GPU acceleration for CLIP within the Docker setup?
- Describe how you ensured zero outbound network traffic during LLM inference.
- If the LLM occasionally hallucinates event details, how would you mitigate hallucinations in this privacy‑focused product?

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
- Note: Client error '402 Payment Required' for url 'https://router.huggingface.co/v1/chat/completions' (Request ID: Root=1-6acb5381-07186b86765a732a1ec54ddb;6472034e-6bee-464a-b974-ddc46a0f248a)
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/402

You have no remaining credits. Purchase pre-paid credits to continue using Inference Providers. Alternatively, subscribe to PRO to get monthly included credits.

## Gemini design review

- Novelty score: 4/10
- Feasibility score: 7/10

### Overlap risks

- Open-source self-hosted photo managers like Immich and PhotoPrism already provide local CLIP embedding indexing, semantic search, and clustering.
- Common GitHub boilerplate patterns pairing Ollama/Llama with local vector databases (pgvector/Chroma) and CLIP embeddings.
### Suggested improvements

- Replace text-only Llama-3-8B with a lightweight local Vision-Language Model (e.g., Moondream2 or LLaVA via Ollama) or add an explicit captioning model (e.g., BLIP), as CLIP embeddings cannot be directly read as prompts by a standard text LLM.
- Combine visual embeddings with EXIF metadata (timestamps, GPS coordinates) using spatio-temporal clustering (e.g., HDBSCAN) instead of purely visual KMeans for realistic event segmentation.
- Resolve the conflict in acceptance criteria between producing a '2-3 sentence summary' and enforcing 'summary <= 80 characters', which is too short for multiple sentences.
- Revise the 20-second end-to-end latency target for 50 images, as CPU-only inference for 50 CLIP passes plus multiple 8B LLM narrative completions on a standard laptop will typically exceed 60-90 seconds.

---
Generated with Groq / openai/gpt-oss-120b. Verify assumptions and report only measured results.

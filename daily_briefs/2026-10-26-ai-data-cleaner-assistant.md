# AI-Powered Automated Data Cleaning Assistant

> A privacy‑first web service that lets users upload tabular data, automatically generates a reproducible cleaning plan using LLM reasoning, and applies the transformations with full provenance tracking.

**Date:** 2026-10-26 | **Category:** AI Automation and Tool Use | **Difficulty:** Intermediate | **Effort:** 7 days

**Build-it-yourself brief:** this factory produces the specification, not source code.

## 1. Problem statement

Business analysts and data scientists waste up to 80% of their time manually fixing dirty CSV/Excel files (missing values, inconsistent formats, outliers). Existing tools either require coding or offer black‑box imputation without explainability, leading to low trust and poor reproducibility.

### Target users

- Data analysts in SMEs
- Junior data scientists
- Product managers needing quick clean datasets

## 2. Unique angle

Combines LLM‑driven natural‑language cleaning suggestions with a deterministic pandas execution engine, stores each step in a version‑controlled DVC repo, and returns a detailed audit log so users can review, accept, or modify each operation before it is applied.

## 3. MVP features and acceptance criteria

### File Upload & Schema Inference

User uploads CSV/Excel; service extracts column types and sample rows

- [ ] Upload succeeds for files ≤5 MB
- [ ] Schema JSON returned within 2 s
- [ ] Supported formats: .csv, .xlsx

### LLM‑Generated Cleaning Plan

LLM proposes a sequence of cleaning actions (e.g., fill missing, trim whitespace, normalize dates) expressed as JSON

- [ ] Plan contains ≥3 actionable steps for a typical messy dataset
- [ ] Each step includes description, pandas code snippet, and confidence score

### Interactive Review & Execution

Frontend (or Swagger UI) shows plan; user can approve, edit, or reject steps; approved steps are executed on the dataframe

- [ ] Approved plan produces cleaned file without errors
- [ ] Execution time ≤5 s for 100 k rows
- [ ] Generated audit log lists original vs. transformed values

### Provenance & Versioning

Every accepted plan is stored in a DVC repo with metadata and version tag

- [ ] DVC commit created for each run
- [ ] User can retrieve previous version via API

## 4. Technology stack

- FastAPI (lightweight async API)
- LangChain (orchestrates LLM prompts and tool calls)
- OpenAI/Groq LLM (text generation)
- pandas (data manipulation)
- pgvector+PostgreSQL (vector store for example datasets)
- DVC (data versioning & reproducibility)
- Docker (containerization)
- GitHub Actions (CI/CD)

## 5. Architecture

A FastAPI gateway receives files, triggers a LangChain workflow that calls an LLM to draft a cleaning plan, presents the plan to the user, and upon approval runs deterministic pandas transformations. Results and provenance are persisted in PostgreSQL (metadata) and DVC (data versions).

- **API Layer** — HTTP endpoints, authentication, file handling
- **LLM Orchestrator** — Prompt templates, tool calls, plan generation via LangChain
- **Execution Engine** — Validate and run pandas code in a sandboxed subprocess
- **Metadata Store** — PostgreSQL with pgvector for storing dataset embeddings and audit logs
- **Version Control Service** — DVC repo mounted as a volume, handles commits and retrieval

### Data flow

1. User POST /upload → API stores raw file → Orchestrator extracts schema → LLM returns plan JSON → API returns plan → User POST /execute with approval → Execution Engine applies transformations → Clean file stored → DVC commit → Audit log written to PostgreSQL

## 6. Data model

- **Dataset:** id (uuid), user_id (uuid), filename (text), schema (json), embedding (vector), created_at (timestamp)
- **CleaningPlan:** id (uuid), dataset_id (uuid), plan_json (json), status (enum: draft|approved|executed), created_at, executed_at
- **AuditLog:** id (uuid), plan_id (uuid), step_index (int), operation (text), pandas_code (text), rows_modified (int), timestamp

## 7. API contracts

| Method | Path | Purpose |
|---|---|---|
| POST | /upload | Receive raw CSV/Excel, store temporarily, and return inferred schema |
| GET | /plan/{dataset_id} | Retrieve the latest LLM‑generated cleaning plan for a dataset |
| POST | /plan/{dataset_id}/execute | Accept user‑approved plan, run transformations, store cleaned file and audit log |
| GET | /audit/{plan_id} | Fetch detailed step‑by‑step provenance for a completed cleaning run |

## 8. Build milestones

### 1 — Foundations & File Service

- [ ] Set up FastAPI project skeleton
- [ ] Implement secure file upload endpoint
- [ ] Add schema inference using pandas‑profiling

**Deliverable:** Working /upload endpoint returning JSON schema

### 2 — LLM Orchestration

- [ ] Create LangChain prompt templates
- [ ] Integrate Groq/OpenAI API
- [ ] Generate cleaning plan JSON
- [ ] Store plan in PostgreSQL

**Deliverable:** GET /plan returns LLM‑generated actions

### 3 — Review UI & Execution Engine

- [ ] Build minimal Swagger UI for plan approval
- [ ] Sandbox pandas execution (subprocess with timeout)
- [ ] Persist cleaned file and DVC commit

**Deliverable:** POST /plan/.../execute produces cleaned dataset and version tag

### 4 — Provenance & Testing

- [ ] Design audit log schema
- [ ] Implement audit endpoint
- [ ] Write unit & integration tests (pytest)

**Deliverable:** GET /audit returns full step log

### 5 — CI/CD & Deployment

- [ ] Dockerize application
- [ ] Create GitHub Actions workflow (lint, test, build)
- [ ] Deploy to Render/ Railway (free tier)

**Deliverable:** Live demo URL with HTTPS


## 9. Evaluation plan

Targets to test, not claimed results.

- **Plan Generation Accuracy:** Human evaluator rates relevance of each suggested step on a 5‑point Likert scale across 10 sample datasets Target: ≥4.0 average
- **Execution Success Rate:** Percentage of approved plans that run without pandas errors Target: ≥95%
- **User Approval Time:** Average time from plan receipt to user approval in the UI Target: ≤30 seconds

## Testing checklist

- [ ] Unit tests for each FastAPI endpoint (coverage ≥ 90%)
- [ ] Integration test that uploads a synthetic dirty CSV, runs full pipeline, and checks that audit log matches expected transformations
- [ ] Security test: verify uploaded files are scanned for malicious content (e.g., CSV injection) and size limits enforced

## Deployment and setup

- [ ] Docker image built with multi‑stage Dockerfile
- [ ] Push to Docker Hub (private)
- [ ] Deploy on Railway with PostgreSQL addon and persistent volume for DVC repo
- [ ] Enable HTTPS via Railway’s automatic certs

## Prerequisites

- Python 3.10+
- Basic FastAPI knowledge
- Familiarity with pandas
- Understanding of prompt engineering

## Safety and privacy

- All file processing occurs in an isolated container with no network egress
- Raw files are deleted after successful DVC commit
- No user data is sent to third‑party services except the LLM call (only text prompts)
- GDPR‑compatible opt‑out endpoint to delete user datasets

## Learning outcomes

- Design LLM‑to‑tool pipelines with LangChain
- Implement reproducible data pipelines with DVC
- Expose ML‑inspired services via FastAPI
- Apply security best practices for file uploads

## Stretch goals

- Add multi‑modal support: ingest JSON or Parquet files
- Enable custom LLM fine‑tuning on organization‑specific cleaning policies
- Integrate with Streamlit front‑end for richer interactive editing
- Provide a CLI wrapper for batch cleaning via Docker

## Resume bullet — add real results after implementation

Developed an end‑to‑end AI‑driven data cleaning SaaS that reduced manual preprocessing time by ~70%, implemented reproducible versioning with DVC, and achieved 95%+ execution success across 50+ real‑world datasets

## Interview questions

- How does LangChain enable LLM‑to‑tool interaction in this project?
- Explain how DVC ensures reproducibility of data transformations and how you integrated it with a web service.
- What security measures did you put in place for handling user‑uploaded files?
- Describe a failure mode when the LLM suggests invalid pandas code and how your system mitigates it.

## Recent research to explore

Fetched from arXiv on this run; leads for further reading, not proof of originality.

- [The Language of Instruction: Genre and Generative AI](http://arxiv.org/abs/2610.32982v1) — updated 2026-10-23.
  - This article argues that instruction-fine-tuned language models should be understood as implementing a genre, what is proposed as the instructional-conversational genre. This genre is an amalgamation of discursive language from prior conversations between generative models and humans recursively run

- [SceneBloom: Agentic Indoor Environment Generation with Realistic and Diverse Layouts for Embodied Learning](http://arxiv.org/abs/2610.32978v1) — updated 2026-10-23.
  - Training generalizable embodied agents requires realistic, varied, and simulation-ready indoor environments. Language-guided methods support semantic planning and object-level reasoning, but precise spatial grounding remains difficult. Visual generative models offer rich priors over plausible arrang

- [UniAction: Unified Action Conditioning for World Models](http://arxiv.org/abs/2610.32977v1) — updated 2026-10-23.
  - Actions that condition world models are highly heterogeneous, and thus existing action-conditioned world models are typically built for individual action types, fragmenting already limited action-annotated data across separate models. We introduce UniAction, a unified action-conditioning framework t

- [FlexGlue: Sparse-to-Dense Feature Matching and Visual Disambiguation](http://arxiv.org/abs/2610.32976v1) — updated 2026-10-23.
  - To estimate correspondences across images, existing approaches match either sparse interest points, which is highly efficient but limited by repeatability, or dense pixel grids, which is robust but expensive. Furthermore, these approaches are trained with only matching pairs and thus often fail to r

- [RobustRLlib: A Unified Library and Benchmark for Robust Reinforcement Learning Algorithms](http://arxiv.org/abs/2610.32971v1) — updated 2026-10-23.
  - Robust reinforcement learning (RL) is critical for reliable real-world deployment, where policies may fail under diverse shifts and disruptions. Existing robust RL algorithms offer a rich set of mechanisms and principles, yet two major barriers limit their broader potential: limited algorithm reusab

- [DexPort: A Hand-Held Skill Interface for Dexterous Hand Data Collection](http://arxiv.org/abs/2610.32969v1) — updated 2026-10-23.
  - Collecting high-quality demonstrations remains a central bottleneck for learning dexterous manipulation. Teleoperation records executable robot actions, but it requires a complete robot setup and places the burden of coordinating many finger joints on the operator. Human demonstrations are easier to

- [MiD-VLM: Detecting and Grounding Global Semantic Misinformation in Image-Caption Pairs](http://arxiv.org/abs/2610.32967v1) — updated 2026-10-23.
  - Semantic misinformation can arise when an authentic image is paired with a caption that changes or distorts its narrative. Because the image itself may contain no visible signs of manipulation, methods designed to detect pixel-level artifacts can miss these misleading image-caption pairs. We study t

- [ViT-H: Generative Video-To-Humanoid Control with Motion Tracking Feedback](http://arxiv.org/abs/2610.32966v1) — updated 2026-10-23.
  - Learning humanoid control from monocular human videos offers a scalable way to acquire diverse whole-body behaviors. Yet, existing reconstruction-retargeting-tracking pipelines are limited in system-level scalability by separately optimized intermediate stages and cannot directly optimize reference 


## Hugging Face optimization

- Status: failed_keep_original
- Model: openai/gpt-oss-120b:fastest
- Note: Client error '402 Payment Required' for url 'https://router.huggingface.co/v1/chat/completions' (Request ID: Root=1-6adf09a6-28c52c1c1d825d410f4c6777;b83c8ef0-e0a3-4931-82e6-9277306f19a1)
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/402

You have no remaining credits. Purchase pre-paid credits to continue using Inference Providers. Alternatively, subscribe to PRO to get monthly included credits.

---
Generated with Groq / openai/gpt-oss-120b. Verify assumptions and report only measured results.

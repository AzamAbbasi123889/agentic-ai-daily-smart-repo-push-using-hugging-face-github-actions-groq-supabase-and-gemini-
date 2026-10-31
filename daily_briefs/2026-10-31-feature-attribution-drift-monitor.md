# Continuous Feature Attribution & Drift Monitoring Platform

> A FastAPI‑based SaaS that ingests production predictions, records per‑instance SHAP explanations, detects drift in feature importance over time, visualizes trends, and alerts engineers with root‑cause suggestions. The MVP stores data in Postgres + pgvector, uses MLflow for model versioning, and runs in Docker for easy deployment.

**Date:** 2026-10-31 | **Category:** MLOps and Model Monitoring | **Difficulty:** Intermediate | **Effort:** 7 days

**Build-it-yourself brief:** this factory produces the specification, not source code.

## 1. Problem statement

Data scientists and ML engineers often monitor model performance but lack visibility into how feature contributions evolve in production, making it hard to diagnose degradation caused by shifting data distributions. Without systematic attribution tracking, silent failures may go unnoticed until business impact occurs.

### Target users

- ML engineers
- Data scientists
- DevOps teams
- Product managers

## 2. Unique angle

Combines real‑time per‑prediction SHAP attribution storage with statistical drift detection on the attribution distribution, automatically surfacing which features are losing predictive power and recommending remediation actions—beyond classic label/feature drift monitors.

## 3. MVP features and acceptance criteria

### Prediction Ingestion API

Endpoint that receives model ID, input features, and predicted label; computes SHAP values on the fly and stores them.

- [ ] POST /predict returns 200 with prediction ID
- [ ] SHAP vector persisted in DB
- [ ] Response time <200 ms for models <1 M parameters

### Attribution Drift Detector

Nightly job that compares current attribution distribution against baseline using Wasserstein distance and flags significant drift.

- [ ] Runs as scheduled Docker container
- [ ] Generates an alert when distance >0.1
- [ ] Stores drift metrics in DB

### Dashboard & Alerting

Grafana dashboards showing feature importance trends and email alerts for drift events.

- [ ] Dashboard updates within 5 min of new data
- [ ] Email sent with correct model & feature details
- [ ] Access control via simple token

## 4. Technology stack

- FastAPI (lightweight async API)
- PostgreSQL with pgvector (persistent storage of embeddings & SHAP vectors)
- MLflow (model registry & versioning)
- Redis (caching recent predictions)
- Docker (containerization)
- GitHub Actions (CI/CD)
- Grafana (dashboard visualizations)
- scikit‑learn & shap (attribution computation)

## 5. Architecture

A modular MLOps service where FastAPI handles ingestion, a background worker computes and stores SHAP vectors, a scheduled drift job analyses stored vectors, and Grafana visualizes results. All components communicate via Redis and PostgreSQL and are orchestrated with Docker Compose.

- **API Layer** — Expose /predict and admin endpoints; validate payloads; enqueue jobs
- **Attribution Worker** — Compute SHAP values using the registered model artifact from MLflow
- **Drift Scheduler** — Run nightly statistical tests on stored attribution vectors
- **Storage Engine** — Persist predictions, SHAP vectors, drift metrics, and alerts
- **Alert Service** — Send email/webhook notifications
- **Dashboard** — 
- **Component** — Render time‑series of feature importance and drift scores

### Data flow

1. Client → POST /predict → API Layer → Redis queue → Attribution Worker → PostgreSQL (predictions+SHAP)
2. Drift Scheduler reads SHAP from DB → computes distance → stores drift metric → triggers Alert Service → Email
3. Grafana queries PostgreSQL for trend visualizations

## 6. Data model

- **Model:** model_id (PK), mlflow_run_id, name, description, created_at
- **Prediction:** prediction_id (PK), model_id (FK), input_vector (float[] ), predicted_label, timestamp
- **AttributionSnapshot:** snapshot_id (PK), prediction_id (FK), shap_vector (float[] ), vector_embedding (vector), timestamp
- **DriftMetric:** metric_id (PK), model_id (FK), date, wasserstein_distance, p_value
- **Alert:** alert_id (PK), model_id (FK), metric_id (FK), triggered_at, message, resolved (bool)

## 7. API contracts

| Method | Path | Purpose |
|---|---|---|
| POST | /predict | Ingest a new prediction, compute SHAP, store results |
| GET | /models/{model_id}/drift | Retrieve latest drift metrics for a model |
| GET | /dashboard | Redirect to Grafana dashboard (optional) |

## 8. Build milestones

### 1 — Setup Foundations

- [ ] Initialize Git repo, Dockerfile, docker‑compose
- [ ] Configure PostgreSQL + pgvector schema
- [ ] Deploy MLflow server

**Deliverable:** Running containers with DB and MLflow

### 2 — Ingestion & Attribution

- [ ] Implement /predict endpoint
- [ ] Integrate shap library with model loading from MLflow
- [ ] Persist predictions & SHAP vectors

**Deliverable:** API that stores SHAP for each request

### 3 — Drift Detection & Alerts

- [ ] Create nightly drift job (Docker entrypoint)
- [ ] Implement Wasserstein distance calculation
- [ ] Configure email alert via SMTP

**Deliverable:** Automated drift alerts

### 4 — Dashboard & Polish

- [ ] Connect Grafana to PostgreSQL
- [ ] Build feature‑importance time series panels
- [ ] Write CI/CD workflow

**Deliverable:** End‑to‑end MVP with UI


## 9. Evaluation plan

Targets to test, not claimed results.

- **Mean latency of /predict:** Locust load test with 100 concurrent requests Target: <200 ms
- **False‑positive drift alert rate:** Simulate stable attribution data for 30 days Target: <5 %
- **Detection latency for real drift:** Inject synthetic attribution shift and measure alert time Target: <6 h

## Testing checklist

- [ ] Unit tests for API validation (pytest)
- [ ] Integration tests for DB persistence
- [ ] Mock shap computation to test worker flow
- [ ] End‑to‑end test: submit prediction → verify SHAP stored → run drift job → verify alert

## Deployment and setup

- [ ] Docker Compose for local development
- [ ] GitHub Actions builds multi‑arch image and pushes to Docker Hub
- [ ] Deploy to Render/ Railway (free tier) with PostgreSQL add‑on
- [ ] Configure environment variables for MLflow & SMTP

## Prerequisites

- Python 3.10+
- Basic knowledge of FastAPI
- Understanding of SHAP/feature attribution
- Familiarity with PostgreSQL and Docker

## Safety and privacy

- Only store numeric feature vectors – no raw PII
- Encrypt DB connections via TLS
- Provide API token authentication
- Log retention limited to 90 days

## Learning outcomes

- Design and implement a data pipeline for model monitoring
- Apply SHAP to generate per‑instance explanations
- Detect statistical drift on high‑dimensional vectors
- Build alerting logic and dashboards
- Deploy a full‑stack MLOps service with CI/CD

## Stretch goals

- Support multi‑model ensembles with combined attribution
- Add causal drift analysis (using DoWhy)
- Integrate Slack webhook for alerts
- Provide automated remediation suggestions (re‑train trigger)

## Resume bullet — add real results after implementation

Designed and delivered a full‑stack MLOps platform that logged per‑prediction SHAP explanations for 10 K daily predictions, detected attribution drift with >90 % precision, and reduced mean time to detection from 48 h to 6 h.

## Interview questions

- How does monitoring feature attributions complement traditional performance monitoring?
- Explain the choice of Wasserstein distance for high‑dimensional attribution drift detection.
- What are the trade‑offs of computing SHAP online vs. offline batch?
- How would you scale this system to handle millions of predictions per day?
- Describe how you ensure privacy when storing input features and SHAP vectors.

## Recent research to explore

Fetched from arXiv on this run; leads for further reading, not proof of originality.

- [Elucidating the Design Space of LM Data Attribution](http://arxiv.org/abs/2610.40655v1) — updated 2026-10-29.
  - Data attribution methods for Language Models (LMs) are typically evaluated using downstream tasks like fact retrieval. However, existing evaluations vary multiple dataset properties simultaneously, making it impossible to isolate exactly why an attribution algorithm fails. To diagnose these failures

- [Propose-Filter-Release: Scaling Noise to Typical Sensitivity via Private Filtering](http://arxiv.org/abs/2610.40654v1) — updated 2026-10-29.
  - An estimator can be accurate and stable on typical data, yet sensitive to a few possible records. Differentially private mechanisms commonly scale their noise to the worst-case influence of a single record, which lets these records dictate the noise even when the remaining data would allow far less.

- [Micro-Edits: Computational Support for Fine-Scale Edits in Film](http://arxiv.org/abs/2610.40653v1) — updated 2026-10-29.
  - In film editing, every frame matters. While macro, content-level edits shape the high-level narrative of a film, small local edits often control timing and direct visual attention. For example, editors can adjust the precise timing of clips to control the length of a meaningful silence, or cut to sh

- [Rethinking Neural Thickets Without Weight Perturbations](http://arxiv.org/abs/2610.40649v1) — updated 2026-10-29.
  - The Neural Thickets hypothesis posits that pretrained language models lie in dense neighborhoods of task-specific experts in weight space, which random Gaussian perturbations can uncover. We reproduce the reported gains, but show that they do not require this geometric explanation. Perturbing a sing

- [Read, Allocate, Route: Role-Coupled Tokenization for Pixel-Space Generative Transformers](http://arxiv.org/abs/2610.40647v1) — updated 2026-10-29.
  - Pixel-space generative Transformers typically use one token per image patch, so capturing finer detail requires more tokens and makes global attention increasingly expensive. We observe that finer detail does not necessarily require more global communication: low-frequency structure benefits from gl

- [Adaptive Scenario Generation for KL-DRO Around a Learned Density Model](http://arxiv.org/abs/2610.40644v1) — updated 2026-10-29.
  - Distributionally robust optimization (DRO) hedges data-driven two-stage stochastic programs against error in the distribution estimated from a finite record, and standard ambiguity sets differ in how they treat realizations absent from that record. A divergence ball around the empirical distribution

- [Luggage re-identification: A study of strategies towards a real-world application](http://arxiv.org/abs/2610.40643v1) — updated 2026-10-29.
  - Luggage re-identification (ReID) is a critical task in video surveillance for forensics, security or border management (suspicious or abandoned luggage recognition), as well as luggage management (lost luggage recovery). It enables the association of observations of the same luggage across disjoint 

- [From extreme weather to agricultural consequences with agentic AI](http://arxiv.org/abs/2610.40641v1) — updated 2026-10-29.
  - Extreme weather is forecast days ahead, yet its consequences for agriculture remain hard to predict: a forecast says where a storm will strike, not which crops will suffer or how much is at risk, and the records that could tell span many sources. We present WxCrop, the first agent that judges agricu


## Hugging Face optimization

- Status: failed_keep_original
- Model: openai/gpt-oss-120b:fastest
- Note: Client error '402 Payment Required' for url 'https://router.huggingface.co/v1/chat/completions' (Request ID: Root=1-6ae5aade-388d7a0a2ff99d164dbd3550;988e7cd3-a313-45e7-b918-5b45638b5ede)
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/402

You have no remaining credits. Purchase pre-paid credits to continue using Inference Providers. Alternatively, subscribe to PRO to get monthly included credits.

## Gemini design review

- Novelty score: 5/10
- Feasibility score: 7/10

### Overlap risks

- Commercial MLOps and observability platforms like Arize AI, Fiddler AI, and Evidently AI already provide production SHAP attribution tracking, concept drift, and data drift monitoring out of the box.
- Open-source packages like Evidently AI and Alibi Detect already have pre-built modules for feature importance drift and statistical hypothesis testing.
### Suggested improvements

- Decouple SHAP computation completely from the synchronous API path: Computing SHAP values on-the-fly inside `POST /predict` under 200ms is unrealistic for non-linear models or models with more than a few features. Use background sampling or fast TreeSHAP exclusively in an async task queue.
- Clarify the use case of `pgvector`: explain whether attribution vectors are queried via approximate nearest neighbor (ANN) for clustering failure modes or outlier discovery, as standard 1D Wasserstein drift does not require vector embeddings.
- Introduce multidimensional attribution drift techniques (e.g., Maximum Mean Discrepancy or attribution space clustering) rather than running separate 1D Wasserstein distance per feature, which misses inter-feature attribution shifts.

---
Generated with Groq / openai/gpt-oss-120b. Verify assumptions and report only measured results.

# CropYield Forecast & Explainability Service

> An end‑to‑end web service that predicts regional crop yields using weather time‑series, soil stats and low‑resolution satellite imagery, then generates LLM‑driven natural‑language explanations of the drivers behind the forecast.

**Date:** 2026-10-30 | **Category:** Applied ML and Forecasting | **Difficulty:** Intermediate | **Effort:** 5 days

**Build-it-yourself brief:** this factory produces the specification, not source code.

## 1. Problem statement

Farmers, agronomists and agricultural policy makers need short‑term yield forecasts to plan inputs and logistics, but existing tools either provide coarse national averages or require expensive proprietary data and lack explainability.

### Target users

- Small‑holder farmers
- Agricultural extension services
- Agri‑tech startups
- Policy analysts

## 2. Unique angle

Combines a lightweight Temporal Fusion Transformer with an LLM that translates model attention and feature importance into a concise, human‑readable narrative, all built on fully public datasets.

## 3. MVP features and acceptance criteria

### Yield Forecast API

Accepts region ID and target month, returns point forecast, 95% confidence interval and JSON payload

- [ ] POST /forecast returns HTTP 200
- [ ] MAE on held‑out test set <= 15% of average yield
- [ ] Response includes fields: forecast, lower_ci, upper_ci, explanation

### LLM Explanation

Generates a 3‑bullet natural‑language summary of the main drivers (weather, soil, satellite NDVI)

- [ ] Explanation length 2‑4 sentences
- [ ] Mentions at least two weather variables and one satellite metric

### Simple Dashboard

React page to select region/month and display forecast + explanation

- [ ] UI shows numeric forecast, confidence band and explanation
- [ ] No client‑side errors in Chrome console

## 4. Technology stack

- FastAPI (lightweight, async API)
- React (interactive dashboard)
- PyTorch (TFT model)
- HuggingFace Transformers (explanation LLM)
- PostgreSQL + pgvector (store weather embeddings)
- DVC (data versioning)
- Docker & Docker‑Compose (reproducible dev/prod)
- GitHub Actions (CI/CD)

## 5. Architecture

Data ingestion → preprocessing → model training (offline) → inference service (FastAPI) → explanation service (LLM) → storage (Postgres) → React UI

- **Ingestion Pipeline** — Pull daily weather from Open-Meteo, soil data from FAO, and Sentinel‑2 NDVI tiles; store raw files in ./data

### Data flow

1. Scheduler pulls raw data → Preprocess → Insert into Postgres
2. Training notebook reads from Postgres → trains model → registers model artifact
3. API loads model → receives request → queries recent weather/NDVI → predicts → sends features to LLM → returns combined JSON
4. Frontend calls API → displays results

## 6. Data model

- **Region:** region_id (PK), name, latitude, longitude, area_km2
- **WeatherObservation:** obs_id (PK), region_id (FK), date, temp_avg, precip_mm, solar_rad, wind_speed
- **SatelliteNDVI:** ndvi_id (PK), region_id (FK), date, ndvi_mean
- **YieldRecord:** yield_id (PK), region_id (FK), year, crop_type, yield_tons_per_ha
- **Forecast:** forecast_id (PK), region_id (FK), target_month, forecast_value, lower_ci, upper_ci, explanation, created_at

## 7. API contracts

| Method | Path | Purpose |
|---|---|---|
| GET | /regions | List available regions for selection |
| POST | /forecast | Compute yield forecast and explanation for a region and month |
| GET | /forecast/{forecast_id} | Retrieve a previously generated forecast record |

## 8. Build milestones

### 1 — Data & Model Foundations

- [ ] Set up repo, Docker, CI
- [ ] Ingest a 3‑month sample of weather, soil, NDVI for 5 regions
- [ ] Implement preprocessing scripts
- [ ] Train a baseline TFT on DVC tracked data

**Deliverable:** Trained model artifact and reproducible pipeline


## 9. Evaluation plan

Targets to test, not claimed results.

- **Mean Absolute Error (MAE):** Compute on held‑out 20% of YieldRecord Target: <= 0.15 * average yield

## Testing checklist

- [ ] Unit tests for preprocessing functions (pytest)
- [ ] Model inference test with dummy input (assert shape)
- [ ] API contract tests using FastAPI TestClient (status codes, schema)
- [ ] End‑to‑end test: POST /forecast → verify JSON contains all fields
- [ ] React component snapshot tests

## Deployment and setup

- [ ] Dockerfile for backend, Dockerfile for frontend
- [ ] docker‑compose.yml orchestrates postgres, api, frontend
- [ ] CI workflow builds images, runs tests, pushes to Docker Hub
- [ ] Deploy on Fly.io (free tier) or Render with automatic HTTPS

## Prerequisites

- Python 3.10+
- Basic knowledge of time‑series forecasting (ARIMA/TFT)
- Familiarity with LLM prompting
- SQL and REST basics

## Safety and privacy

- All data sources are public (Open‑Meteo, FAO Soil, Sentinel‑2) – no PII
- Store only region IDs, no farmer‑level identifiers
- LLM runs locally; no external API calls, ensuring data never leaves host
- Rate‑limit /forecast to prevent abuse

## Learning outcomes

- Design and train a multi‑modal time‑series model
- Integrate vector similarity search with pgvector
- Prompt‑engineer LLMs for model explainability
- Deploy a full‑stack ML service with CI/CD

## Stretch goals

- Add real‑time weather pull for next‑day updates
- Support multi‑crop forecasts (wheat, corn, rice)
- Interactive what‑if scenario UI (e.g., +10 mm rain)
- Ensemble of TFT + Prophet for robustness

## Resume bullet — add real results after implementation

Built a full‑stack crop‑yield forecasting service that achieved MAE < 15% on a public dataset and delivered LLM‑generated explanations, deployed with Docker‑Compose on Fly.io and automated via GitHub Actions

## Interview questions

- How did you choose Temporal Fusion Transformer over ARIMA or Prophet for this task?
- Explain how you transformed raw satellite NDVI tiles into features usable by the TFT.
- Describe the prompt engineering technique you used to turn model importances into a natural‑language explanation.
- What steps did you take to ensure reproducibility of data and model artifacts?
- How would you extend the system to handle multi‑regional hierarchical forecasting?

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
- Note: Client error '402 Payment Required' for url 'https://router.huggingface.co/v1/chat/completions' (Request ID: Root=1-6ae45b77-6f454e5d3b681615267fcc9d;4884bb64-79f3-4b78-b6c8-d0caea76722b)
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/402

You have no remaining credits. Purchase pre-paid credits to continue using Inference Providers. Alternatively, subscribe to PRO to get monthly included credits.

---
Generated with Groq / openai/gpt-oss-120b. Verify assumptions and report only measured results.

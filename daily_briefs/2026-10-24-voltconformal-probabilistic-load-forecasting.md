# VoltConformal: Conformal Probabilistic Net-Load Forecasting and Microgrid Energy Arbitrage Engine

> VoltConformal is a production-grade probabilistic net-load forecasting and battery dispatch engine for decentralized solar-plus-storage microgrids. It combines gradient-boosted quantile regressors with inductive split-conformal prediction to output rigorous, finite-sample coverage intervals for volatile renewable generation and net load. An integrated linear programming dispatch solver uses these risk-bounded forecasts to execute cost-optimal, battery-degradation-aware energy arbitrage under dynamic time-of-use electricity tariffs.

**Date:** 2026-10-24 | **Category:** Applied ML and Forecasting | **Difficulty:** Advanced | **Effort:** 7 days

**Build-it-yourself brief:** this factory produces the specification, not source code.

## 1. Problem statement

Decentralized microgrids pairing rooftop solar photovoltaic (PV) systems with battery energy storage systems (BESS) face extreme net-load volatility from cloud transient events and uncoordinated customer demands. Traditional point forecasting models (e.g., standard MSE-minimized ARIMA or neural networks) fail to quantify downside tail risks, leading to severe battery depletion during unexpected peak price surges or grid feed-in curtailment penalties. Existing open tools either provide uncalibrated point forecasts or decouple forecasting from downstream battery dispatch optimization.

### Target users

- Microgrid operators and community solar portfolio managers
- Commercial and industrial facility energy managers optimizing peak demand charges
- Energy tech developers and grid integration ML engineers
- Applied ML researchers in probabilistic time series and decision-focused forecasting

## 2. Unique angle

Unlike traditional black-box forecasting tools or basic time series regressors, VoltConformal couples distribution-free inductive conformal prediction intervals (guaranteeing exact statistical coverage without Gaussian distribution assumptions) with hierarchical reconciliation (MinT algorithm) across individual meters and grid aggregate transformers. Furthermore, it embeds a linear programming battery dispatch solver directly into the forecasting loop to evaluate decisions under expected worst-case quantiles.

## 3. MVP features and acceptance criteria

### Multi-Horizon Quantile Net-Load Forecaster

Ingests historical 15-minute resolution consumption and solar generation telemetry, producing 24-hour forward forecasts across P10, P50, and P90 quantiles.

- [ ] Inference latency under 150ms for a 96-step forward horizon (24 hours at 15-min intervals)
- [ ] Pinball loss across test holdout is at least 12% lower than a seasonal persistence baseline
- [ ] Empirical quantile calibration within 2.5% deviation from nominal quantiles (e.g., P90 captures between 87.5% and 92.5% of observations)

### Conformal Uncertainty Interval Calibrator

Applies inductive split-conformal calibration on a rolling calibration set to deliver bounded upper and lower net-load bands with provable marginal coverage.

- [ ] User can specify error rate alpha between 0.05 and 0.20 via API parameter
- [ ] Maintains empirical prediction interval coverage >= 1 - alpha on non-stationary test windows
- [ ] Outputs adaptive prediction band widths that naturally widen during cloud transient periods and narrow at night

### Hierarchical Aggregation Reconciler

Enforces spatial coherence across microgrid feeder hierarchies (e.g., individual households summing to neighborhood distribution transformer).

- [ ] Reconciles bottom-up meter forecasts to aggregate transformer forecasts with zero summation residual
- [ ] Mean Absolute Scaled Error (MASE) of reconciled forecasts improves or stays within 1% of independent transformer-level forecasts

### Risk-Bounded Battery Arbitrage Optimizer

Solves an hourly/quarter-hourly linear program to determine optimal charge, discharge, and grid export schedules against time-of-use (TOU) tariffs under P90 peak demand risk.

- [ ] BESS State of Charge (SoC) remains strictly bounded between 15% and 95% at all time steps
- [ ] Generates feasible schedule in less than 300ms using PuLP/CBC solver
- [ ] Demonstrates documented electric bill cost savings exceeding 18% compared to unmanaged heuristic charging in backtests

## 4. Technology stack

- Python 3.11 for primary model training, conformal calibration, and orchestration
- FastAPI for high-throughput, low-latency prediction and dispatch REST API endpoints
- LightGBM with custom pinball/quantile loss objectives for multi-horizon quantile regression (P10, P50, P90)
- MAPIE (Model Agnostic Prediction Interval Estimator) for distribution-free split conformal inference with valid empirical coverage
- PuLP / SciPy Optimize for formulating and solving the constrained battery arbitrage linear program
- Polars and DuckDB for out-of-core feature engineering and high-frequency meter aggregation (15-minute intervals)
- Pydantic v2 for strict runtime schema validation of time-series payloads and dispatch policies
- Docker and Docker Compose for reproducible, containerized local and cloud deployment
- GitHub Actions for automated CI, linting, and continuous model backtesting validation

## 5. Architecture

VoltConformal operates as an asynchronous microservice. Telemetry data from smart meters and weather APIs enter through DuckDB-backed ingestion pipelines. The feature engineering module builds cyclical and lag features. LightGBM quantile models produce initial quantile traces, which pass through the Conformal Calibrator and Hierarchical Reconciler. The resulting calibrated probability distribution feeds the BESS Dispatch Optimizer, which solves a multi-period linear program and returns actionable dispatch schedules and risk alerts via FastAPI.

- **Ingestion & Preprocessing Engine** — Validates incoming 15-min CSV/JSON meter readings, handles missing timestamp imputation, and computes solar position features (zenith, azimuth).
- **Quantile Forecaster** — Executes trained gradient-boosted trees on engineered features to produce raw P10, P50, and P90 net-load forecasts.
- **Conformal Calibration Layer** — Computes non-conformity scores on sliding calibration windows and constructs certified prediction bounds at chosen confidence levels.
- **Hierarchical Reconciler** — Applies linear algebra projection (MinT/Bottom-Up) ensuring child feeder predictions sum exactly to parent substation metrics.
- **Battery Arbitrage Optimizer** — Executes linear programming to calculate charge/discharge schedules balancing TOU arbitrage, demand charge limits, and battery degradation costs.
- **REST API Gateway** — Exposes endpoints for forecasting, calibration updates, dispatch generation, and historical backtesting reports.

### Data flow

1. 1. Client uploads historical 15-minute load, PV generation, and weather telemetry via /api/v1/telemetry/ingest.
2. 2. DuckDB processes and validates time series, writing clean tabular features to local storage or memory.
3. 3. /api/v1/forecast/generate triggers LightGBM quantile regression over the next 96 timesteps (24 hours).
4. 4. The Conformal Calibration module adjusts interval bounds using non-conformity scores from recent calibration slices.
5. 5. The Hierarchical Reconciler projects multi-meter forecasts onto transformer structural constraints.
6. 6. /api/v1/dispatch/optimize feeds the calibrated P90 peak net-load trajectory and tariff matrices into the PuLP linear program.
7. 7. Optimized 24-hour battery battery schedule (kW charge/discharge, SoC %) and risk-bound intervals are returned as structured JSON.

## 6. Data model

- **MeterTelemetry:** timestamp: DateTime, node_id: String, parent_id: Optional[String], load_kw: Float, pv_generation_kw: Float, net_load_kw: Float, temperature_c: Float, ghi_wm2: Float
- **ForecastHorizonRecord:** horizon_step: Integer, target_timestamp: DateTime, node_id: String, p10_kw: Float, p50_kw: Float, p90_kw: Float, conformal_lower_kw: Float, conformal_upper_kw: Float, coverage_nominal: Float
- **TariffSchedule:** schedule_id: String, tariff_name: String, import_rates_per_kwh: List[Float], export_rates_per_kwh: List[Float], demand_charge_per_kw: Float
- **BatteryConfig:** battery_id: String, capacity_kwh: Float, max_charge_kw: Float, max_discharge_kw: Float, roundtrip_efficiency: Float, min_soc_pct: Float, max_soc_pct: Float, degradation_cost_per_kwh: Float
- **DispatchSchedule:** schedule_id: String, node_id: String, timestamp: DateTime, charge_kw: Float, discharge_kw: Float, grid_import_kw: Float, grid_export_kw: Float, simulated_soc_pct: Float, projected_cost_usd: Float

## 7. API contracts

| Method | Path | Purpose |
|---|---|---|
| POST | /api/v1/telemetry/ingest | Upload and validate raw time series batch (meter load, solar generation, weather) with timestamp alignment. |
| POST | /api/v1/forecast/generate | Generate 24-hour ahead (96-step) quantile forecasts with split-conformal prediction intervals for a specified node. |
| POST | /api/v1/forecast/reconcile | Reconcile independent node forecasts across the microgrid structural hierarchy using MinT or Bottom-Up methods. |
| POST | /api/v1/dispatch/optimize | Compute cost-optimal 24-hour battery charge/discharge schedule under conformal risk bounds and input tariff rates. |
| GET | /api/v1/evaluation/backtest | Run rolling backtest over historical dataset and return Pinball loss, Winkler score, interval coverage %, and cost savings. |

## 8. Build milestones

### 1 — Pipeline, Quantile Models, and Conformal Calibration

- [ ] Curate open microgrid dataset (e.g., OpenEI or Pecan Street open sample) downsampled to uniform 15-minute intervals.
- [ ] Implement temporal feature engineering pipeline (time-of-day, day-of-week, solar angles, 24h/168h lags, rolling standard deviations).
- [ ] Train multi-quantile LightGBM models for P10, P50, and P90 net-load.
- [ ] Implement split conformal prediction layer to generate statistically valid prediction bands at user-chosen alpha.
- [ ] Verify empirical coverage on held-out test windows.

**Deliverable:** Working Python module and tests generating calibrated conformal prediction intervals with validation scripts.

### 2 — Optimization Solver, API Layer, and End-to-End Evaluation

- [ ] Implement hierarchical reconciliation matrix operations to ensure sub-meter coherence.
- [ ] Construct PuLP-based linear programming optimizer enforcing BESS limits, C-rates, and degradation penalties.
- [ ] Build FastAPI endpoints exposing ingestion, forecast, reconcile, and dispatch functionalities with Pydantic validation.
- [ ] Write backtesting benchmarking script comparing VoltConformal against deterministic point-forecast heuristic dispatch.
- [ ] Containerize application using Docker and create reproducible sample execution CLI.

**Deliverable:** Fully functioning Dockerized FastAPI service with automated integration tests and backtest benchmark report.


## 9. Evaluation plan

Targets to test, not claimed results.

- **Empirical Prediction Interval Coverage (PICP):** Proportion of actual net-load observations falling between lower and upper conformal bounds over rolling 30-day out-of-sample backtest at nominal 90% confidence. Target: >= 89.0% and <= 92.0% (strict marginal validity without undercoverage)
- **Normalized Continuous Ranked Probability Score (CRPS) or Pinball Loss:** Mean pinball loss across P10, P50, and P90 evaluation steps normalized by average load capacity. Target: >= 15% reduction in pinball loss relative to a persistence baseline
- **Microgrid Arbitrage Cost Reduction:** Simulated total electricity billing cost (energy import fees + demand charges - export credits) over 30 test days compared to naive heuristic solar self-consumption. Target: >= 18.0% cumulative energy cost reduction
- **End-to-End Pipeline Latency:** Wall-clock execution time for feature engineering, 96-step forecast generation, conformal calibration, and LP dispatch solve under single request. Target: < 450 milliseconds on standard 4-core consumer CPU

## Testing checklist

- [ ] Unit tests for solar position calculations and time-lag feature extraction under missing timestamp scenarios using pytest.
- [ ] Property-based testing with Hypothesis ensuring conformal lower bounds are strictly less than or equal to upper bounds for all timesteps.
- [ ] Constraint validation tests for the PuLP dispatch optimizer verifying battery SoC never exceeds specified physical thresholds (e.g., [15%, 95%]).
- [ ] API integration tests using FastAPI TestClient asserting correct HTTP status codes, error handling for corrupted time-series schemas, and valid JSON schemas.
- [ ] Stress test generating forecasts and dispatch schedules for 50 concurrent microgrid nodes within 2 seconds.

## Deployment and setup

- [ ] Multi-stage Dockerfile packaging FastAPI, LightGBM, and PuLP with minimal Debian slim base.
- [ ] Docker Compose environment pre-configured with local DuckDB volume and optional Redis cache for fast feature lookups.
- [ ] GitHub Actions pipeline running flake8/black linting, pytest suite, and automated backtest regression test on PRs.
- [ ] Deployable to free-tier cloud containers (Render, Railway, or Hugging Face Spaces) with zero proprietary vendor dependencies.

## Prerequisites

- Intermediate to advanced proficiency in Python and statistical machine learning
- Understanding of time-series cross-validation (expanding/rolling window evaluation)
- Familiarity with quantile loss (pinball loss) and basic conformal prediction theory
- Basic knowledge of linear programming and constrained optimization

## Safety and privacy

- Zero transmission of raw customer PII; only anonymized node IDs and aggregated electrical metrics (kW) are processed.
- Deterministic physical battery safety bounds hardcoded into the optimizer constraints to prevent virtual battery over-discharge or thermal over-stress commands.
- Strict input payload validation preventing SQL injection and path traversal during DuckDB local queries.

## Learning outcomes

- Implement multi-horizon temporal feature engineering (lags, rolling statistics, calendar harmonics, solar zenith angles) on high-frequency energy data
- Train and tune LightGBM quantile regression models to capture heteroscedastic net-load uncertainty
- Apply inductive conformal prediction to time-series residuals to guarantee user-specified confidence coverage (e.g., 90%) without normality assumptions
- Implement hierarchical reconciliation (Bottom-Up and MinT-shrinkage) to ensure meter-level forecasts sum consistently to transformer-level aggregates
- Formulate and solve a real-world multi-period Battery Energy Storage System (BESS) dispatch linear program incorporating state-of-charge limits and cycle degradation penalties

## Stretch goals

- Incorporate a pre-trained open-weights time series foundation model (e.g., Chronos or TinyTimeMixer) as an ensemble candidate alongside LightGBM.
- Add battery health-aware battery degradation modeling using non-linear rainflow-counting cycle cost approximations.
- Implement an interactive React or Streamlit dashboard visualizing quantile fan charts, conformal bands, and real-time battery state transitions.

## Resume bullet — add real results after implementation

Architected VoltConformal, a production-grade microgrid forecasting and dispatch engine in FastAPI and LightGBM; delivered finite-sample 90% conformal coverage for net-load volatility and cut simulated energy arbitrage costs by 18.4% via a PuLP-driven constrained linear program.

## Interview questions

- Why choose inductive split conformal prediction over assuming Gaussian prediction errors or standard bootstrapping for time-series intervals?
- How does the pinball loss function allow a gradient-boosted tree like LightGBM to directly output specific quantiles (e.g., P10, P90)?
- What is the MinT (Minimum Trace) hierarchical reconciliation approach, and why does predicting independently at all hierarchy levels cause aggregation mismatches?
- How does formulating battery dispatch as a linear program differ from using reinforcement learning, and what are the trade-offs regarding computational determinism and safety guarantees?

## Recent research to explore

Fetched from arXiv on this run; leads for further reading, not proof of originality.

- [A Unified Framework for Image-to-3D Part Generation via Variable Granularity](http://arxiv.org/abs/2610.31671v1) — updated 2026-10-22.
  - Controllable 3D part generation is pivotal for digital asset creation, yet existing methods lack the flexibility to accommodate diverse user workflows requiring varying levels of control. In this paper, we introduce FlexPart, a unified image-to-3D part generation framework that supports variable-gra

- [Sensorimotor Alignment: A Platonic Proxy for Embodied Policy Success](http://arxiv.org/abs/2610.31670v1) — updated 2026-10-22.
  - Robotic foundation models are typically evaluated through costly closed-loop rollouts, which motivates cheap offline proxies for model capability. The Platonic Representation Hypothesis (PRH) suggests that as representations improve, different modalities such as vision and language converge toward a

- [Reading, Writing, Sharing, and Interacting with the World through Video](http://arxiv.org/abs/2610.31668v1) — updated 2026-10-22.
  - Video foundation models have advanced rapidly in understanding and generating visual sequences, while video world models seek to capture the underlying dynamics of the world they depict. Despite their different objectives, both concern the relationship between video observations and an evolving worl

- [Direct Pass@$k$ Optimization for Thought Pruning: Balancing Quality and Diversity in Test-Time Reasoning](http://arxiv.org/abs/2610.31667v1) — updated 2026-10-22.
  - Test-time scaling has emerged as a key inference strategy for reasoning models, where a model generates a large number of candidate solutions in the hope of finding at least one correct solution. Running all candidate solutions to completion can be computationally demanding, so recent work prunes th

- [Phase Transition from Random Features to Fully Trainable Networks](http://arxiv.org/abs/2610.31663v1) — updated 2026-10-22.
  - Constructing accurate and computationally tractable approximation spaces is a fundamental task in scientific computing. Partially trainable neural networks bridge fixed random features and fully adaptive representations. This paper quantifies a phase transition pattern in approximation bounds and ob

- [Reliable AI-Assisted Decisions via Selective Auditing](http://arxiv.org/abs/2610.31662v1) — updated 2026-10-22.
  - We consider online monitoring of an AI system that produces a sequence of decisions. At each round, the system outputs a proposed decision together with a confidence score estimating the trustworthiness of the decision. The decision and confidence score need not be produced by the same model: for ex

- [SpectralCanary: Embarrassingly Simple Low-Frequency Traces for T2I Dataset-Use Auditing](http://arxiv.org/abs/2610.31659v1) — updated 2026-10-22.
  - Auditing whether a text-to-image (T2I) model was fine-tuned on a particular image collection is difficult: a model can absorb collection-level visual characteristics without reproducing training images. Proactive dataset-use auditing plants a shared signal in a dataset before release, then later che

- [Cost-Aware Abstention for LLM-Based IT Ticket Classification](http://arxiv.org/abs/2610.31657v1) — updated 2026-10-22.
  - Wrong automatic routing of an IT support ticket can cost more than human triage. We evaluate cost-aware abstention as an offline, cost-conditional readiness assessment: select a routing policy on calibration data under explicit costs, then evaluate that frozen policy once on held-out test data. On a


## Hugging Face optimization

- Status: failed_keep_original
- Model: openai/gpt-oss-120b:fastest
- Note: Client error '402 Payment Required' for url 'https://router.huggingface.co/v1/chat/completions' (Request ID: Root=1-6adc613d-34d8fecd73a0b4ba29807f6f;1f526334-43b1-4e00-a369-1511a1e0922c)
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/402

You have no remaining credits. Purchase pre-paid credits to continue using Inference Providers. Alternatively, subscribe to PRO to get monthly included credits.

## Gemini design review

- Novelty score: 7/10
- Feasibility score: 8/10

### Overlap risks

- Standard quantile regression for solar/load forecasting is widely covered in ML energy literature and open-source packages (e.g., neuralprophet, darts, statsmodels).
- Open-source microgrid dispatch optimization (e.g., PyPSA, OEMOF, pymgrid) already implements linear programming for battery arbitrage.
- MAPIE already provides conformal quantile regression out-of-the-box, making simple wrapping of MAPIE + LightGBM low in technical differentiation.
### Suggested improvements

- Address exchangeability violations inherent to time series by implementing Adaptive Conformal Inference (ACI) or EnbPI (Ensemble Batch Prediction Intervals) rather than basic inductive split conformal.
- Formulate the downstream battery dispatch as a robust or distributionally robust optimization problem directly driven by the conformal interval radius rather than merely taking the P90 point estimate into a standard LP.
- Clarify how hierarchical reconciliation (MinT) interacts mathematically with conformal bounds, as linear summation projections typically distort non-Gaussian quantile bounds.

---
Generated with Gemini fallback / gemini-3.8-flash. Verify assumptions and report only measured results.

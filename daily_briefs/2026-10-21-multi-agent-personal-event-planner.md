# Multi-Agent Personal Event Planner

> An agentic web service that composes privacy‑first, multimodal itineraries by orchestrating specialized LLM agents with LangGraph state graphs and CrewAI task crews. Users get a day‑plan with activities, travel, budget, and generated visual moodboards.

**Date:** 2026-10-21 | **Category:** LangChain | **Difficulty:** Intermediate | **Effort:** 5 days

**Build-it-yourself brief:** this factory produces the specification, not source code.

## 1. Problem statement

College students and young professionals struggle to manually synthesize calendars, emails, location preferences, budget constraints, and real‑time weather into coherent daily plans. Existing planners are either static or rely on cloud services that expose personal data.

### Target users

- College students
- Young professionals
- Travel enthusiasts seeking privacy‑first planning

## 2. Unique angle

First open‑source planner that couples LangGraph’s persistent state graph with CrewAI’s crew orchestration, enabling dynamic replanning when external conditions (weather, transit delays) change, all while keeping user data on‑device or in a self‑hosted Supabase instance.

## 3. MVP features and acceptance criteria

### User Profile & Calendar Ingestion

Upload a CSV of calendar events and a JSON of user preferences; service stores them securely.

- [ ] API returns 201 on valid upload
- [ ] Data persisted in Supabase with encrypted columns
- [ ] Upload size limit 5 MB enforced

### Stateful Itinerary Generation

LangGraph creates a planning graph; CrewAI coordinates WeatherAgent, TransportAgent, BudgetAgent, and MoodboardAgent to output a JSON itinerary.

- [ ] Response time < 8 seconds for a typical day plan
- [ ] Itinerary includes at least 3 activities, travel steps, budget summary, and a moodboard image URL
- [ ] If weather forecast changes, a replan endpoint returns updated itinerary

### Replan & Feedback Loop

User can request a replan after changing constraints; the graph resumes from the last state without recomputing from scratch.

- [ ] Replan endpoint returns updated plan within 5 seconds
- [ ] State graph version increments correctly
- [ ] Previous plan is archived for audit

## 4. Technology stack

- FastAPI – lightweight async API layer
- LangChain – tool integration and LLM prompting
- LangGraph – graph‑based stateful planning across multiple LLM calls
- CrewAI – defines specialized agents (WeatherAgent, TransportAgent, BudgetAgent, MoodboardAgent) and manages task delegation
- PostgreSQL + pgvector (via Supabase) – stores user events, embeddings for semantic search, and the LangGraph state
- Redis – short‑term cache for external API responses (weather, transit)
- Docker – reproducible container for dev & deployment
- GitHub Actions – CI/CD lint, test, and Docker image build

## 5. Architecture

A FastAPI gateway receives user data, persists it, and triggers a LangGraph workflow. CrewAI defines specialized agents that call external APIs via LangChain tools. The graph state lives in Redis & PostgreSQL, enabling resumable planning. Results are stored and served back to the UI (outside scope).

- **FastAPI Gateway** — HTTP request validation, authentication, and orchestration trigger
- **LangGraph Planner** — Maintain directed acyclic graph of planning steps, store node results, enable resumability
- **CrewAI Crew Manager** — Instantiate and schedule specialized agents, aggregate outputs
- **PostgreSQL (Supabase)** — Persist user profiles, calendar data, embeddings, and final itineraries
- **Redis Cache** — Cache weather/transit API responses and intermediate graph nodes
- **External APIs** — Provide weather (OpenWeather), public transit (Google Directions), and image generation (Stable Diffusion)

### Data flow

1. User uploads calendar → FastAPI stores raw data → Embeddings generated via SentenceTransformer → LangGraph creates initial planning node → CrewAI dispatches agents → Each agent calls a LangChain tool → Results cached in Redis → Graph nodes persisted in PostgreSQL → Final itinerary returned to user

## 6. Data model

- **user:** id (uuid), email (encrypted), created_at (timestamp)
- **calendar_event:** id, user_id, title, start_time, end_time, location, description
- **preference:** user_id, budget_limit, preferred_activities (json), mobility_constraints
- **itinerary:** id, user_id, date, plan_json (jsonb), moodboard_url, created_at
- **graph_state:** graph_id, user_id, node_id, state_blob (jsonb), updated_at

## 7. API contracts

| Method | Path | Purpose |
|---|---|---|
| POST | /upload/calendar | Ingest user calendar CSV |
| GET | /itinerary/{date} | Retrieve generated itinerary for a given date |
| POST | /itinerary/{date}/replan | Trigger a replan with optional constraint overrides |
| GET | /healthz | Liveness probe |

## 8. Build milestones

### 1 — Foundations & Data Layer

- [ ] Set up FastAPI skeleton
- [ ] Configure Supabase + pgvector schema
- [ ] Implement CSV ingestion endpoint

**Deliverable:** Running API that accepts calendar uploads and stores them


## 9. Evaluation plan

Targets to test, not claimed results.

- **Average planning latency:** Measure response time for /itinerary generation over 30 random days Target: < 8 seconds
- **Plan completeness:** Automated check that itinerary JSON contains ≥3 activities, travel steps, budget, moodboard Target: 100% of generated plans
- **Privacy compliance score:** Static analysis ensuring no raw PII leaves container (no external logging) Target: Full compliance

## Testing checklist

- [ ] Unit tests for each FastAPI route (pytest)
- [ ] Integration test simulating full planning cycle with mocked external APIs
- [ ] Load test (locust) for 50 concurrent users measuring latency
- [ ] Security test verifying encryption at rest for email field

## Deployment and setup

- [ ] Dockerfile builds a lightweight image (python:slim)
- [ ] docker-compose defines api, redis, postgres services
- [ ] GitHub Actions CI builds image, runs tests, pushes to Docker Hub
- [ ] Deploy to Fly.io (free tier) or Render.com with environment variables for API keys

## Prerequisites

- Python 3.11+
- Basic FastAPI knowledge
- Familiarity with LangChain abstractions (LLM, Tools)
- Understanding of graph‑based workflows (LangGraph)
- Intro to CrewAI task definition

## Safety and privacy

- All user data stored in self‑hosted Supabase; optional local mode skips remote DB
- API keys for weather/transport are kept in server‑side env vars, never exposed to client
- No telemetry is sent to third‑party services
- Data is encrypted at rest (PGP) and in transit (HTTPS)

## Learning outcomes

- Design and implement a multi‑agent system using CrewAI
- Persist and query planning state with LangGraph
- Integrate external APIs as LangChain tools
- Store and retrieve semantic embeddings with pgvector
- Deploy a privacy‑first FastAPI service with Docker

## Stretch goals

- Add voice interaction using VAPI to capture constraints via speech
- Support multi‑day trip planning with itinerary chaining
- Integrate a small fine‑tuned LLM (e.g., Llama‑3‑8B) hosted locally for fully offline operation

## Resume bullet — add real results after implementation

Designed and delivered a privacy‑first multi‑agent event planner; achieved <8s end‑to‑end latency for dynamic itineraries, integrated LangGraph state graphs and CrewAI crew orchestration, and deployed via Docker to a production‑grade cloud platform.

## Interview questions

- Explain how LangGraph enables resumable planning compared to a stateless chain of LLM calls.
- What are the trade‑offs of using CrewAI versus manually sequencing agents?
- How would you secure user calendar data when using external weather APIs?
- Describe a failure scenario where the weather API is unavailable. How does your system recover?
- If you wanted to move the entire stack to an on‑device deployment, which components would need to change?

## Recent research to explore

Fetched from arXiv on this run; leads for further reading, not proof of originality.

- [Joints, Camera, Action! Co-Generating 3D Motion and Video for Arbitrary Rigs](http://arxiv.org/abs/2610.28632v1) — updated 2026-10-20.
  - Video generation models can now depict remarkably realistic motion. Yet it is unclear how to use this motion beyond pixels: to animate a specific 3D asset and replay the animation in its 3D scene. For instance, a video model can show a monkey jumping over a crossbar, but it cannot return that jump a

- [AEON: Unifying Video and 3D World Models](http://arxiv.org/abs/2610.28631v1) — updated 2026-10-20.
  - Current world models for explicit world simulation typically follow two distinct pathways: (1) video generative models (e.g., Sora), which simulate realistic appearances but fail to preserve 3D consistency; and (2) 3D generative models (e.g., Marble), which generate geometrically consistent scenes b

- [SolarRenderer: Few-Step Generative Reference Rendering](http://arxiv.org/abs/2610.28630v1) — updated 2026-10-20.
  - Game engines and coding agents can specify the layout, motion, and camera of a scene, yet turning such coarse structure into realistic video requires a renderer that follows the structure and completes the appearance it leaves open. Existing renderers are tied to the representation of one engine, ne

- [GBClaw: An agentic AI framework for atomistic grain boundary research and mechanistic discovery](http://arxiv.org/abs/2610.28629v1) — updated 2026-10-20.
  - Agentic artificial intelligence (AI) systems hold immense potential for automating complex workflows in materials discovery and design, but extending them to domain-intensive mechanistic investigations remains challenging. Here, we present GBClaw, an agentic AI framework for investigating the struct

- [Learning Adaptable Dexterous Skills via Hybrid Dexterous Mimicking](http://arxiv.org/abs/2610.28628v1) — updated 2026-10-20.
  - Dexterous multi-finger hands hold promise to unlock diverse skills like functional grasps, in-hand reorientation, and dynamic handover that the human-designed world assumes, yet existing learning recipes force a trade-off. Goal-reaching reinforcement learning generalizes to arbitrary object poses bu

- [UniWALM: Unified World Action Language Model for Embodied Robot Control](http://arxiv.org/abs/2610.28626v1) — updated 2026-10-20.
  - Motivated by the human ability to integrate experience across language, perception, and action, we introduce UniWALM, a unified world-action-language model that learns video, action, and language in a single shared representation, where each modality is both a conditioning signal and a supervision t

- [PsycheMME: A Psychology-Informed Benchmark for Social Understanding and Interaction in Videos](http://arxiv.org/abs/2610.28625v1) — updated 2026-10-20.
  - Understanding human needs and selecting responses require distinct judgments that aggregate accuracy can obscure. We introduce PsycheMME, a video benchmark informed by psychology, with eight capabilities spanning grounding, states, needs, interaction decisions, memory, and risk. Drawing on Social In

- [Industrial ReMEmbR: Scaling Spatiotemporal Memory to Robot Fleets](http://arxiv.org/abs/2610.28624v1) — updated 2026-10-20.
  - Warehouse robot fleets continuously observe operational conditions, but preserving these observations as reusable semantic memory incurs substantial computation, communication, and storage costs. For example, explaining recurring aisle blockages can require reviewing video from multiple robots acros


## Hugging Face optimization

- Status: failed_keep_original
- Model: openai/gpt-oss-120b:fastest
- Note: Client error '402 Payment Required' for url 'https://router.huggingface.co/v1/chat/completions' (Request ID: Root=1-6ad87065-4660e07f6fb7164b0d19682a;ad36540a-0f03-4143-967c-217aecf2101f)
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/402

You have no remaining credits. Purchase pre-paid credits to continue using Inference Providers. Alternatively, subscribe to PRO to get monthly included credits.

---
Generated with Groq / openai/gpt-oss-120b. Verify assumptions and report only measured results.

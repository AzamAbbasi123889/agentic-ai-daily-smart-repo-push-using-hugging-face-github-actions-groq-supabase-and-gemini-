# PolicyGraph-Agent: Multi-Agent Autonomous IaC Security Remediation Engine with LangGraph Verification Cycles

> PolicyGraph-Agent is an autonomous security remediation system that ingests Infrastructure-as-Code (Terraform/OpenTofu) static scan findings, maps resource dependency graphs, and generates drift-safe configuration patches. Orchestrated via LangGraph stateful cycles and specialized CrewAI worker agents, the engine validates synthesized patches inside ephemeral OpenTofu sandbox containers to ensure zero unintended infrastructure destruction before routing to human-in-the-loop review.

**Date:** 2026-10-25 | **Category:** LangChain, LangGraph and CrewAI | **Difficulty:** Advanced | **Effort:** 7 days

**Build-it-yourself brief:** this factory produces the specification, not source code.

## 1. Problem statement

Cloud security scanners such as Checkov and Trivy detect thousands of configuration policy violations (e.g., exposed storage buckets, broad security group egress, unencrypted volumes), but platform engineering teams face an overwhelming remediation backlog. Naive LLM code generation regularly outputs invalid HashiCorp Configuration Language (HCL) syntax, misses critical resource dependencies, or produces patches that trigger unintended resource destruction during deployment. SRE and DevSecOps teams lack an automated, deterministic verification loop that bridges static vulnerability reports with validated, non-destructive IaC remediation PRs.

### Target users

- DevSecOps Engineers managing sprawling multi-cloud Terraform repositories
- Platform Engineering Leads tasked with eliminating infrastructure compliance backlogs
- Site Reliability Engineers (SREs) who require zero-downtime and zero-drift security patching
- Open-source cloud maintainers needing automated SARIF vulnerability resolution

## 2. Unique angle

Unlike traditional copilots that suggest unverified code snippets in an IDE, PolicyGraph executes an autonomous closed-loop agentic state machine using LangGraph. It runs localized OpenTofu validation and speculative execution plans in an isolated sandbox, parsing CLI diagnostic outputs back into agent feedback channels until the patch passes compilation with strict invariant assertions (0 resource destructions, zero schema invalidation) before pausing at a human-in-the-loop checkpoint.

## 3. MVP features and acceptance criteria

### SARIF & Checkov Ingestion Parser

Ingests raw JSON/SARIF vulnerability reports from Checkov or Trivy, extracting exact resource IDs, policy violation codes, and line numbers.

- [ ] Correctly parses Checkov JSON reports containing multiple failed checks into structured Pydantic schemas
- [ ] Extracts target resource addresses (e.g., aws_s3_bucket.data_archive) with 100% accuracy from file path and line coordinates
- [ ] Discards informational checks and isolates high/critical policy alerts

### AST Resource Dependency Mapper

Constructs a local dependency subgraph from affected HCL files using python-hcl2 to trace variable references and linked provider blocks.

- [ ] Identifies parent-child resource relationships and referenced local variables for the target block
- [ ] Outputs an isolated context payload under 4,000 tokens for downstream agent synthesis
- [ ] Gracefully handles multi-file Terraform module hierarchies

### Cyclic Verification and Patching StateGraph

LangGraph-powered iterative cycle where the HCL Synthesizer proposes code edits and the Sandbox Runner verifies them via OpenTofu CLI.

- [ ] Executes tofu fmt, tofu validate, and tofu plan inside a detached ephemeral Docker sandbox
- [ ] Feeds CLI stderr and diagnostic messages back to the synthesizer node upon validation failure
- [ ] Enforces a maximum cycle depth limit (default: 3 iterations) before gracefully failing or escalating

### Human-in-the-Loop Diff Signoff & Guardrail Checker

Halts agent graph execution at a review breakpoint, requiring human authorization if changes touch critical security parameters.

- [ ] Halts state machine execution via LangGraph interrupt() when a clean patch is generated
- [ ] Computes unified diff and parses tofu plan output to verify that resources_destroyed is strictly 0
- [ ] Exposes approve and reject API actions that resume or terminate graph execution

## 4. Technology stack

- Python 3.11+ for robust asynchronous backend and agent orchestration
- LangGraph for cyclic graph routing, state channels, checkpointer persistence, and human-in-the-loop interrupts
- CrewAI for role-specialized collaborative sub-agents (Security Auditor, Dependency Grapher, HCL Synthesizer)
- FastAPI for high-throughput asynchronous REST endpoints and webhook triggers
- OpenTofu / Terraform CLI in Docker for deterministic, isolated syntax verification and execution plan generation
- python-hcl2 and tree-sitter-hcl for fast AST parsing and resource dependency mapping
- SQLite / Redis with LangGraph MemorySaver for durable thread state and execution history caching
- Pydantic v2 for strict schema definition and structured LLM tool outputs

## 5. Architecture

The system follows an event-driven, agentic state-machine architecture. A FastAPI gateway receives vulnerability scan payloads and initializes a LangGraph state graph. Within the graph, specialized CrewAI agents analyze the SARIF finding, extract AST dependency boundaries, and synthesize HCL modifications. An ephemeral Docker runner executes OpenTofu commands, feeding back compiler outcomes into the state channel. Once validation passes with zero resource destruction, execution halts for human approval before outputting the final Git patch manifest.

- **FastAPI Webhook & Ingestion Service** — Receives SARIF/Checkov scan payloads, validates schemas, schedules background graph runs, and serves review APIs.
- **LangGraph Orchestrator** — Maintains shared execution state, conditional edges, retry counters, and human-in-the-loop interruption checkpointers.
- **CrewAI Remediation Ensemble** — Coordinates the Security Auditor (policy context), Dependency Analyst (AST scoping), and HCL Synthesizer (code patch generation).
- **Docker OpenTofu Verification Sandbox** — Executes isolated 'tofu init', 'tofu validate', and 'tofu plan' commands against generated code, outputting deterministic JSON execution plans.
- **Invariant Guardrail Evaluator** — Audits generated plan JSON to enforce zero-destruction policies and structural integrity invariants.

### Data flow

1. 1. CI/CD or user posts a Checkov JSON report and repo commit hash to /api/v1/scans/ingest.
2. 2. The Ingestion Engine parses violations into Pydantic models and initializes a LangGraph thread.
3. 3. The AST Mapper node parses local HCL files and extracts the target resource block and dependent variables.
4. 4. The CrewAI Synthesizer agent generates a candidate HCL patch using rule-specific remediation guidelines.
5. 5. The Sandbox Runner node writes the candidate code to an isolated volume and executes 'tofu validate' and 'tofu plan'.
6. 6. If errors occur, the diagnostic trace is appended to graph state, and a conditional edge routes back to the Synthesizer.
7. 7. If validation passes and resource destructions equal zero, the graph enters the review node and triggers an interrupt().
8. 8. An SRE inspects the unified diff via /api/v1/remediations/{id}/diff and posts an approval to /api/v1/remediations/{id}/approve.
9. 9. The final node creates a verifiable patch bundle and updates session state to COMPLETED.

## 6. Data model

- **ScanReport:** id: UUID (Primary Key), repository_url: String, commit_sha: String, scanner_type: String (Checkov | Trivy), raw_payload: JSONB, created_at: Timestamp
- **SecurityViolation:** id: UUID (Primary Key), scan_id: UUID (Foreign Key -> ScanReport.id), rule_id: String (e.g., CKV_AWS_18), severity: String (LOW | MEDIUM | HIGH | CRITICAL), target_file: String, resource_address: String, start_line: Integer, end_line: Integer, status: String (PENDING | REMEDIATING | RESOLVED | FAILED)
- **RemediationSession:** session_id: UUID (Primary Key), violation_id: UUID (Foreign Key -> SecurityViolation.id), thread_id: String (LangGraph Thread Key), iteration_count: Integer, current_state: String, is_interrupted: Boolean, created_at: Timestamp, updated_at: Timestamp
- **PatchArtifact:** id: UUID (Primary Key), session_id: UUID (Foreign Key -> RemediationSession.session_id), original_code: Text, patched_code: Text, unified_diff: Text, plan_summary: JSONB (added, changed, destroyed counts), validation_passed: Boolean, reviewer_verdict: String (PENDING | APPROVED | REJECTED), reviewed_at: Optional[Timestamp]

## 7. API contracts

| Method | Path | Purpose |
|---|---|---|
| POST | /api/v1/scans/ingest | Ingests a Checkov or Trivy JSON report, extracts distinct security violations, and registers them in the database. |
| POST | /api/v1/remediations/trigger | Launches a LangGraph remediation workflow for a specific violation ID and returns the active session thread ID. |
| GET | /api/v1/remediations/{session_id}/state | Retrieves real-time execution state, current node position, retry iteration count, and interrupt status. |
| GET | /api/v1/remediations/{session_id}/diff | Provides the unified diff and OpenTofu execution plan summary for pending human verification. |
| POST | /api/v1/remediations/{session_id}/approve | Submits reviewer verdict (approve/reject), resuming the interrupted LangGraph state to finalize or abort the patch. |

## 8. Build milestones

### 1 — Scan Ingestion, AST Scoper & Local Sandbox Setup

- [ ] Construct Pydantic models for Checkov SARIF and JSON vulnerability inputs
- [ ] Implement AST extraction logic using python-hcl2 to capture resource blocks and local contexts
- [ ] Build a lightweight Dockerized runner utility to execute headless OpenTofu init, validate, and plan commands
- [ ] Verify sandbox isolation and CLI stderr capture using sample vulnerable Terraform files

**Deliverable:** Working Python module that parses scan findings and runs containerized OpenTofu validation on arbitrary HCL fixtures.

### 2 — LangGraph Cyclic State Machine & CrewAI Integration

- [ ] Define LangGraph TypedDict state tracking code revisions, compiler outputs, and iteration bounds
- [ ] Implement CrewAI synthesizer agent equipped with HCL formatting and security policy prompt guides
- [ ] Create conditional routing edges: retry synthesis on compiler error, proceed to review on valid plan
- [ ] Implement LangGraph interrupt() logic for human review and persistent SQLite checkpointing
- [ ] Build FastAPI endpoints exposing scan upload, remediation triggering, and diff approval

**Deliverable:** Fully functional end-to-end agentic pipeline taking a failing Checkov finding to a verified, human-approved Git patch.


## 9. Evaluation plan

Targets to test, not claimed results.

- **Syntactic & Plan Validation Pass Rate:** Ratio of generated patches that pass both 'tofu validate' and 'tofu plan' without CLI failure over a benchmark of 30 synthetic Terraform vulnerabilities. Target: >= 90% pass rate within maximum 3 graph cycles
- **Zero Inadvertent Destruction Adherence:** Percentage of generated plans where OpenTofu plan JSON reports exactly 0 resources destroyed. Target: 100% adherence (zero permitted accidental destructions)
- **Average Agentic Convergence Cycles:** Mean number of LangGraph feedback iterations needed by the HCL Synthesizer to reach a clean validation state. Target: <= 2.0 cycles per violation
- **Remediation Latency:** End-to-end wall-clock time from scan ingestion to interrupted human-review breakpoint using standard Ollama/Groq inference. Target: < 40 seconds per single-resource remediation

## Testing checklist

- [ ] Unit tests for Checkov/Trivy JSON parser verifying extraction of resource addresses across 15 real-world scanner examples
- [ ] AST isolation tests ensuring referenced local variables and provider blocks are correctly parsed without dropping module contexts
- [ ] Mocked sandbox tests verifying that non-zero CLI exit codes properly populate the state channel with compiler error text
- [ ] Graph property tests confirming that the state machine halts immediately when iteration_count exceeds the configured limit
- [ ] Integration tests with a live Docker daemon verifying OpenTofu plan creation on sample S3, IAM, and Security Group misconfigurations
- [ ] Human-in-the-loop interruption tests verifying state persistence across process restarts using LangGraph MemorySaver

## Deployment and setup

- [ ] Package the FastAPI service and agent graph runtime into a primary Docker image
- [ ] Mount the host Docker socket or execute in a sibling Docker-out-of-Docker container for ephemeral OpenTofu validation runners
- [ ] Provide a docker-compose.yml including the API server, a Redis checkpointer service, and sample vulnerable IaC fixtures
- [ ] Include local execution documentation supporting both local Ollama models (e.g., Llama-3.1-8B) and Groq API keys for zero-cost operation

## Prerequisites

- Proficiency in Python and asynchronous programming (asyncio)
- Understanding of stateful LLM graphs (nodes, edges, conditional branches, state reducers)
- Familiarity with Infrastructure-as-Code concepts (Terraform/OpenTofu, state files, HCL syntax)
- Basic knowledge of Docker for containerized tool sandboxing

## Safety and privacy

- Sandbox Isolation: OpenTofu commands execute in an ephemeral container with disabled networking to prevent unauthorized provider downloads or data exfiltration
- Credential Protection: Real cloud credentials are explicitly excluded; the validator uses mock provider configurations and local state backends
- Prompt Injection Defense: IaC source code and vulnerability descriptions are sanitized and strictly treated as data variables within Pydantic prompts
- Human Supremacy Guardrail: No patch can be committed or applied automatically; graph termination is gated behind an explicit human cryptographic or API confirmation

## Learning outcomes

- Architect resilient, cyclic agentic workflows using LangGraph and role-based CrewAI agents
- Implement state persistence, time-travel debugging, and human-in-the-loop approval barriers in production LLM graphs
- Parse and manipulate code Abstract Syntax Trees (AST) to anchor LLM generation with structural constraints
- Integrate headless CLI compiler/linter feedback loops to dynamically correct LLM hallucination and syntax errors
- Design secure code execution environments that guard against hostile prompt injection and unauthorized script execution

## Stretch goals

- Support for multi-file cross-module refactoring where fixing a parent resource requires updating outputs in child modules
- Automated GitHub Pull Request creation with formatted Markdown summaries displaying the Checkov rule, rationale, and plan diff
- Integration with AWS LocalStack to test runtime API behavior for remediated resources before human review

## Resume bullet — add real results after implementation

Engineered an autonomous IaC security remediation platform using LangGraph and CrewAI that ingests static scan findings, resolves dependency graphs, and generates drift-free Terraform patches verified via containerized OpenTofu feedback loops with 100% zero-destruction compliance.

## Interview questions

- Why did you choose LangGraph's cyclic state machine over a standard linear CrewAI sequence for this problem?
- How does your architecture prevent an LLM from inadvertently creating a patch that destroys and recreates a production database?
- How did you implement human-in-the-loop breakpoints in LangGraph, and how is the agent state maintained during approval waits?
- What strategies did you use to pass compiler diagnostic logs back to the LLM to minimize token consumption while maximizing repair success?
- How do you secure the containerized sandbox to prevent malicious Terraform code from compromising the host execution environment?

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
- Note: Client error '402 Payment Required' for url 'https://router.huggingface.co/v1/chat/completions' (Request ID: Root=1-6addb50a-75ead09b4abb9b1029fa054e;f78b2b95-e2b4-4059-8729-9a5d72a23909)
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/402

You have no remaining credits. Purchase pre-paid credits to continue using Inference Providers. Alternatively, subscribe to PRO to get monthly included credits.

---
Generated with Gemini fallback / gemini-3.8-flash. Verify assumptions and report only measured results.

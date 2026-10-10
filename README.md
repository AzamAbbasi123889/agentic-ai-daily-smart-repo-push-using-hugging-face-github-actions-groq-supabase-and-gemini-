# Daily GitHub Agent — AI Project Brief Factory

This repository now has a daily **build-it-yourself project brief** workflow. It generates one detailed, distinct AI/ML project plan per day; it does **not** generate the implementation source code or create a new project repository for you. You build it yourself, then use Supabase to track your progress.

## What it covers

The rotating topic pool covers agentic AI and multi-agent systems, CrewAI/LangChain/LangGraph, advanced RAG and GraphRAG, LLM evaluation and LangSmith observability, NLP and Transformers, computer vision and multimodal AI, deep learning, MLOps, model monitoring, automation/tool use, AI safety, and AI developer tools.

Each brief is saved to `daily_briefs/YYYY-MM-DD-project-slug.md` and includes:
- Problem statement, target users and a clear differentiator.
- MVP features with testable acceptance criteria.
- Technology choices, component architecture, data flow and data model.
- API endpoint contracts, milestone-by-milestone build order and prerequisites.
- Test plan, measurable evaluation targets, privacy/safety and deployment plan.
- Resume bullet to update only after measuring real results, plus interview questions.
- Fresh arXiv AI research links retrieved during that run when the feed is available.
- A dedicated Hugging Face optimization pass that tightens the specification's scope, architecture, API/data contracts, acceptance criteria, testing, and evaluation. It preserves the project's title, slug, and core idea.
- Optional Gemini novelty/feasibility critique.

The factory scans your existing GitHub repository names, the current project's `data/projects.json`, local brief history, and Supabase memory to reduce repeats. It checks candidate titles/slugs and retries collisions. Local JSON history is a fallback; Supabase is required in the scheduled workflow.

## AI model routing

1. Primary generation: Groq with `openai/gpt-oss-120b`.
2. Generation fallback: Gemini with `gemini-3.8-flash`, if Groq fails and Gemini is configured.
3. Optimization pass: Hugging Face Inference Providers, using `HF_TOKEN` and `HF_OPTIMIZER_MODEL` (default `openai/gpt-oss-120b:fastest`). Hugging Face does **not** generate the initial brief and is not a generation fallback; it takes the Groq/Gemini draft and attempts to improve its technical quality while preserving the title, slug, and central idea.
4. Optional review: Gemini scores novelty and feasibility after optimization.
5. Recent research: arXiv Atom API, used as inspiration and linked in the brief.

Hugging Face uses the hosted **Inference Providers chat-completion API**, not an automatic download or local run of a model. Your `HF_TOKEN` must be a Hugging Face user access token with **Inference Providers** permission. If optimization fails, the original validated Groq/Gemini brief is kept. Provider/model availability, account credits and usage limits can affect the optimization call; set `HF_OPTIMIZER_MODEL` to a model available to your account if needed. Official docs: [Hugging Face chat completion](https://huggingface.co/docs/inference-providers/tasks/chat-completion).

## Setup (one-time)

### 1. Create the Supabase memory table

Open your Supabase project, go to **SQL Editor**, and run [`supabase/schema.sql`](supabase/schema.sql). The table uses row-level security and grants access to the server-side `service_role` only. Do not put the service-role/secret key in browser code or commit it to Git.

### 2. Add GitHub Actions secrets

Open your repository at GitHub → **Settings → Secrets and variables → Actions → New repository secret**. Add:

| Secret name | Value |
|---|---|
| `GROQ_API_KEY` | Your Groq API key |
| `GEMINI_API_KEY` | Your Google Gemini API key |
| `HF_TOKEN` | Hugging Face user access token with Inference Providers permission; used only to optimize the generated project specification |
| `SUPABASE_URL` | Project URL from Supabase |
| `SUPABASE_SECRET_KEY` | Supabase server-side secret key; alternatively use `SUPABASE_SERVICE_ROLE_KEY` |
| `AGENT_GITHUB_TOKEN` | Optional GitHub token with read access to your owned repositories, including private repos. Public repo scan works without it. |

Do not paste API keys into chat or source files. The GitHub workflow injects them at runtime.

### 3. Put the bundle in GitHub

**For a new empty repository:** extract the ZIP, open PowerShell in the extracted folder, initialize Git, and push to the repository you just created:

```powershell
git init -b main
git add .
git commit -m "Initial daily AI project brief builder"
git remote add origin https://github.com/YOUR-USERNAME/YOUR-NEW-REPOSITORY.git
git push -u origin main
```

Replace the remote URL with the HTTPS URL shown in your repository's **Quick setup** panel. Git must be installed and authenticated on your computer.

**For your existing `daily-github-agent` repository instead:** copy the files into your local clone, replace `README.md`, `requirements.txt`, `.env.example`, and `.github/workflows/daily-run.yml`, add the new generator and `supabase/schema.sql`, and keep your existing `app/`, project catalog, tests, and history. Commit and push on the repository's default branch.

### 4. Run the first brief

Go to **Actions → Daily AI Project Brief Builder → Run workflow** on `master`. The scheduled run is at **08:00 India Standard Time every day**. It will save one Markdown brief and local history to this repository. The workflow has no push trigger, so its own commit does not create a recursive run.

## Local usage

Python 3.11+ is recommended.

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env`, fill in local keys, and keep `.env` untracked. The factory loads `.env` automatically for local runs. Then run:

```bash
python daily_brief_factory.py --dry-run
```

This prints a brief without persisting it. For a real run with Supabase configured:

```bash
python daily_brief_factory.py --require-supabase
```

## Tracking your build

Use the Supabase SQL Editor to set the project's status to `building`, `completed`, or `skipped` and add your own notes. Example:

```sql
update public.project_memory
set status = 'building', build_notes = 'Started API and data ingestion', updated_at = now()
where slug = 'the-project-slug';
```

To finish, set status to `completed` and record what you actually implemented, tests, deployed URL and measured results. The next brief reads recent memory to help choose a different topic.

## Important behavior

- One brief per India-local calendar day. Re-running the same day's workflow keeps the existing brief.
- Initial generation requires `GROQ_API_KEY` or `GEMINI_API_KEY`; `HF_TOKEN` alone is intentionally insufficient because Hugging Face is an optimizer, not a generation provider.
- The scheduled workflow requires Supabase secrets; local runs can use local history only.
- If `HF_TOKEN` is not configured or optimization fails, the validated Groq/Gemini brief is retained and clearly labeled.
- If Gemini is unavailable, Groq can still generate the brief without the Gemini novelty/feasibility critique.
- If arXiv is unavailable, the brief is still generated without live paper links.
- The old template-based code generator remains in `main.py` / `app/`; this daily workflow no longer invokes it automatically.

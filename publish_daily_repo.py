#!/usr/bin/env python3
"""Publish one daily project brief into its own GitHub repository."""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

ROOT = Path(__file__).resolve().parent
BRIEFS_DIR = ROOT / "daily_briefs"
API = "https://api.github.com"
IST = ZoneInfo("Asia/Kolkata")

DEFAULT_OWNER = "AzamAbbasi123889"
CONTROLLER_REPO = (
    "agentic-ai-daily-smart-repo-push-using-hugging-face-"
    "github-actions-groq-supabase-and-gemini-"
)


def slugify(value: str, limit: int = 70) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return re.sub(r"-+", "-", value)[:limit].strip("-") or "ai-project"


def find_today_brief(date_text: str | None = None) -> Path:
    date_text = date_text or datetime.now(IST).date().isoformat()

    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_text):
        raise ValueError("Date must use YYYY-MM-DD format.")

    matches = sorted(BRIEFS_DIR.glob(f"{date_text}-*.md"))

    if not matches:
        raise FileNotFoundError(
            f"No brief exists for {date_text} in {BRIEFS_DIR}. "
            "Run daily_brief_factory.py first."
        )

    if len(matches) > 1:
        raise RuntimeError(
            f"Expected one brief for {date_text}; found {len(matches)}."
        )

    return matches[0]


def parse_brief(text: str, path: Path) -> dict[str, str]:
    date_match = re.match(r"^(\d{4}-\d{2}-\d{2})-", path.name)
    if not date_match:
        raise ValueError(f"Unexpected brief filename: {path.name}")

    date_text = date_match.group(1)
    title = next(
        (line[2:].strip() for line in text.splitlines()
         if line.startswith("# ")),
        "Daily AI Project",
    )
    summary = next(
        (line[2:].strip() for line in text.splitlines()
         if line.startswith("> ")),
        title,
    )

    def field(name: str, fallback: str) -> str:
        match = re.search(
            rf"\*\*{re.escape(name)}:\*\*\s*([^|\n]+)", text
        )
        return match.group(1).strip() if match else fallback

    slug = slugify(path.stem[len(date_text) + 1:])

    return {
        "date": date_text,
        "title": title,
        "summary": summary,
        "slug": slug,
        "category": field("Category", "AI Engineering"),
        "difficulty": field("Difficulty", "Intermediate"),
        "effort": field("Effort", "5 days"),
    }


def build_repo_name(meta: dict[str, str]) -> str:
    return (
        f"daily-ai-project-{meta['date']}-{meta['slug']}"
    )[:100].rstrip("-")


def build_checklist(brief: str) -> str:
    criteria = [
        line.strip()
        for line in brief.splitlines()
        if line.strip().startswith("- [ ]")
    ]

    lines = [
        "# Implementation Checklist",
        "",
        "Build this project yourself using `PROJECT_BRIEF.md`.",
        "",
        "## Initial setup",
        "",
        "- [ ] Read the project specification.",
        "- [ ] Create a Python virtual environment.",
        "- [ ] Install the documented dependencies.",
        "- [ ] Review the data and API requirements.",
        "- [ ] Keep credentials in environment variables.",
        "",
        "## Project acceptance criteria",
        "",
    ]

    lines.extend(
        criteria or ["- [ ] Turn the MVP requirements into testable tasks."]
    )

    lines.extend([
        "",
        "## Before completion",
        "",
        "- [ ] Implement the MVP features.",
        "- [ ] Add unit and integration tests.",
        "- [ ] Run the tests and record the actual result.",
        "- [ ] Measure the evaluation metrics in the brief.",
        "- [ ] Document setup, limitations and deployment.",
        "- [ ] Update the README with what you really implemented.",
        "- [ ] Add only verified results to your resume.",
        "",
    ])

    return "\n".join(lines)


def build_files(
    brief: str,
    meta: dict[str, str],
    owner: str,
    repo_name: str,
) -> dict[str, str]:
    package = slugify(meta["slug"], limit=55).replace("-", "_")
    if not package.isidentifier():
        package = "project_" + package

    controller_url = (
        f"https://github.com/{owner}/{CONTROLLER_REPO}"
    )

    readme = f"""# {meta['title']}

> {meta['summary']}

| Detail | Value |
|---|---|
| Date | {meta['date']} |
| Category | {meta['category']} |
| Difficulty | {meta['difficulty']} |
| Estimated effort | {meta['effort']} |
| Status | Starter scaffold — implementation required |

## Start here

1. Read [PROJECT_BRIEF.md](PROJECT_BRIEF.md).
2. Follow [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md).
3. Implement your application in `src/{package}/`.
4. Write tests in `tests/`.
5. Report real evaluation results, never invented results.

## Local setup

Use Python 3.11 or newer.

```bash
python -m venv .venv

# Windows CMD:
.venv\\Scripts\\activate.bat

# Windows PowerShell:
.venv\\Scripts\\Activate.ps1

# macOS/Linux:
# source .venv/bin/activate

python -m pip install -e ".[dev]"
pytest -q

#!/usr/bin/env python3
"""Publish each daily AI project brief to its own GitHub repository."""

from __future__ import annotations

import argparse
import base64
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

API_BASE = "https://api.github.com"
IST = ZoneInfo("Asia/Kolkata")

DEFAULT_OWNER = "AzamAbbasi123889"

CONTROLLER_REPO = (
    "agentic-ai-daily-smart-repo-push-using-hugging-face-"
    "github-actions-groq-supabase-and-gemini-"
)


def slugify(value: str, limit: int = 70) -> str:
    """Convert a project title into a GitHub-friendly slug."""
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    value = re.sub(r"-+", "-", value)
    return value[:limit].strip("-") or "ai-project"


def find_today_brief(date_text: str | None = None) -> Path:
    """Find the one Markdown brief generated for the requested date."""
    date_text = date_text or datetime.now(IST).date().isoformat()

    try:
        datetime.strptime(date_text, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("Date must use YYYY-MM-DD format.") from exc

    matches = sorted(BRIEFS_DIR.glob(f"{date_text}-*.md"))

    if not matches:
        raise FileNotFoundError(
            f"No brief found for {date_text} in {BRIEFS_DIR}. "
            "Run daily_brief_factory.py first."
        )

    if len(matches) > 1:
        raise RuntimeError(
            f"Expected one brief for {date_text}, "
            f"but found {len(matches)}. Resolve the duplicate briefs first."
        )

    return matches[0]


def parse_brief(text: str, brief_path: Path) -> dict[str, str]:
    """Extract project metadata from the generated Markdown brief."""
    date_match = re.match(r"^(\d{4}-\d{2}-\d{2})-", brief_path.stem)

    if not date_match:
        raise ValueError(
            f"Brief filename must start with YYYY-MM-DD-: {brief_path.name}"
        )

    date_text = date_match.group(1)

    title = next(
        (
            line[2:].strip()
            for line in text.splitlines()
            if line.startswith("# ")
        ),
        "Daily AI Project",
    )

    summary = next(
        (
            line[2:].strip()
            for line in text.splitlines()
            if line.startswith("> ")
        ),
        title,
    )

    def read_field(name: str, fallback: str) -> str:
        pattern = rf"\*\*{re.escape(name)}:\*\*\s*([^|\n]+)"
        match = re.search(pattern, text)
        return match.group(1).strip() if match else fallback

    project_slug = slugify(
        brief_path.stem[len(date_text) + 1:],
        limit=70,
    )

    return {
        "date": date_text,
        "title": title,
        "summary": summary,
        "slug": project_slug,
        "category": read_field("Category", "AI Engineering"),
        "difficulty": read_field("Difficulty", "Intermediate"),
        "effort": read_field("Effort", "5 days"),
    }


def build_repo_name(meta: dict[str, str]) -> str:
    """Produce a deterministic repository name for one daily project."""
    prefix = f"daily-ai-project-{meta['date']}-"
    remaining = 100 - len(prefix)
    return prefix + slugify(meta["slug"], limit=remaining)


def build_checklist(brief: str) -> str:
    """Create an implementation checklist from the project specification."""
    criteria = [
        line.strip()
        for line in brief.splitlines()
        if line.strip().startswith("- [ ]")
    ]

    lines = [
        "# Implementation Checklist",
        "",
        "Build the application yourself using `PROJECT_BRIEF.md`.",
        "",
        "## Initial setup",
        "",
        "- [ ] Read the project specification.",
        "- [ ] Review the architecture and data model.",
        "- [ ] Create a Python virtual environment.",
        "- [ ] Install and pin the required dependencies.",
        "- [ ] Configure credentials through environment variables.",
        "- [ ] Review the data privacy and security requirements.",
        "",
        "## Project acceptance criteria",
        "",
    ]

    lines.extend(
        criteria or [
            "- [ ] Translate the MVP features into testable implementation tasks."
        ]
    )

    lines.extend(
        [
            "",
            "## Before completion",
            "",
            "- [ ] Implement the planned MVP features.",
            "- [ ] Add unit and integration tests.",
            "- [ ] Run the test suite.",
            "- [ ] Measure the evaluation metrics in the brief.",
            "- [ ] Record actual results and known limitations.",
            "- [ ] Document setup and deployment.",
            "- [ ] Update the README to reflect the implemented features.",
            "- [ ] Add only verified outcomes to your resume.",
            "",
        ]
    )

    return "\n".join(lines)


def build_files(
    brief: str,
    meta: dict[str, str],
    owner: str,
    repo_name: str,
) -> dict[str, str]:
    """Build the starter files to publish to the new project repository."""
    package_name = slugify(meta["slug"], limit=55).replace("-", "_")

    if not package_name.isidentifier():
        package_name = "project_" + package_name

    controller_url = f"https://github.com/{owner}/{CONTROLLER_REPO}"
    safe_title = meta["title"].replace('"', "'")

    readme = f"""# {meta['title']}

> {meta['summary']}

| Detail | Value |
|---|---|
| Project date | {meta['date']} |
| Category | {meta['category']} |
| Difficulty | {meta['difficulty']} |
| Estimated effort | {meta['effort']} |
| Status | Starter scaffold; implementation required |

## Start here

1. Read [PROJECT_BRIEF.md](PROJECT_BRIEF.md) completely.
2. Follow [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md).
3. Implement your Python application in `src/{package_name}/`.
4. Add tests in `tests/`.
5. Measure the evaluation metrics from the project brief.
6. Record real results rather than invented performance claims.

## Local setup

Python 3.11 or newer is recommended.

Create a virtual environment, activate it for your operating system, then run:

    python -m pip install -e ".[dev]"
    pytest -q

## Repository contents

- `PROJECT_BRIEF.md` — detailed project specification.
- `IMPLEMENTATION_CHECKLIST.md` — implementation checklist.
- `src/{package_name}/` — your application code.
- `tests/` — automated tests.
- `.github/workflows/tests.yml` — basic Python CI.
- `data/` — add appropriate sample data.
- `artifacts/` — place generated outputs here when appropriate.

This repository contains a specification and a starter scaffold, not a finished
application. Implement and test the real functionality yourself.

Never commit API tokens, real `.env` files, private datasets, or personal records.

## Daily project controller

[{owner}/{CONTROLLER_REPO}]({controller_url})
"""

    pyproject = f"""[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{repo_name}"
version = "0.1.0"
description = "Starter scaffold for {safe_title}"
readme = "README.md"
requires-python = ">=3.11"
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=8.0.0"]

[tool.setuptools]
package-dir = {{"" = "src"}}

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
"""

    return {
        "README.md": readme,
        "PROJECT_BRIEF.md": brief.rstrip() + "\n",
        "IMPLEMENTATION_CHECKLIST.md": build_checklist(brief),
        "pyproject.toml": pyproject,
        ".gitignore": """__pycache__/
*.py[cod]
*.egg-info/
build/
dist/
.venv/
venv/
.env
.env.*
!.env.example
.pytest_cache/
.coverage
htmlcov/
data/raw/*
data/private/*
artifacts/*
!data/.gitkeep
!artifacts/.gitkeep
""",
        ".env.example": (
            "# Example configuration only.\n"
            "# Never commit real API credentials.\n"
        ),
        f"src/{package_name}/__init__.py": (
            '"""Implement the application modules here."""\n\n'
            '__version__ = "0.1.0"\n'
        ),
        "tests/test_scaffold.py": (
            f"from {package_name} import __version__\n\n\n"
            "def test_scaffold_version():\n"
            '    assert __version__ == "0.1.0"\n'
        ),
        "tests/README.md": (
            "# Tests\n\n"
            "Add unit tests, integration tests, and evaluation cases "
            "based on PROJECT_BRIEF.md. Mock external services in unit tests.\n"
        ),
        "data/.gitkeep": "",
        "artifacts/.gitkeep": "",
        ".github/workflows/tests.yml": """name: Python scaffold checks

on:
  push:
  pull_request:

permissions:
  contents: read

jobs:
  tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: pip
      - run: python -m pip install -e ".[dev]"
      - run: pytest -q
""",
    }


class GitHubPublisher:
    """Create repositories and publish files through the GitHub Git API."""

    def __init__(
        self,
        token: str,
        owner: str,
        private: bool = False,
    ):
        if not token:
            raise RuntimeError(
                "AGENT_GITHUB_TOKEN is missing. Add a GitHub token "
                "allowed to create repositories and write their contents."
            )

        self.owner = owner
        self.private = private
        self.session = requests.Session()

        self.session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )

        account = self.request("GET", "/user").json()
        actual_owner = account.get("login", "")

        if actual_owner.casefold() != owner.casefold():
            raise RuntimeError(
                f"The token belongs to {actual_owner!r}, "
                f"but the configured owner is {owner!r}."
            )

    def request(self, method: str, path: str, **kwargs):
        response = self.session.request(
            method,
            API_BASE + path,
            timeout=30,
            **kwargs,
        )

        if response.status_code >= 400:
            try:
                message = response.json().get("message", response.text)
            except ValueError:
                message = response.text

            if response.status_code == 403:
                message += (
                    " Check token scopes, repository permissions, "
                    "account restrictions, and rate limits."
                )

            if response.status_code == 422:
                message += (
                    " Check the repository name and whether repository "
                    "creation is permitted for this account."
                )

            raise RuntimeError(
                f"GitHub API {method} {path} returned "
                f"{response.status_code}: {message}"
            )

        return response

    def create_or_get_repo(
        self,
        name: str,
        description: str,
    ) -> tuple[dict, bool]:
        """Create the daily repository or reuse it on a retry."""
        path = f"/repos/{self.owner}/{name}"

        existing = self.session.get(
            API_BASE + path,
            timeout=30,
        )

        if existing.status_code == 200:
            repo = existing.json()
            actual_owner = repo.get("owner", {}).get("login", "")

            if actual_owner.casefold() != self.owner.casefold():
                raise RuntimeError("Existing repository owner mismatch.")

            return repo, False

        if existing.status_code != 404:
            self.request("GET", path)

        try:
            repo = self.request(
                "POST",
                "/user/repos",
                json={
                    "name": name,
                    "description": description[:350],
                    "private": self.private,
                    "auto_init": True,
                    "has_issues": True,
                    "has_projects": False,
                    "has_wiki": False,
                },
            ).json()

            print(f"[success] Created {repo.get('html_url', name)}")
            return repo, True

        except RuntimeError:
            # Another attempt may have created the repo already.
            check = self.session.get(API_BASE + path, timeout=30)

            if check.status_code == 200:
                return check.json(), False

            raise

    def get_base_tree(
        self,
        repo_name: str,
        branch: str,
    ) -> tuple[str, str]:
        """Return the latest commit and tree SHA for the target branch."""
        path = (
            f"/repos/{self.owner}/{repo_name}/"
            f"git/ref/heads/{branch}"
        )

        for attempt in range(10):
            response = self.session.get(
                API_BASE + path,
                timeout=30,
            )

            if response.status_code == 200:
                ref = response.json()
                break

            if response.status_code != 404:
                self.request("GET", path)

            time.sleep(min(attempt + 1, 4))
        else:
            raise RuntimeError(
                f"Could not find branch {branch!r} after repository creation."
            )

        parent_sha = ref["object"]["sha"]

        commit = self.request(
            "GET",
            f"/repos/{self.owner}/{repo_name}/git/commits/{parent_sha}",
        ).json()

        return parent_sha, commit["tree"]["sha"]

    def brief_already_uploaded(
        self,
        repo_name: str,
        branch: str,
        brief: str,
    ) -> bool:
        """Check whether this exact daily brief already exists remotely."""
        path = (
            f"/repos/{self.owner}/{repo_name}/contents/PROJECT_BRIEF.md"
        )

        response = self.session.get(
            API_BASE + path,
            params={"ref": branch},
            timeout=30,
        )

        if response.status_code == 404:
            return False

        if response.status_code != 200:
            self.request(
                "GET",
                path,
                params={"ref": branch},
            )

        data = response.json()

        if data.get("encoding") != "base64":
            return False

        remote_text = base64.b64decode(
            data.get("content", "")
        ).decode("utf-8")

        return remote_text.rstrip() == brief.rstrip()

    def publish(
        self,
        repo: dict,
        files: dict[str, str],
        brief: str,
    ) -> str:
        """Publish the provided files in one Git commit."""
        repo_name = repo["name"]
        branch = repo.get("default_branch") or "main"

        if self.brief_already_uploaded(repo_name, branch, brief):
            url = repo.get(
                "html_url",
                f"https://github.com/{self.owner}/{repo_name}",
            )
            print(f"[info] Today's brief already exists: {url}")
            return url

        parent_sha, base_tree_sha = self.get_base_tree(
            repo_name,
            branch,
        )

        entries = []

        for file_path, content in files.items():
            blob = self.request(
                "POST",
                f"/repos/{self.owner}/{repo_name}/git/blobs",
                json={
                    "content": content,
                    "encoding": "utf-8",
                },
            ).json()

            entries.append(
                {
                    "path": file_path,
                    "mode": "100644",
                    "type": "blob",
                    "sha": blob["sha"],
                }
            )

        tree = self.request(
            "POST",
            f"/repos/{self.owner}/{repo_name}/git/trees",
            json={
                "base_tree": base_tree_sha,
                "tree": entries,
            },
        ).json()

        commit = self.request(
            "POST",
            f"/repos/{self.owner}/{repo_name}/git/commits",
            json={
                "message": (
                    "docs: add daily project brief and starter scaffold"
                ),
                "tree": tree["sha"],
                "parents": [parent_sha],
            },
        ).json()

        self.request(
            "PATCH",
            f"/repos/{self.owner}/{repo_name}/git/refs/heads/{branch}",
            json={
                "sha": commit["sha"],
                "force": False,
            },
        )

        return repo.get(
            "html_url",
            f"https://github.com/{self.owner}/{repo_name}",
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Publish the daily brief into a separate repository."
    )

    parser.add_argument(
        "--date",
        help="Optional target date in YYYY-MM-DD format.",
    )

    parser.add_argument(
        "--owner",
        default=os.getenv("GITHUB_OWNER", DEFAULT_OWNER),
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the repository and filenames without publishing.",
    )

    args = parser.parse_args()

    brief_path = find_today_brief(args.date)
    brief = brief_path.read_text(encoding="utf-8")

    meta = parse_brief(brief, brief_path)
    repo_name = build_repo_name(meta)

    files = build_files(
        brief=brief,
        meta=meta,
        owner=args.owner,
        repo_name=repo_name,
    )

    if args.dry_run:
        print(f"Project: {meta['title']}")
        print(
            f"Repository: https://github.com/{args.owner}/{repo_name}"
        )
        print("Files to publish:")

        for filename in sorted(files):
            print(f"  {filename}")

        return 0

    token = (
        os.getenv("AGENT_GITHUB_TOKEN", "").strip()
        or os.getenv("GH_TOKEN", "").strip()
    )

    private = (
        os.getenv("DAILY_PROJECT_PRIVATE", "false").strip().lower()
        in {"1", "true", "yes"}
    )

    publisher = GitHubPublisher(
        token=token,
        owner=args.owner,
        private=private,
    )

    repo, created = publisher.create_or_get_repo(
        name=repo_name,
        description=(
            f"{meta['summary']} Build-it-yourself AI/ML project."
        ),
    )

    url = publisher.publish(
        repo=repo,
        files=files,
        brief=brief,
    )

    action = "Created" if created else "Reused"
    print(f"[success] {action} repository: {url}")
    print(f"[success] Published {len(files)} project files.")
    print(
        "[info] The repository contains a build brief and starter scaffold; "
        "the actual application still needs to be implemented."
    )

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[error] {exc}", file=sys.stderr)
        raise SystemExit(1)

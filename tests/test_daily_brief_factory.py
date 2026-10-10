import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "daily_brief_factory", Path(__file__).resolve().parents[1] / "daily_brief_factory.py"
)
factory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(factory)


def test_slugification():
    assert factory.slug("GraphRAG + Agentic QA!") == "graphrag-agentic-qa"


def test_json_object_parser():
    assert factory.parsej('```json\n{"title":"A","slug":"a"}\n```') == {"title": "A", "slug": "a"}


def test_similarity_detects_related_titles():
    assert factory.similarity("Agentic Incident Response Planner", "Agentic Incident Response Planner") == 1.0


def test_clean_rejects_incomplete_spec():
    try:
        factory.clean({"title": "Too short"})
    except ValueError as exc:
        assert "Missing fields" in str(exc)
    else:
        raise AssertionError("Incomplete specs must be rejected")


def minimal_spec():
    return {
        "title": "TraceForge Agent Replay",
        "slug": "traceforge-agent-replay",
        "category": "Agentic AI and Multi-Agent Systems",
        "summary": "Replay and evaluate agent tool traces.",
        "problem_statement": "Tool calling changes can break agents silently.",
        "unique_angle": "Deterministic trace replay with diffable outcomes.",
        "tech_stack": ["Python — orchestration", "FastAPI — API", "pytest — tests"],
        "mvp_features": [{"name": "Replay", "description": "Replay one trace", "acceptance_criteria": ["Same input creates a comparable result"]}],
        "architecture": {"overview": "Local-first replay service", "components": [{"name": "Runner", "responsibility": "Replay stored traces"}], "data_flow": ["Load trace", "Replay mocked tools", "Compare output"]},
        "data_model": [{"entity": "Trace", "fields": ["id", "events"]}],
        "api_endpoints": [{"method": "POST", "path": "/replay", "purpose": "Replay a trace"}],
        "milestones": [{"week": 1, "name": "MVP", "tasks": ["Build replay store"], "deliverable": "Runnable local app"}],
        "evaluation_plan": [{"metric": "Replay determinism", "how_to_measure": "Repeat the same trace", "target": "95% identical mocked outcomes"}],
        "test_plan": ["Test empty trace", "Test tool failure"],
        "deployment_plan": ["Run locally with documented setup"],
        "learning_outcomes": ["Agent evaluation"],
        "resume_bullet": "Built an agent replay harness; replace with measured results.",
        "interview_questions": ["How does trace replay help regression tests?"]
    }


def test_huggingface_json_uses_configured_token_and_parses_json(monkeypatch):
    import sys
    from types import SimpleNamespace

    seen = {}

    class FakeInferenceClient:
        def __init__(self, token):
            seen["token"] = token

        def chat_completion(self, **kwargs):
            seen["kwargs"] = kwargs
            message = SimpleNamespace(content='{"title":"HF optimized project"}')
            choice = SimpleNamespace(message=message)
            return SimpleNamespace(choices=[choice])

    monkeypatch.setenv("HF_TOKEN", "hf_test_token")
    monkeypatch.setitem(sys.modules, "huggingface_hub", SimpleNamespace(InferenceClient=FakeInferenceClient))
    result = factory.huggingface_json("system", "user", max_tokens=300)

    assert result == {"title": "HF optimized project"}
    assert seen["token"] == "hf_test_token"
    assert seen["kwargs"]["model"] == factory.HF_OPTIMIZER_MODEL
    assert seen["kwargs"]["response_format"] == {"type": "json_object"}
    assert seen["kwargs"]["max_tokens"] == 300


def test_huggingface_optimizer_preserves_project_identity(monkeypatch):
    monkeypatch.setenv("HF_TOKEN", "hf_test_token")
    original = factory.clean(minimal_spec())
    optimized = dict(original)
    optimized["unique_angle"] = "Improved: deterministic replay with structured behavioral diffs."
    monkeypatch.setattr(factory, "huggingface_json", lambda *a, **k: optimized)

    result, status = factory.optimize_with_huggingface(original)
    assert result["title"] == original["title"]
    assert result["slug"] == original["slug"]
    assert result["unique_angle"].startswith("Improved:")
    assert status["status"] == "optimized"


def test_huggingface_is_not_a_generation_fallback(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("HF_TOKEN", "hf_test_token")

    try:
        factory.generate("make one project")
    except RuntimeError as exc:
        assert "GROQ_API_KEY and/or GEMINI_API_KEY" in str(exc)
    else:
        raise AssertionError("Hugging Face must optimize, not generate the initial brief")


def test_optimizer_skips_when_token_missing(monkeypatch):
    monkeypatch.delenv("HF_TOKEN", raising=False)
    original = factory.clean(minimal_spec())
    result, status = factory.optimize_with_huggingface(original)
    assert result == original
    assert status["status"] == "skipped"

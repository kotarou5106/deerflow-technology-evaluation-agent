"""Live research E2E smoke test for Technology Evaluation Agent.

This test requires a real model configuration and live network access. It is
skipped by default and must be enabled explicitly:

    TECHNOLOGY_EVALUATION_LIVE_E2E=1 PYTHONPATH=. uv run pytest \
        tests/test_technology_evaluation_live_e2e.py -v -s
"""

from __future__ import annotations

import contextlib
import json
import os
import signal
import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LIVE_ENABLED = os.environ.get("TECHNOLOGY_EVALUATION_LIVE_E2E") == "1"
HAS_CONFIG = PROJECT_ROOT.joinpath("config.yaml").exists()
SKIP_REASON = "Technology evaluation live E2E requires TECHNOLOGY_EVALUATION_LIVE_E2E=1 and project-root config.yaml with valid model credentials"

LIVE_PROMPT = """Evaluate LangGraph for long-running AI agent workflows.

Use the Technology Research & Evaluation Agent workflow. Research real sources,
then call evaluation_scorecard, evaluation_report_validate, and
evaluation_report_assembly before the final answer. Produce both EvaluationReport
JSON and Markdown artifacts.
"""

REQUIRED_TOOLS = {
    "evaluation_scorecard",
    "evaluation_report_validate",
    "evaluation_report_assembly",
}

OPTIONAL_SUBAGENT_TOOLS = {"task"}
DEFAULT_LIVE_TIMEOUT_SECONDS = 900

REQUIRED_MARKDOWN_SECTIONS = [
    "# Technology Evaluation Report",
    "## 1. Executive Summary / 执行摘要",
    "## 2. Final Verdict / 最终结论",
    "## 3. Evaluation Context / 评估背景",
    "## 4. Technology Overview / 技术概览",
    "## 5. Core Capabilities / 核心能力",
    "## 6. Evidence Matrix / 证据矩阵",
    "## 7. Evaluation Scorecard / 评分卡",
    "## 8. Alternative Comparison / 替代方案对比",
    "## 9. Hands-on Validation / 实验验证",
    "## 10. Risk Register / 风险清单",
    "## 11. Adoption Recommendation / 采用建议",
    "## 12. Open Questions / 待确认问题",
    "## 13. References / 参考资料",
]


def _collect_tool_names(events: list[Any]) -> list[str]:
    tool_names: list[str] = []
    for event in events:
        if event.type != "messages-tuple" or event.data.get("type") != "ai":
            continue
        for tool_call in event.data.get("tool_calls", []):
            name = tool_call.get("name")
            if isinstance(name, str):
                tool_names.append(name)
    return tool_names


def _collect_final_artifacts(events: list[Any]) -> list[str]:
    artifacts: list[str] = []
    for event in events:
        if event.type == "values" and event.data.get("artifacts"):
            artifacts = list(event.data["artifacts"])
    return artifacts


def _artifact_lookup(artifacts: list[str], suffix: str) -> str:
    for artifact in artifacts:
        if artifact.endswith(suffix):
            return artifact
    raise AssertionError(f"Expected artifact ending with {suffix!r}, got {artifacts!r}")


def _client_artifact_path(virtual_path: str) -> str:
    return virtual_path.removeprefix("/")


def _live_timeout_seconds() -> int:
    value = os.environ.get("TECHNOLOGY_EVALUATION_LIVE_E2E_TIMEOUT_SECONDS")
    if value is None:
        return DEFAULT_LIVE_TIMEOUT_SECONDS
    try:
        return max(0, int(value))
    except ValueError:
        return DEFAULT_LIVE_TIMEOUT_SECONDS


@contextlib.contextmanager
def _live_smoke_timeout() -> Iterator[None]:
    timeout_seconds = _live_timeout_seconds()
    if timeout_seconds <= 0 or not hasattr(signal, "SIGALRM"):
        yield
        return

    previous_handler = signal.getsignal(signal.SIGALRM)

    def _raise_timeout(signum: int, frame: Any) -> None:
        raise TimeoutError(f"Technology evaluation live E2E exceeded {timeout_seconds} seconds")

    signal.signal(signal.SIGALRM, _raise_timeout)
    signal.alarm(timeout_seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous_handler)


@pytest.mark.skipif(not LIVE_ENABLED or not HAS_CONFIG, reason=SKIP_REASON)
def test_live_langgraph_research_generates_structured_artifacts():
    """Smoke-test the real agent path without grading report content depth."""
    load_dotenv(PROJECT_ROOT / ".env")

    from deerflow.client import DeerFlowClient
    from deerflow.evaluation.schemas import EvaluationReport

    thread_id = f"tech-eval-live-{uuid.uuid4().hex[:8]}"
    client = DeerFlowClient(thinking_enabled=False, subagent_enabled=True)

    with _live_smoke_timeout():
        events = list(client.stream(LIVE_PROMPT, thread_id=thread_id, recursion_limit=180))

    tool_names = _collect_tool_names(events)
    artifacts = _collect_final_artifacts(events)
    print("thread_id:", thread_id)
    print("tool_names:", tool_names)
    print("artifacts:", artifacts)
    print("optional_subagent_tools:", sorted(OPTIONAL_SUBAGENT_TOOLS.intersection(tool_names)))

    missing_tools = REQUIRED_TOOLS.difference(tool_names)
    assert not missing_tools, f"Missing required technology evaluation tools: {sorted(missing_tools)}"
    assert any(name in {"web_search", "web_fetch"} for name in tool_names), "Expected at least one live research tool call such as web_search or web_fetch"

    json_artifact = _artifact_lookup(artifacts, ".json")
    markdown_artifact = _artifact_lookup(artifacts, ".md")

    json_bytes, json_mime = client.get_artifact(thread_id, _client_artifact_path(json_artifact))
    markdown_bytes, markdown_mime = client.get_artifact(thread_id, _client_artifact_path(markdown_artifact))
    assert "json" in json_mime
    assert markdown_mime in {"text/markdown", "text/plain", "application/octet-stream"}

    report_payload = json.loads(json_bytes.decode("utf-8"))
    report = EvaluationReport.model_validate(report_payload)
    markdown = markdown_bytes.decode("utf-8")

    for section in REQUIRED_MARKDOWN_SECTIONS:
        assert section in markdown

    assert str(report.final_score) in markdown
    assert report.verdict in markdown

    if "Consistency Notes / 一致性备注" in markdown:
        assert "| Level | Code | Message | Path | Referenced ID |" in markdown

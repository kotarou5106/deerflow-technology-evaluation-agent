import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from deerflow.evaluation.schemas import EvaluationReport
from deerflow.tools.builtins import evaluation_report_artifact_tool
from deerflow.tools.builtins.evaluation_report_artifact_tool import write_evaluation_report_artifact
from deerflow.tools.tools import get_available_tools


def _criterion() -> dict:
    return {
        "name": "Problem Fit",
        "description": "Fit for long-running agent workflows.",
        "weight": 1.0,
        "score": 4.2,
        "rationale": "Evidence supports the target workflow with manageable constraints.",
        "evidence_ids": ["ev-1"],
    }


def _evidence_item() -> dict:
    return {
        "id": "ev-1",
        "claim": "The technology supports durable graph-based agent orchestration.",
        "evidence_summary": "Official docs describe persisted graph execution and recovery.",
        "source_title": "Official documentation",
        "source_url": "https://example.com/docs",
        "source_type": "official_docs",
        "trust_level": "high",
        "support_status": "supports",
        "confidence": 0.9,
        "relevance": 0.95,
        "notes": "Needs validation in the user's deployment environment.",
    }


def _alternative() -> dict:
    return {
        "name": "Alternative Agent Framework",
        "description": "Comparable multi-agent workflow framework.",
        "category": "agent_framework",
        "strengths": ["Simple onboarding"],
        "weaknesses": ["Less durable execution evidence"],
        "best_fit_use_cases": ["Small prototypes"],
        "risks": ["Migration cost"],
    }


def _experiment() -> dict:
    return {
        "name": "Quickstart reproducibility",
        "description": "Install package and run documented quickstart.",
        "command": "python quickstart.py",
        "success": True,
        "logs_summary": "Quickstart completed without errors.",
        "reproducibility_score": 0.8,
        "notes": "Run again in the target CI image before adoption.",
    }


def _report() -> dict:
    return {
        "title": "LangGraph Technology Evaluation",
        "target_technology": "LangGraph",
        "evaluation_context": "Long-running AI agent workflows",
        "verdict": "Recommended",
        "final_score": 4.2,
        "criteria": [_criterion()],
        "evidence_items": [_evidence_item()],
        "alternatives": [_alternative()],
        "experiments": [_experiment()],
        "risks": ["Operational complexity must be validated before production rollout."],
        "recommendation": "Adopt for a constrained pilot, then expand after operational validation.",
    }


def _make_minimal_config():
    config = MagicMock()
    config.tools = []
    config.models = []
    config.tool_search.enabled = False
    config.skill_evolution.enabled = False
    config.sandbox = MagicMock()
    config.acp_agents = {}
    return config


def test_evaluation_report_artifact_tool_can_be_imported():
    assert evaluation_report_artifact_tool.name == "evaluation_report_artifact"


def test_evaluation_report_artifact_tool_is_available_through_builtin_tools_path():
    config = _make_minimal_config()

    with patch("deerflow.tools.tools.is_host_bash_allowed", return_value=True):
        tools = get_available_tools(include_mcp=False, app_config=config)

    assert "evaluation_report_artifact" in [tool.name for tool in tools]


def test_valid_input_generates_evaluation_report_json(tmp_path: Path):
    artifact = write_evaluation_report_artifact(tmp_path, _report())
    payload = json.loads(Path(artifact["path"]).read_text(encoding="utf-8"))
    parsed = EvaluationReport.model_validate(payload)

    assert artifact["filename"] == "evaluation_report_langgraph.json"
    assert artifact["virtual_path"] == "/mnt/user-data/outputs/evaluation_report_langgraph.json"
    assert parsed.target_technology == "LangGraph"
    assert parsed.verdict == "Recommended"
    assert parsed.final_score == 4.2
    assert parsed.criteria
    assert parsed.evidence_items
    assert parsed.alternatives
    assert parsed.experiments
    assert parsed.risks
    assert parsed.recommendation


def test_invalid_input_is_rejected_by_evaluation_report_schema(tmp_path: Path):
    report = _report()
    report.pop("recommendation")

    with pytest.raises(ValidationError):
        write_evaluation_report_artifact(tmp_path, report)


def test_custom_filename_rejects_path_traversal(tmp_path: Path):
    with pytest.raises(ValueError):
        write_evaluation_report_artifact(tmp_path, _report(), filename="../evil.json")


def test_generated_filename_sanitizes_target_technology(tmp_path: Path):
    report = _report()
    report["target_technology"] = "LangGraph/../../Enterprise Agent SDK"

    artifact = write_evaluation_report_artifact(tmp_path, report)

    assert artifact["filename"] == "evaluation_report_langgraph_enterprise_agent_sdk.json"
    assert Path(artifact["path"]).parent == tmp_path.resolve()

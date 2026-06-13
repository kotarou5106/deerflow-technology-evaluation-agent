import json
from pathlib import Path

import pytest

from deerflow.evaluation import check_evaluation_report_consistency
from deerflow.evaluation.consistency import ConsistencyCheckResult, ConsistencyIssue
from deerflow.tools.builtins.evaluation_report_assembly_tool import write_assembled_evaluation_report


def _report() -> dict:
    return {
        "title": "LangGraph Technology Evaluation",
        "target_technology": "LangGraph",
        "evaluation_context": "Long-running AI agent workflows",
        "verdict": "Recommended with constraints",
        "final_score": 3.8,
        "criteria": [
            {
                "name": "Problem Fit",
                "description": "Fit for durable workflow orchestration.",
                "weight": 1.0,
                "score": 3.8,
                "rationale": "Evidence supports the main workflow requirement.",
                "evidence_ids": ["ev-1"],
            }
        ],
        "evidence_items": [
            {
                "id": "ev-1",
                "claim": "LangGraph supports durable agent workflows.",
                "evidence_summary": "Official docs describe persisted graph execution.",
                "source_title": "LangGraph Docs",
                "source_url": "https://example.com/langgraph/docs",
                "source_type": "official_docs",
                "trust_level": "high",
                "support_status": "supports",
                "confidence": 0.9,
                "relevance": 0.95,
                "notes": "Verify target deployment behavior.",
            },
            {
                "id": "ev-2",
                "claim": "Operations require graph-specific debugging practices.",
                "evidence_summary": "Engineering blog discusses tracing needs.",
                "source_title": "Production Agent Engineering",
                "source_url": "https://example.com/engineering/agents",
                "source_type": "engineering_blog",
                "trust_level": "medium",
                "support_status": "partially_supports",
                "confidence": 0.75,
                "relevance": 0.8,
                "notes": None,
            },
            {
                "id": "ev-3",
                "claim": "Teams should validate checkpoint recovery.",
                "evidence_summary": "Operational recovery depends on target storage.",
                "source_title": "Recovery Notes",
                "source_url": "https://example.com/recovery",
                "source_type": "engineering_blog",
                "trust_level": "medium",
                "support_status": "unclear",
                "confidence": 0.65,
                "relevance": 0.85,
                "notes": None,
            },
        ],
        "alternatives": [],
        "experiments": [],
        "risks": ["Operational complexity must be validated."],
        "recommendation": "Use for a constrained pilot before broad production adoption.",
        "core_capabilities": [
            {
                "name": "Durable orchestration",
                "description": "Coordinates stateful agent steps with persistence.",
                "evidence_ids": ["ev-1"],
                "maturity_level": "production-adjacent",
                "limitations": ["Requires graph-specific debugging practices"],
            }
        ],
        "risk_register": [
            {
                "name": "Operational learning curve",
                "description": "Teams must learn graph debugging and state inspection.",
                "severity": "medium",
                "likelihood": "medium",
                "mitigation": "Run a pilot and define observability practices.",
                "evidence_ids": ["ev-2"],
            }
        ],
        "references": [
            {
                "title": "LangGraph Docs",
                "url": "https://example.com/langgraph/docs",
                "source_type": "official_docs",
            }
        ],
    }


def _codes(result: ConsistencyCheckResult) -> set[str]:
    return {issue.code for issue in [*result.errors, *result.warnings]}


def test_consistency_checker_can_be_imported():
    assert callable(check_evaluation_report_consistency)
    assert ConsistencyIssue(level="warning", code="x", message="msg").level == "warning"


def test_valid_report_passes_consistency_check():
    result = check_evaluation_report_consistency(_report())

    assert result.passed
    assert result.errors == []
    assert result.warnings == []


def test_missing_criteria_evidence_id_returns_error():
    report = _report()
    report["criteria"][0]["evidence_ids"] = ["missing"]

    result = check_evaluation_report_consistency(report)

    assert not result.passed
    assert "missing_evidence_id" in _codes(result)
    assert result.errors[0].referenced_id == "missing"


def test_missing_core_capability_evidence_id_returns_error():
    report = _report()
    report["core_capabilities"][0]["evidence_ids"] = ["missing"]

    result = check_evaluation_report_consistency(report)

    assert not result.passed
    assert "missing_evidence_id" in _codes(result)


def test_missing_risk_register_evidence_id_returns_error():
    report = _report()
    report["risk_register"][0]["evidence_ids"] = ["missing"]

    result = check_evaluation_report_consistency(report)

    assert not result.passed
    assert "missing_evidence_id" in _codes(result)


def test_recommended_with_too_little_evidence_returns_warning():
    report = _report()
    report["verdict"] = "Recommended"
    report["evidence_items"] = report["evidence_items"][:1]
    report["criteria"][0]["evidence_ids"] = ["ev-1"]
    report["core_capabilities"][0]["evidence_ids"] = ["ev-1"]
    report["risk_register"][0]["evidence_ids"] = ["ev-1"]

    result = check_evaluation_report_consistency(report)

    assert result.passed
    assert "recommended_low_evidence" in _codes(result)


def test_high_score_with_too_little_evidence_returns_warning():
    report = _report()
    report["final_score"] = 4.5
    report["evidence_items"] = report["evidence_items"][:1]
    report["criteria"][0]["evidence_ids"] = ["ev-1"]
    report["core_capabilities"][0]["evidence_ids"] = ["ev-1"]
    report["risk_register"][0]["evidence_ids"] = ["ev-1"]

    result = check_evaluation_report_consistency(report)

    assert result.passed
    assert "high_score_low_evidence" in _codes(result)


def test_missing_source_metadata_returns_warnings():
    report = _report()
    report["evidence_items"][0]["source_url"] = ""
    report["evidence_items"][0]["source_type"] = ""
    report["evidence_items"][0]["trust_level"] = ""

    result = check_evaluation_report_consistency(report)

    assert result.passed
    assert {"missing_source_url", "missing_source_type", "missing_trust_level"} <= _codes(result)


def test_invalid_support_status_and_confidence_return_warnings():
    report = _report()
    report["evidence_items"][0]["support_status"] = "certainly_true"
    report["evidence_items"][0]["confidence"] = "absolute"

    result = check_evaluation_report_consistency(report)

    assert result.passed
    assert {"invalid_support_status", "invalid_confidence"} <= _codes(result)


def test_invalid_risk_severity_and_likelihood_return_warnings():
    report = _report()
    report["risk_register"][0]["severity"] = "severe-ish"
    report["risk_register"][0]["likelihood"] = ""

    result = check_evaluation_report_consistency(report)

    assert result.passed
    assert {"invalid_risk_severity", "invalid_risk_likelihood"} <= _codes(result)


def test_duplicate_references_return_warning():
    report = _report()
    report["references"].append(
        {
            "title": "Duplicate Docs",
            "url": "https://example.com/langgraph/docs",
            "source_type": "official_docs",
        }
    )

    result = check_evaluation_report_consistency(report)

    assert result.passed
    assert "duplicate_reference_url" in _codes(result)


def test_assembly_consistency_error_writes_no_artifacts(tmp_path: Path):
    report = _report()
    report["criteria"][0]["evidence_ids"] = ["missing"]

    with pytest.raises(ValueError, match="consistency check failed"):
        write_assembled_evaluation_report(tmp_path, report)

    assert list(tmp_path.iterdir()) == []


def test_assembly_consistency_warning_still_writes_artifacts(tmp_path: Path):
    report = _report()
    report["final_score"] = 4.5
    report["evidence_items"] = report["evidence_items"][:1]
    report["criteria"][0]["evidence_ids"] = ["ev-1"]
    report["core_capabilities"][0]["evidence_ids"] = ["ev-1"]
    report["risk_register"][0]["evidence_ids"] = ["ev-1"]

    artifact = write_assembled_evaluation_report(tmp_path, report)
    markdown = Path(artifact["markdown_artifact"]["path"]).read_text(encoding="utf-8")

    assert Path(artifact["json_artifact"]["path"]).is_file()
    assert Path(artifact["markdown_artifact"]["path"]).is_file()
    assert artifact["consistency_check"]["passed"] is True
    assert artifact["consistency_check"]["warnings"]
    assert "### Consistency Notes / 一致性备注" in markdown
    assert "high_score_low_evidence" in markdown


def test_assembly_warning_does_not_write_warnings_into_json_artifact(tmp_path: Path):
    report = _report()
    report["final_score"] = 4.5
    report["evidence_items"] = report["evidence_items"][:1]
    report["criteria"][0]["evidence_ids"] = ["ev-1"]
    report["core_capabilities"][0]["evidence_ids"] = ["ev-1"]
    report["risk_register"][0]["evidence_ids"] = ["ev-1"]

    artifact = write_assembled_evaluation_report(tmp_path, report)
    payload = json.loads(Path(artifact["json_artifact"]["path"]).read_text(encoding="utf-8"))

    assert "consistency_check" not in payload
    assert "warnings" not in payload
    assert payload["target_technology"] == "LangGraph"


def test_report_without_evidence_item_ids_remains_compatible():
    report = _report()
    report["evidence_items"][0].pop("id")
    report["evidence_items"][1].pop("id")
    report["evidence_items"][2].pop("id")
    report["criteria"][0]["evidence_ids"] = []
    report["core_capabilities"][0]["evidence_ids"] = []
    report["risk_register"][0]["evidence_ids"] = []

    result = check_evaluation_report_consistency(report)

    assert result.passed
    assert "missing_evidence_id" in _codes(result)

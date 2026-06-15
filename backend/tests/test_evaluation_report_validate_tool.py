from pathlib import Path
from unittest.mock import MagicMock, patch

from deerflow.tools.builtins import evaluation_report_validate_tool
from deerflow.tools.builtins.evaluation_report_validate_tool import validate_evaluation_report_payload
from deerflow.tools.tools import get_available_tools


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


def _make_minimal_config():
    config = MagicMock()
    config.tools = []
    config.models = []
    config.tool_search.enabled = False
    config.skill_evolution.enabled = False
    config.sandbox = MagicMock()
    config.acp_agents = {}
    return config


def test_evaluation_report_validate_tool_can_be_imported():
    assert evaluation_report_validate_tool.name == "evaluation_report_validate"


def test_evaluation_report_validate_tool_is_available_through_builtin_tools_path():
    config = _make_minimal_config()

    with patch("deerflow.tools.tools.is_host_bash_allowed", return_value=True):
        tools = get_available_tools(include_mcp=False, app_config=config)

    assert "evaluation_report_validate" in [tool.name for tool in tools]


def test_valid_report_returns_passed_true():
    result = evaluation_report_validate_tool.invoke({"report": _report()})

    assert result["passed"] is True
    assert result["error_count"] == 0
    assert result["warning_count"] == 0
    assert result["errors"] == []
    assert result["warnings"] == []


def test_report_with_warning_returns_passed_true_and_next_actions():
    report = _report()
    report["final_score"] = 4.5
    report["evidence_items"] = report["evidence_items"][:1]
    report["criteria"][0]["evidence_ids"] = ["ev-1"]
    report["core_capabilities"][0]["evidence_ids"] = ["ev-1"]
    report["risk_register"][0]["evidence_ids"] = ["ev-1"]

    result = validate_evaluation_report_payload(report)

    assert result["passed"] is True
    assert result["error_count"] == 0
    assert result["warning_count"] > 0
    assert any(issue["code"] == "high_score_low_evidence" for issue in result["warnings"])
    assert "Add more evidence or lower the score/verdict." in result["next_actions"]


def test_report_with_consistency_error_returns_passed_false():
    report = _report()
    report["criteria"][0]["evidence_ids"] = ["missing"]

    result = validate_evaluation_report_payload(report)

    assert result["passed"] is False
    assert result["error_count"] == 1
    assert result["warning_count"] == 0
    assert result["errors"][0]["code"] == "missing_evidence_id"
    assert "Fix evidence_ids so they point to existing evidence_items." in result["next_actions"]


def test_schema_validation_failure_returns_error_result():
    report = _report()
    report.pop("target_technology")

    result = validate_evaluation_report_payload(report)

    assert result["passed"] is False
    assert result["error_count"] == 1
    assert result["warning_count"] == 0
    assert result["errors"][0]["code"] == "schema_validation_error"
    assert result["errors"][0]["path"] == "target_technology"
    assert "Field required" in result["errors"][0]["message"]
    assert "Fix the EvaluationReport payload so it matches the required schema." in result["next_actions"]


def test_schema_validation_guides_loose_payload_shapes():
    report = _report()
    report["executive_summary"] = "Recommended with constraints."
    report["technology_overview"] = "Graph workflow framework."
    report["evidence_items"][0]["relevance"] = "high"
    report["open_questions"] = ["Does recovery meet the target RTO?"]
    report["adoption_plan"] = {
        "recommendation": "Pilot first.",
        "validation_plan": "Run recovery tests.",
    }

    result = validate_evaluation_report_payload(report)

    assert result["passed"] is False
    errors_by_path = {error["path"]: error for error in result["errors"]}
    assert "executive_summary" in errors_by_path
    assert "technology_overview" in errors_by_path
    assert "evidence_items[0].relevance" in errors_by_path
    assert "open_questions[0]" in errors_by_path
    assert "adoption_plan.validation_plan" in errors_by_path
    assert "Use executive_summary as an object" in errors_by_path["executive_summary"]["fix_hint"]
    assert "Use relevance as a JSON number" in errors_by_path["evidence_items[0].relevance"]["fix_hint"]
    assert "Use open_questions as a list of objects" in errors_by_path["open_questions[0]"]["fix_hint"]
    assert "Use adoption_plan.validation_plan as a list" in errors_by_path["adoption_plan.validation_plan"]["fix_hint"]
    assert any("Use executive_summary as an object" in action for action in result["next_actions"])


def test_schema_validation_guides_missing_live_run_fields():
    report = _report()
    report.pop("title")
    report["evidence_items"][0].pop("evidence_summary")
    report["evidence_items"][0].pop("source_title")
    report["evidence_items"][0].pop("confidence")
    report["alternatives"] = [
        {
            "name": "AutoGen",
            "description": "Multi-agent conversation framework.",
            "strengths": ["Flexible collaboration patterns."],
            "weaknesses": ["Durability needs validation."],
            "best_fit_use_cases": ["Research prototypes."],
            "risks": ["Extra infrastructure may be required."],
        }
    ]
    report["risk_register"] = [
        {
            "severity": "medium",
            "likelihood": "medium",
            "mitigation": "Run a pilot.",
            "evidence_ids": ["ev-2"],
        }
    ]

    result = validate_evaluation_report_payload(report)

    assert result["passed"] is False
    errors_by_path = {error["path"]: error for error in result["errors"]}
    for path in [
        "title",
        "evidence_items[0].evidence_summary",
        "evidence_items[0].source_title",
        "evidence_items[0].confidence",
        "alternatives[0].category",
        "risk_register[0].name",
        "risk_register[0].description",
    ]:
        assert path in errors_by_path
        assert errors_by_path[path]["fix_hint"]


def test_validate_tool_does_not_write_artifacts(tmp_path: Path):
    result = validate_evaluation_report_payload(_report())

    assert result["passed"] is True
    assert list(tmp_path.iterdir()) == []


def test_next_actions_are_deduplicated():
    report = _report()
    report["evidence_items"][0]["source_url"] = ""
    report["evidence_items"][1]["source_url"] = ""

    result = validate_evaluation_report_payload(report)

    assert result["next_actions"].count("Add source_url for the evidence item.") == 1

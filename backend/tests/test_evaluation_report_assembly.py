import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from deerflow.evaluation import render_evaluation_report_markdown
from deerflow.evaluation.consistency import ConsistencyIssue
from deerflow.evaluation.schemas import (
    AdoptionPlan,
    CoreCapability,
    EvaluationReport,
    ExecutiveSummary,
    OpenQuestion,
    ReferenceItem,
    RiskItem,
    TechnologyOverview,
)
from deerflow.tools.builtins import evaluation_report_assembly_tool
from deerflow.tools.builtins.evaluation_report_assembly_tool import write_assembled_evaluation_report
from deerflow.tools.tools import get_available_tools

FIXED_SECTIONS = [
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
                "weight": 0.6,
                "score": 4.0,
                "rationale": "Evidence supports the main workflow requirement.",
                "evidence_ids": ["ev-1"],
            },
            {
                "name": "Operational Complexity",
                "description": "Deployment and debugging burden.",
                "weight": 0.4,
                "score": 3.5,
                "rationale": "Some operational risks remain.",
                "evidence_ids": ["ev-2"],
            },
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
                "evidence_summary": "Engineering blog discusses tracing and state inspection needs.",
                "source_title": "Production Agent Engineering",
                "source_url": "https://example.com/engineering/agents",
                "source_type": "engineering_blog",
                "trust_level": "medium",
                "support_status": "partially_supports",
                "confidence": 0.75,
                "relevance": 0.8,
                "notes": None,
            },
        ],
        "alternatives": [
            {
                "name": "AutoGen",
                "description": "Multi-agent conversation framework.",
                "category": "agent_framework",
                "strengths": ["Flexible conversation patterns"],
                "weaknesses": ["Different durability model"],
                "best_fit_use_cases": ["Research prototypes"],
                "risks": ["Migration effort"],
            }
        ],
        "experiments": [
            {
                "name": "Quickstart reproducibility",
                "description": "Run documented quickstart.",
                "command": "python quickstart.py",
                "success": True,
                "logs_summary": "Quickstart completed.",
                "reproducibility_score": 0.8,
                "notes": "Repeat in CI image.",
            }
        ],
        "risks": ["Operational complexity must be validated before production rollout."],
        "recommendation": "Use for a constrained pilot before broad production adoption.",
    }


def _empty_report() -> dict:
    report = _report()
    report["criteria"] = []
    report["evidence_items"] = []
    report["alternatives"] = []
    report["experiments"] = []
    report["risks"] = []
    return report


def _structured_report() -> dict:
    report = _report()
    report.update(
        {
            "executive_summary": {
                "one_sentence_verdict": "Adopt LangGraph for durable workflows after a constrained pilot.",
                "key_reasons": ["Strong workflow fit", "Evidence-backed persistence model"],
                "major_risks": ["Operational learning curve"],
                "best_fit": "Teams building long-running, stateful agent workflows.",
            },
            "technology_overview": {
                "description": "LangGraph is a graph-based orchestration framework for agent workflows.",
                "problem_addressed": "Durable orchestration for stateful agent execution.",
                "primary_use_cases": ["Long-running agents", "Human-in-the-loop workflows"],
                "key_features": ["Graph execution", "State persistence"],
                "target_users": ["AI platform teams", "Agent application engineers"],
            },
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
            "open_questions": [
                {
                    "question": "Does checkpoint storage meet internal recovery objectives?",
                    "why_it_matters": "Recovery behavior is decision-critical for production workflows.",
                    "suggested_validation": "Run failure injection against the target deployment.",
                }
            ],
            "references": [
                {
                    "title": "LangGraph Persistence Docs",
                    "url": "https://example.com/langgraph/persistence",
                    "source_type": "official_docs",
                    "publisher": "LangChain",
                    "accessed_at": "2026-06-13",
                    "notes": "Primary source for persistence claims.",
                }
            ],
            "adoption_plan": {
                "recommendation": "Run a constrained production-like pilot.",
                "suggested_next_steps": ["Build a thin vertical workflow", "Instrument checkpoints"],
                "validation_plan": ["Run quickstart", "Run failure recovery test"],
                "rollout_strategy": "Pilot one workflow before expanding.",
                "decision_deadline": "After pilot evidence is collected.",
            },
        }
    )
    return report


def _make_minimal_config():
    config = MagicMock()
    config.tools = []
    config.models = []
    config.tool_search.enabled = False
    config.skill_evolution.enabled = False
    config.sandbox = MagicMock()
    config.acp_agents = {}
    return config


def test_report_renderer_can_be_imported():
    assert callable(render_evaluation_report_markdown)


def test_new_schema_classes_can_be_imported_and_instantiated():
    assert CoreCapability(name="Capability", description="Description").name == "Capability"
    assert RiskItem(name="Risk", description="Description", severity="high", likelihood="medium").severity == "high"
    assert OpenQuestion(question="Question?", why_it_matters="Decision critical").question == "Question?"
    assert ReferenceItem(title="Docs", url="https://example.com", source_type="official_docs").title == "Docs"
    assert TechnologyOverview(description="Overview").description == "Overview"
    assert ExecutiveSummary(one_sentence_verdict="Proceed with constraints").one_sentence_verdict == "Proceed with constraints"
    assert AdoptionPlan(recommendation="Pilot first").recommendation == "Pilot first"


def test_evaluation_report_accepts_new_structured_fields():
    parsed = EvaluationReport.model_validate(_structured_report())

    assert parsed.executive_summary is not None
    assert parsed.technology_overview is not None
    assert parsed.core_capabilities[0].evidence_ids == ["ev-1"]
    assert parsed.risk_register[0].mitigation == "Run a pilot and define observability practices."
    assert parsed.open_questions[0].suggested_validation == "Run failure injection against the target deployment."
    assert parsed.references[0].publisher == "LangChain"
    assert parsed.adoption_plan is not None


def test_old_evaluation_report_payload_remains_valid():
    parsed = EvaluationReport.model_validate(_report())

    assert parsed.executive_summary is None
    assert parsed.technology_overview is None
    assert parsed.core_capabilities == []
    assert parsed.risk_register == []
    assert parsed.open_questions == []
    assert parsed.references == []
    assert parsed.adoption_plan is None


def test_renderer_outputs_fixed_sections():
    markdown = render_evaluation_report_markdown(_report())

    for section in FIXED_SECTIONS:
        assert section in markdown


def test_renderer_old_call_does_not_include_consistency_notes():
    markdown = render_evaluation_report_markdown(_report())

    assert "### Consistency Notes / 一致性备注" not in markdown


def test_renderer_accepts_consistency_warnings():
    markdown = render_evaluation_report_markdown(
        _report(),
        consistency_warnings=[
            ConsistencyIssue(
                level="warning",
                code="high_score_low_evidence",
                message="final_score is high, but evidence is limited.",
                path="final_score",
                referenced_id=None,
            )
        ],
    )

    assert "### Consistency Notes / 一致性备注" in markdown
    assert "| Level | Code | Message | Path | Referenced ID |" in markdown
    assert "warning" in markdown
    assert "high_score_low_evidence" in markdown
    assert "final_score is high, but evidence is limited." in markdown
    assert "final_score" in markdown
    assert "| warning | high_score_low_evidence | final_score is high, but evidence is limited. | final_score | - |" in markdown


def test_renderer_accepts_consistency_warning_dicts():
    markdown = render_evaluation_report_markdown(
        _report(),
        consistency_warnings=[
            {
                "level": "warning",
                "code": "missing_source_url",
                "message": "Evidence item is missing source_url.",
                "path": "evidence_items[0].source_url",
                "referenced_id": "ev-1",
            }
        ],
    )

    assert "missing_source_url" in markdown
    assert "evidence_items[0].source_url" in markdown
    assert "ev-1" in markdown


def test_renderer_uses_report_verdict_and_final_score():
    markdown = render_evaluation_report_markdown(_report())

    assert "**Verdict:** Recommended with constraints" in markdown
    assert "**Final score:** 3.80" in markdown


def test_renderer_includes_structured_report_fields():
    markdown = render_evaluation_report_markdown(_report())

    assert "Problem Fit" in markdown
    assert "LangGraph supports durable agent workflows." in markdown
    assert "AutoGen" in markdown
    assert "Quickstart reproducibility" in markdown
    assert "Operational complexity must be validated" in markdown
    assert "Use for a constrained pilot" in markdown


def test_renderer_renders_executive_summary():
    markdown = render_evaluation_report_markdown(_structured_report())

    assert "Adopt LangGraph for durable workflows after a constrained pilot." in markdown
    assert "Strong workflow fit" in markdown
    assert "Teams building long-running, stateful agent workflows." in markdown


def test_renderer_renders_technology_overview():
    markdown = render_evaluation_report_markdown(_structured_report())

    assert "LangGraph is a graph-based orchestration framework" in markdown
    assert "Human-in-the-loop workflows" in markdown
    assert "Agent application engineers" in markdown


def test_renderer_renders_core_capabilities():
    markdown = render_evaluation_report_markdown(_structured_report())

    assert "Durable orchestration" in markdown
    assert "production-adjacent" in markdown
    assert "Requires graph-specific debugging practices" in markdown


def test_renderer_renders_risk_register():
    markdown = render_evaluation_report_markdown(_structured_report())

    assert "Operational learning curve" in markdown
    assert "Run a pilot and define observability practices." in markdown


def test_renderer_renders_open_questions():
    markdown = render_evaluation_report_markdown(_structured_report())

    assert "Does checkpoint storage meet internal recovery objectives?" in markdown
    assert "Run failure injection against the target deployment." in markdown


def test_renderer_renders_references():
    markdown = render_evaluation_report_markdown(_structured_report())

    assert "LangGraph Persistence Docs" in markdown
    assert "https://example.com/langgraph/persistence" in markdown
    assert "Primary source for persistence claims." in markdown


def test_renderer_falls_back_to_evidence_sources_when_references_empty():
    markdown = render_evaluation_report_markdown(_report())

    assert "LangGraph Docs" in markdown
    assert "Derived from evidence item ev-1" in markdown


def test_renderer_outputs_no_data_provided_for_empty_sections():
    markdown = render_evaluation_report_markdown(_empty_report())

    assert markdown.count("No data provided") >= 6


def test_evaluation_report_assembly_tool_can_be_imported():
    assert evaluation_report_assembly_tool.name == "evaluation_report_assembly"


def test_evaluation_report_assembly_tool_is_available_through_builtin_tools_path():
    config = _make_minimal_config()

    with patch("deerflow.tools.tools.is_host_bash_allowed", return_value=True):
        tools = get_available_tools(include_mcp=False, app_config=config)

    assert "evaluation_report_assembly" in [tool.name for tool in tools]


def test_assembly_writes_json_and_markdown_from_same_payload(tmp_path: Path):
    artifact = write_assembled_evaluation_report(tmp_path, _report())
    json_path = Path(artifact["json_artifact"]["path"])
    markdown_path = Path(artifact["markdown_artifact"]["path"])

    parsed = EvaluationReport.model_validate(json.loads(json_path.read_text(encoding="utf-8")))
    markdown = markdown_path.read_text(encoding="utf-8")

    assert json_path.name == "evaluation_report_langgraph.json"
    assert markdown_path.name == "technology_evaluation_report_langgraph.md"
    assert artifact["artifacts"] == [
        "/mnt/user-data/outputs/evaluation_report_langgraph.json",
        "/mnt/user-data/outputs/technology_evaluation_report_langgraph.md",
    ]
    assert parsed.verdict == artifact["verdict"] == "Recommended with constraints"
    assert parsed.final_score == artifact["final_score"] == 3.8
    assert "**Verdict:** Recommended with constraints" in markdown
    assert "**Final score:** 3.80" in markdown
    assert parsed.criteria[0].name in markdown
    assert parsed.evidence_items[0].claim in markdown


def test_assembly_json_preserves_new_structured_fields(tmp_path: Path):
    artifact = write_assembled_evaluation_report(tmp_path, _structured_report())
    json_path = Path(artifact["json_artifact"]["path"])
    markdown_path = Path(artifact["markdown_artifact"]["path"])

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")

    assert payload["executive_summary"]["one_sentence_verdict"] == "Adopt LangGraph for durable workflows after a constrained pilot."
    assert payload["technology_overview"]["description"].startswith("LangGraph is a graph-based")
    assert payload["core_capabilities"][0]["name"] == "Durable orchestration"
    assert payload["risk_register"][0]["name"] == "Operational learning curve"
    assert payload["open_questions"][0]["question"] == "Does checkpoint storage meet internal recovery objectives?"
    assert payload["references"][0]["publisher"] == "LangChain"
    assert payload["adoption_plan"]["recommendation"] == "Run a constrained production-like pilot."
    assert "Run a constrained production-like pilot." in markdown


def test_assembly_rejects_path_traversal_filename(tmp_path: Path):
    with pytest.raises(ValueError):
        write_assembled_evaluation_report(tmp_path, _report(), markdown_filename="../report.md")


def test_assembly_schema_failure_writes_no_partial_files(tmp_path: Path):
    report = _report()
    report.pop("target_technology")

    with pytest.raises(ValidationError):
        write_assembled_evaluation_report(tmp_path, report)

    assert list(tmp_path.iterdir()) == []

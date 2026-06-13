from unittest.mock import MagicMock, patch

from deerflow.tools.builtins import evaluation_scorecard_tool
from deerflow.tools.tools import get_available_tools


def _criterion(name: str, weight: float, score: float, evidence_ids: list[str] | None = None) -> dict:
    return {
        "name": name,
        "description": f"{name} assessment",
        "weight": weight,
        "score": score,
        "rationale": f"{name} rationale",
        "evidence_ids": evidence_ids if evidence_ids is not None else [f"ev-{name}"],
    }


def _criteria(score: float) -> list[dict]:
    return [
        _criterion("problem-fit", 0.5, score),
        _criterion("maturity", 0.3, score),
        _criterion("operations", 0.2, score),
    ]


def _invoke(criteria: list[dict], *, evidence_count: int | None = 3, critical_risks: list[str] | None = None) -> dict:
    return evaluation_scorecard_tool.invoke(
        {
            "target_technology": "LangGraph",
            "evaluation_context": "Long-running AI agent workflows",
            "criteria": criteria,
            "evidence_count": evidence_count,
            "critical_risks": critical_risks,
        }
    )


def _make_minimal_config():
    config = MagicMock()
    config.tools = []
    config.models = []
    config.tool_search.enabled = False
    config.skill_evolution.enabled = False
    config.sandbox = MagicMock()
    config.acp_agents = {}
    return config


def test_evaluation_scorecard_tool_can_be_imported():
    assert evaluation_scorecard_tool.name == "evaluation_scorecard"


def test_evaluation_scorecard_tool_is_available_through_builtin_tools_path():
    config = _make_minimal_config()

    with patch("deerflow.tools.tools.is_host_bash_allowed", return_value=True):
        tools = get_available_tools(include_mcp=False, app_config=config)

    assert "evaluation_scorecard" in [tool.name for tool in tools]


def test_evaluation_scorecard_tool_returns_score_and_verdict():
    result = _invoke(_criteria(4.2))

    assert result["final_score"] == 4.2
    assert result["verdict"] == "Recommended"
    assert result["target_technology"] == "LangGraph"


def test_high_score_without_critical_risk_returns_recommended():
    result = _invoke(_criteria(4.5))

    assert result["verdict"] == "Recommended"


def test_medium_score_returns_recommended_with_constraints():
    result = _invoke(_criteria(3.5))

    assert result["verdict"] == "Recommended with constraints"


def test_low_score_returns_not_recommended():
    result = _invoke(_criteria(2.2))

    assert result["verdict"] == "Not recommended"


def test_low_evidence_count_returns_insufficient_evidence_warning():
    result = _invoke(_criteria(4.5), evidence_count=0)

    assert result["verdict"] == "Insufficient evidence"
    assert any("Evidence count is 0" in warning for warning in result["warnings"])


def test_critical_risks_prevent_recommended_verdict():
    result = _invoke(_criteria(4.8), critical_risks=["license incompatibility"])

    assert result["verdict"] == "Recommended with constraints"

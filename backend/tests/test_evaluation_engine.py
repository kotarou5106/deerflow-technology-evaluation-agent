import pytest

from deerflow.evaluation.engine import (
    build_scorecard_result,
    calculate_weighted_score,
    classify_verdict,
    validate_criteria_weights,
)
from deerflow.evaluation.schemas import EvaluationCriterion


def _criterion(name: str, weight: float, score: float, evidence_ids: list[str] | None = None) -> EvaluationCriterion:
    return EvaluationCriterion(
        name=name,
        description=f"{name} assessment",
        weight=weight,
        score=score,
        rationale=f"{name} rationale",
        evidence_ids=evidence_ids if evidence_ids is not None else ["ev-1"],
    )


def test_calculate_weighted_score_with_valid_weights():
    criteria = [
        _criterion("fit", 0.5, 5),
        _criterion("maturity", 0.3, 4),
        _criterion("operability", 0.2, 3),
    ]

    validate_criteria_weights(criteria)

    assert calculate_weighted_score(criteria) == pytest.approx(4.3)


def test_invalid_weights_raise_clear_error():
    criteria = [
        _criterion("fit", 0.6, 5),
        _criterion("maturity", 0.6, 4),
    ]

    with pytest.raises(ValueError, match="sum to 1.0"):
        validate_criteria_weights(criteria)


def test_high_score_without_critical_risk_is_recommended():
    assert classify_verdict(4.2) == "Recommended"


def test_medium_score_is_recommended_with_constraints():
    assert classify_verdict(3.4) == "Recommended with constraints"


def test_low_score_is_not_recommended():
    assert classify_verdict(2.8) == "Not recommended"


def test_insufficient_evidence_verdict_when_criteria_lack_evidence():
    criteria = [
        _criterion("fit", 0.5, 5, evidence_ids=[]),
        _criterion("maturity", 0.5, 4, evidence_ids=["ev-2"]),
    ]

    result = build_scorecard_result(criteria)

    assert result.verdict == "Insufficient evidence"


def test_critical_risk_prevents_direct_recommended_verdict():
    assert classify_verdict(4.7, critical_risks=["license incompatibility"]) == "Recommended with constraints"

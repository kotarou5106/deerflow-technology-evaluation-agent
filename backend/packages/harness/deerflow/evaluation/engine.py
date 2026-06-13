"""Deterministic scoring helpers for technology evaluation.

This module intentionally contains no LLM calls, network access, filesystem IO,
or tool invocation. It turns structured evaluation criteria into a repeatable
scorecard that can be tested and audited.
"""

from __future__ import annotations

from collections.abc import Sequence

from deerflow.evaluation.schemas import EvaluationCriterion, ScorecardResult, Verdict

WEIGHT_SUM_TARGET = 1.0
WEIGHT_SUM_TOLERANCE = 0.01
RECOMMENDED_THRESHOLD = 4.0
CONSTRAINTS_THRESHOLD = 3.0
MIN_EVIDENCE_COVERAGE = 0.75
INSUFFICIENT_EVIDENCE_MARKERS = {"insufficient_evidence", "insufficient evidence", "missing_evidence", "missing evidence"}


def validate_criteria_weights(criteria: Sequence[EvaluationCriterion]) -> None:
    """Validate that criteria are present and weights sum close to 1.0."""
    if not criteria:
        raise ValueError("At least one evaluation criterion is required.")

    total_weight = sum(criterion.weight for criterion in criteria)
    if abs(total_weight - WEIGHT_SUM_TARGET) > WEIGHT_SUM_TOLERANCE:
        raise ValueError(f"Evaluation criteria weights must sum to 1.0 +/- {WEIGHT_SUM_TOLERANCE}; got {total_weight:.4f}.")


def calculate_weighted_score(criteria: Sequence[EvaluationCriterion]) -> float:
    """Calculate the weighted average score on a 1-5 scale."""
    validate_criteria_weights(criteria)
    return round(sum(criterion.weight * criterion.score for criterion in criteria), 2)


def _risk_texts(critical_risks: Sequence[str] | None) -> list[str]:
    return [str(risk).strip() for risk in (critical_risks or []) if str(risk).strip()]


def _has_insufficient_evidence_marker(critical_risks: Sequence[str] | None) -> bool:
    return any(risk.lower().replace("-", "_") in INSUFFICIENT_EVIDENCE_MARKERS for risk in _risk_texts(critical_risks))


def classify_verdict(final_score: float, critical_risks: Sequence[str] | None = None) -> Verdict:
    """Classify an adoption verdict from a score and blocking risk signals."""
    if final_score < 0 or final_score > 5:
        raise ValueError(f"final_score must be between 0 and 5; got {final_score}.")

    risks = _risk_texts(critical_risks)
    if _has_insufficient_evidence_marker(risks):
        return "Insufficient evidence"

    if final_score < CONSTRAINTS_THRESHOLD:
        return "Not recommended"

    if risks:
        return "Recommended with constraints"

    if final_score >= RECOMMENDED_THRESHOLD:
        return "Recommended"

    return "Recommended with constraints"


def _evidence_coverage(criteria: Sequence[EvaluationCriterion]) -> float:
    if not criteria:
        return 0.0
    supported = sum(1 for criterion in criteria if criterion.evidence_ids)
    return round(supported / len(criteria), 2)


def summarize_scorecard(criteria: Sequence[EvaluationCriterion]) -> str:
    """Produce a concise deterministic summary of criteria scores."""
    if not criteria:
        return "No evaluation criteria were provided."

    strongest = max(criteria, key=lambda criterion: criterion.score)
    weakest = min(criteria, key=lambda criterion: criterion.score)
    final_score = calculate_weighted_score(criteria)
    return (
        f"Weighted score {final_score:.2f}/5 across {len(criteria)} criteria. "
        f"Strongest criterion: {strongest.name} ({strongest.score:.1f}/5). "
        f"Weakest criterion: {weakest.name} ({weakest.score:.1f}/5)."
    )


def build_scorecard_result(criteria: Sequence[EvaluationCriterion], critical_risks: Sequence[str] | None = None) -> ScorecardResult:
    """Build a full deterministic scorecard result from weighted criteria."""
    final_score = calculate_weighted_score(criteria)
    coverage = _evidence_coverage(criteria)
    warnings: list[str] = []
    risks = _risk_texts(critical_risks)

    if coverage < MIN_EVIDENCE_COVERAGE:
        warnings.append(f"Evidence coverage is {coverage:.0%}; at least {MIN_EVIDENCE_COVERAGE:.0%} is required for a confident adoption verdict.")
        risks = [*risks, "insufficient_evidence"]

    if critical_risks:
        warnings.extend(f"Critical risk: {risk}" for risk in _risk_texts(critical_risks))

    verdict = classify_verdict(final_score, risks)
    return ScorecardResult(
        final_score=final_score,
        verdict=verdict,
        criteria_count=len(criteria),
        evidence_coverage=coverage,
        summary=summarize_scorecard(criteria),
        warnings=warnings,
    )

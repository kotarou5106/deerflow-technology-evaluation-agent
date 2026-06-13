"""Deterministic technology evaluation scorecard tool."""

from __future__ import annotations

import math
from typing import Any

from langchain.tools import tool

from deerflow.evaluation.engine import build_scorecard_result
from deerflow.evaluation.schemas import EvaluationCriterion


def _parse_criteria(criteria: list[dict[str, Any]]) -> list[EvaluationCriterion]:
    return [EvaluationCriterion.model_validate(item) for item in criteria]


def _evidence_count_warning(evidence_count: int | None, criteria_count: int) -> str | None:
    if evidence_count is None:
        return None

    minimum = max(1, math.ceil(criteria_count * 0.75))
    if evidence_count < minimum:
        return f"Evidence count is {evidence_count}; at least {minimum} evidence item(s) are recommended for {criteria_count} criteria."
    return None


@tool("evaluation_scorecard", parse_docstring=True)
def evaluation_scorecard_tool(
    target_technology: str,
    criteria: list[dict[str, Any]],
    evaluation_context: str | None = None,
    evidence_count: int | None = None,
    critical_risks: list[str] | None = None,
) -> dict[str, Any]:
    """Calculate a deterministic Technology Research & Evaluation scorecard and verdict.

    Use this tool for Technology Research & Evaluation Agent tasks before writing
    the Evaluation Scorecard / 评分卡 and Final Verdict / 最终结论. This is not a
    generic calculator: it converts evidence-backed evaluation criteria into a
    deterministic weighted final_score and adoption verdict. The LLM may collect
    evidence, organize rationale, and write the report narrative, but this tool
    should calculate the final score and verdict.

    This tool does not call an LLM, search the web, access the network, invoke
    external tools, or generate a long report.

    Args:
        target_technology: Technology, framework, platform, protocol, model, or tool being evaluated.
        criteria: Evaluation criteria with name, description, weight, score, rationale, and evidence_ids.
        evaluation_context: Optional adoption context for traceability.
        evidence_count: Optional count of evidence items gathered for the evaluation.
        critical_risks: Optional list of critical adoption risks. Any critical risk prevents a direct Recommended verdict.
    """
    parsed_criteria = _parse_criteria(criteria)
    risks = list(critical_risks or [])
    warnings: list[str] = []

    evidence_warning = _evidence_count_warning(evidence_count, len(parsed_criteria))
    if evidence_warning is not None:
        warnings.append(evidence_warning)
        risks.append("insufficient_evidence")

    scorecard = build_scorecard_result(parsed_criteria, critical_risks=risks)
    combined_warnings = [*warnings, *scorecard.warnings]

    return {
        "target_technology": target_technology,
        "evaluation_context": evaluation_context,
        "final_score": scorecard.final_score,
        "verdict": scorecard.verdict,
        "summary": scorecard.summary,
        "criteria": [criterion.model_dump() for criterion in parsed_criteria],
        "critical_risks": list(critical_risks or []),
        "evidence_count": evidence_count,
        "evidence_coverage": scorecard.evidence_coverage,
        "warnings": combined_warnings,
    }

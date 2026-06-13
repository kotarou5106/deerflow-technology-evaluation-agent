"""Preflight validation tool for structured technology evaluation reports."""

from __future__ import annotations

from typing import Any

from langchain.tools import tool
from pydantic import ValidationError

from deerflow.evaluation.consistency import ConsistencyIssue, check_evaluation_report_consistency
from deerflow.evaluation.schemas import EvaluationReport

_NEXT_ACTIONS_BY_CODE = {
    "schema_validation_error": "Fix the EvaluationReport payload so it matches the required schema.",
    "missing_evidence_id": "Fix evidence_ids so they point to existing evidence_items.",
    "evidence_ids_not_verifiable": "Add stable id values to evidence_items before relying on evidence_ids.",
    "high_score_low_evidence": "Add more evidence or lower the score/verdict.",
    "recommended_low_evidence": "Add more evidence or change the verdict to reflect uncertainty.",
    "missing_source_url": "Add source_url for the evidence item.",
    "missing_source_type": "Add source_type for the evidence item.",
    "missing_trust_level": "Add trust_level for the evidence item.",
    "invalid_trust_level": "Use one of high/medium/low for trust_level.",
    "invalid_support_status": "Use a recognized support_status such as supported, partially_supported, contradicted, unverified, outdated, or speculative.",
    "invalid_confidence": "Use a confidence value from 0.0 to 1.0, or one of high/medium/low.",
    "invalid_risk_severity": "Use one of critical/high/medium/low for risk severity.",
    "invalid_risk_likelihood": "Use one of high/medium/low for risk likelihood.",
    "missing_reference_url": "Add url for the reference item.",
    "duplicate_reference_url": "Remove duplicate references or merge them into one entry.",
}


def _issue_to_dict(issue: ConsistencyIssue) -> dict[str, Any]:
    return issue.model_dump(mode="json")


def _schema_validation_issue(exc: ValidationError) -> dict[str, Any]:
    locations = [str(error.get("loc", "")) for error in exc.errors()]
    paths = ", ".join(location for location in locations if location) or None
    return {
        "level": "error",
        "code": "schema_validation_error",
        "message": str(exc),
        "path": paths,
        "referenced_id": None,
    }


def _next_actions(errors: list[dict[str, Any]], warnings: list[dict[str, Any]]) -> list[str]:
    actions: list[str] = []
    for issue in [*errors, *warnings]:
        action = _NEXT_ACTIONS_BY_CODE.get(issue["code"], "Review and fix the reported validation issue.")
        if action not in actions:
            actions.append(action)
    return actions


def validate_evaluation_report_payload(report: dict[str, Any]) -> dict[str, Any]:
    """Validate an EvaluationReport payload and return deterministic preflight feedback."""
    try:
        parsed_report = EvaluationReport.model_validate(report)
    except ValidationError as exc:
        errors = [_schema_validation_issue(exc)]
        return {
            "passed": False,
            "error_count": len(errors),
            "warning_count": 0,
            "errors": errors,
            "warnings": [],
            "next_actions": _next_actions(errors, []),
        }

    consistency = check_evaluation_report_consistency(parsed_report)
    errors = [_issue_to_dict(issue) for issue in consistency.errors]
    warnings = [_issue_to_dict(issue) for issue in consistency.warnings]
    return {
        "passed": consistency.passed,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "next_actions": _next_actions(errors, warnings),
    }


@tool("evaluation_report_validate", parse_docstring=True)
def evaluation_report_validate_tool(report: dict[str, Any]) -> dict[str, Any]:
    """Preflight validate an EvaluationReport payload before report assembly.

    Use this tool for Technology Research & Evaluation Agent tasks before
    calling `evaluation_report_assembly`. It validates the EvaluationReport
    schema, checks evidence consistency, and returns blocking errors,
    non-blocking warnings, and next_actions. It does not write files, create
    artifacts, call an LLM, search the web, access the network, or modify the
    payload.

    Args:
        report: Complete or near-complete EvaluationReport payload to validate.
    """
    return validate_evaluation_report_payload(report)

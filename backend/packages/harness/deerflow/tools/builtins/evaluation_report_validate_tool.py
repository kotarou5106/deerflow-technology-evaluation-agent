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


def _format_schema_path(loc: tuple[Any, ...]) -> str:
    path = ""
    for part in loc:
        if isinstance(part, int):
            path += f"[{part}]"
        else:
            path += f".{part}" if path else str(part)
    return path or "<root>"


def _schema_fix_hint(path: str, error_type: str) -> str:
    if path == "title":
        return "Add title as a short string, for example '<Technology> Technology Evaluation'."
    if path.startswith("evidence_items["):
        if path.endswith(".evidence_summary"):
            return "Add evidence_summary as a concise string summarizing the source evidence."
        if path.endswith(".source_title"):
            return "Add source_title as a human-readable source title string."
        if path.endswith(".confidence"):
            return "Add confidence as a number from 0.0 to 1.0, or high/medium/low."
        if path.endswith(".relevance"):
            return "Use relevance as a JSON number from 0.0 to 1.0, not a string label."
        return "Each evidence_items entry must be an object with claim, evidence_summary, source_title, source_url, source_type, trust_level, support_status, confidence, and numeric relevance."
    if path.startswith("alternatives[") and path.endswith(".category"):
        return "Add category as a short string such as framework, library, platform, model, database, or tool."
    if path == "executive_summary" or path.startswith("executive_summary."):
        return "Use executive_summary as an object with one_sentence_verdict, key_reasons, major_risks, and best_fit."
    if path == "technology_overview" or path.startswith("technology_overview."):
        return "Use technology_overview as an object with description, problem_addressed, primary_use_cases, key_features, and target_users."
    if path.startswith("risk_register["):
        if path.endswith(".name"):
            return "Add risk_register[].name as a short risk title string."
        if path.endswith(".description"):
            return "Add risk_register[].description as a concrete risk description string."
        return "Each risk_register entry must be an object with name, description, severity, likelihood, mitigation, and evidence_ids."
    if path.startswith("open_questions"):
        return "Use open_questions as a list of objects, each with question, why_it_matters, and suggested_validation; do not use plain strings."
    if path == "adoption_plan.validation_plan" or path.startswith("adoption_plan.validation_plan"):
        return "Use adoption_plan.validation_plan as a list of validation step strings, not one combined string."
    if error_type == "missing":
        return "Add the required field using the EvaluationReport schema."
    if error_type.endswith("_type"):
        return "Change the value to the required JSON type for this EvaluationReport field."
    return "Fix this field so it matches the EvaluationReport schema."


def _schema_validation_issues(exc: ValidationError) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for error in exc.errors():
        loc = error.get("loc", ())
        loc_tuple = tuple(loc) if isinstance(loc, tuple | list) else (loc,)
        path = _format_schema_path(loc_tuple)
        error_type = str(error.get("type", ""))
        issues.append(
            {
                "level": "error",
                "code": "schema_validation_error",
                "message": str(error.get("msg", "Schema validation failed.")),
                "path": path,
                "referenced_id": None,
                "error_type": error_type,
                "fix_hint": _schema_fix_hint(path, error_type),
            }
        )
    return issues


def _next_actions(errors: list[dict[str, Any]], warnings: list[dict[str, Any]]) -> list[str]:
    actions: list[str] = []
    for issue in [*errors, *warnings]:
        action = _NEXT_ACTIONS_BY_CODE.get(issue["code"], "Review and fix the reported validation issue.")
        if action not in actions:
            actions.append(action)
        fix_hint = issue.get("fix_hint")
        if isinstance(fix_hint, str) and fix_hint and fix_hint not in actions:
            actions.append(fix_hint)
    return actions


def validate_evaluation_report_payload(report: dict[str, Any]) -> dict[str, Any]:
    """Validate an EvaluationReport payload and return deterministic preflight feedback."""
    try:
        parsed_report = EvaluationReport.model_validate(report)
    except ValidationError as exc:
        errors = _schema_validation_issues(exc)
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
    non-blocking warnings, and next_actions. Schema errors include field paths
    and fix_hint values so callers can repair loose payload shapes before
    validating again. It does not write files, create artifacts, call an LLM,
    search the web, access the network, or modify the payload.

    Args:
        report: Complete or near-complete EvaluationReport payload to validate.
    """
    return validate_evaluation_report_payload(report)

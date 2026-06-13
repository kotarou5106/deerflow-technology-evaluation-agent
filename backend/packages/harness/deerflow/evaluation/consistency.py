"""Evidence consistency checks for structured technology evaluation reports."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from deerflow.evaluation.schemas import EvaluationReport

IssueLevel = Literal["error", "warning"]

ALLOWED_SUPPORT_STATUSES = {
    "supports",
    "partially_supports",
    "contradicts",
    "unclear",
    "supported",
    "partially_supported",
    "contradicted",
    "unverified",
    "outdated",
    "speculative",
}
ALLOWED_CONFIDENCE_LABELS = {"high", "medium", "low"}
ALLOWED_TRUST_LEVELS = {"high", "medium", "low"}
ALLOWED_RISK_LEVELS = {"critical", "high", "medium", "low"}


class ConsistencyIssue(BaseModel):
    """A deterministic evidence consistency issue."""

    level: IssueLevel
    code: str
    message: str
    path: str | None = None
    referenced_id: str | None = None


class ConsistencyCheckResult(BaseModel):
    """Result of checking an EvaluationReport for evidence consistency."""

    passed: bool
    errors: list[ConsistencyIssue] = Field(default_factory=list)
    warnings: list[ConsistencyIssue] = Field(default_factory=list)


def _as_report(report: EvaluationReport | dict[str, Any]) -> EvaluationReport:
    if isinstance(report, EvaluationReport):
        return report
    return EvaluationReport.model_validate(report)


def _issue(
    level: IssueLevel,
    code: str,
    message: str,
    path: str | None = None,
    referenced_id: str | None = None,
) -> ConsistencyIssue:
    return ConsistencyIssue(
        level=level,
        code=code,
        message=message,
        path=path,
        referenced_id=referenced_id,
    )


def _is_blank(value: object) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _evidence_ids(report: EvaluationReport) -> tuple[set[str], bool]:
    explicit_ids = {evidence.id for evidence in report.evidence_items if evidence.id}
    fallback_ids = {f"evidence_{index}" for index, _ in enumerate(report.evidence_items, start=1)}
    return explicit_ids | fallback_ids, bool(explicit_ids)


def _check_evidence_references(
    report: EvaluationReport,
    valid_ids: set[str],
    has_explicit_ids: bool,
) -> tuple[list[ConsistencyIssue], list[ConsistencyIssue]]:
    errors: list[ConsistencyIssue] = []
    warnings: list[ConsistencyIssue] = []

    reference_groups = [
        ("criteria", report.criteria),
        ("core_capabilities", report.core_capabilities),
        ("risk_register", report.risk_register),
    ]
    for group_name, items in reference_groups:
        for index, item in enumerate(items):
            for evidence_id in getattr(item, "evidence_ids", []):
                path = f"{group_name}[{index}].evidence_ids"
                if evidence_id in valid_ids:
                    continue
                if has_explicit_ids:
                    errors.append(
                        _issue(
                            "error",
                            "missing_evidence_id",
                            f"{path} references unknown evidence id '{evidence_id}'.",
                            path=path,
                            referenced_id=evidence_id,
                        )
                    )
                else:
                    warnings.append(
                        _issue(
                            "warning",
                            "evidence_ids_not_verifiable",
                            f"{path} references '{evidence_id}', but evidence_items have no explicit ids.",
                            path=path,
                            referenced_id=evidence_id,
                        )
                    )
    return errors, warnings


def _check_evidence_quality(report: EvaluationReport) -> list[ConsistencyIssue]:
    warnings: list[ConsistencyIssue] = []
    for index, evidence in enumerate(report.evidence_items):
        base_path = f"evidence_items[{index}]"
        if _is_blank(evidence.id):
            warnings.append(
                _issue(
                    "warning",
                    "missing_evidence_id",
                    "Evidence item has no explicit id; fallback ids such as evidence_1 may be used only for positional references.",
                    path=f"{base_path}.id",
                )
            )
        if _is_blank(evidence.source_url):
            warnings.append(_issue("warning", "missing_source_url", "Evidence item is missing source_url.", path=f"{base_path}.source_url"))
        if _is_blank(evidence.source_type):
            warnings.append(_issue("warning", "missing_source_type", "Evidence item is missing source_type.", path=f"{base_path}.source_type"))
        if _is_blank(evidence.trust_level):
            warnings.append(_issue("warning", "missing_trust_level", "Evidence item is missing trust_level.", path=f"{base_path}.trust_level"))
        elif str(evidence.trust_level).strip().lower() not in ALLOWED_TRUST_LEVELS:
            warnings.append(_issue("warning", "invalid_trust_level", "Evidence item has an unrecognized trust_level.", path=f"{base_path}.trust_level"))

        support_status = str(evidence.support_status).strip().lower()
        if support_status not in ALLOWED_SUPPORT_STATUSES:
            warnings.append(_issue("warning", "invalid_support_status", "Evidence item has an unrecognized support_status.", path=f"{base_path}.support_status"))

        confidence = evidence.confidence
        if isinstance(confidence, str):
            if confidence.strip().lower() not in ALLOWED_CONFIDENCE_LABELS:
                warnings.append(_issue("warning", "invalid_confidence", "Evidence item has an unrecognized confidence label.", path=f"{base_path}.confidence"))
        elif not 0.0 <= confidence <= 1.0:
            warnings.append(_issue("warning", "invalid_confidence", "Evidence item confidence must be between 0.0 and 1.0.", path=f"{base_path}.confidence"))
    return warnings


def _check_evidence_sufficiency(report: EvaluationReport) -> list[ConsistencyIssue]:
    warnings: list[ConsistencyIssue] = []
    evidence_count = len(report.evidence_items)
    if report.final_score >= 4.0 and evidence_count < 3:
        warnings.append(
            _issue(
                "warning",
                "high_score_low_evidence",
                f"final_score is {report.final_score:.2f}, but only {evidence_count} evidence item(s) are present.",
                path="final_score",
            )
        )
    if report.verdict == "Recommended" and evidence_count < 3:
        warnings.append(
            _issue(
                "warning",
                "recommended_low_evidence",
                f"verdict is Recommended, but only {evidence_count} evidence item(s) are present.",
                path="verdict",
            )
        )
    return warnings


def _check_risks(report: EvaluationReport) -> list[ConsistencyIssue]:
    warnings: list[ConsistencyIssue] = []
    for index, risk in enumerate(report.risk_register):
        base_path = f"risk_register[{index}]"
        severity = risk.severity.strip().lower()
        likelihood = risk.likelihood.strip().lower()
        if not severity or severity not in ALLOWED_RISK_LEVELS:
            warnings.append(_issue("warning", "invalid_risk_severity", "Risk item has an unrecognized severity.", path=f"{base_path}.severity"))
        if not likelihood or likelihood not in ALLOWED_RISK_LEVELS:
            warnings.append(_issue("warning", "invalid_risk_likelihood", "Risk item has an unrecognized likelihood.", path=f"{base_path}.likelihood"))
    return warnings


def _check_references(report: EvaluationReport) -> list[ConsistencyIssue]:
    warnings: list[ConsistencyIssue] = []
    seen_urls: set[str] = set()
    for index, reference in enumerate(report.references):
        url = reference.url.strip()
        if not url:
            warnings.append(_issue("warning", "missing_reference_url", "Reference item is missing url.", path=f"references[{index}].url"))
            continue
        if url in seen_urls:
            warnings.append(
                _issue(
                    "warning",
                    "duplicate_reference_url",
                    f"Reference url '{url}' appears more than once.",
                    path=f"references[{index}].url",
                )
            )
        seen_urls.add(url)
    return warnings


def check_evaluation_report_consistency(report: EvaluationReport | dict[str, Any]) -> ConsistencyCheckResult:
    """Check evidence id references, source quality, risk metadata, and evidence sufficiency."""
    parsed = _as_report(report)
    errors: list[ConsistencyIssue] = []
    warnings: list[ConsistencyIssue] = []

    valid_ids, has_explicit_ids = _evidence_ids(parsed)
    reference_errors, reference_warnings = _check_evidence_references(parsed, valid_ids, has_explicit_ids)
    errors.extend(reference_errors)
    warnings.extend(reference_warnings)
    warnings.extend(_check_evidence_quality(parsed))
    warnings.extend(_check_evidence_sufficiency(parsed))
    warnings.extend(_check_risks(parsed))
    warnings.extend(_check_references(parsed))

    return ConsistencyCheckResult(
        passed=not errors,
        errors=errors,
        warnings=warnings,
    )

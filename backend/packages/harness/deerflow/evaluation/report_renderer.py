"""Deterministic Markdown renderer for technology evaluation reports."""

from __future__ import annotations

from typing import Any

from deerflow.evaluation.consistency import ConsistencyIssue
from deerflow.evaluation.schemas import EvaluationReport

NO_DATA = "No data provided"


def _as_report(report: EvaluationReport | dict[str, Any]) -> EvaluationReport:
    if isinstance(report, EvaluationReport):
        return report
    return EvaluationReport.model_validate(report)


def _line(value: str | None) -> str:
    if value is None or not value.strip():
        return NO_DATA
    return value.strip()


def _list(values: list[str]) -> str:
    if not values:
        return NO_DATA
    return "\n".join(f"- {_line(value)}" for value in values)


def _labeled_list(label: str, values: list[str]) -> str:
    return f"**{label}:**\n{_list(values)}"


def _table_cell(value: object) -> str:
    text = str(value) if value is not None else NO_DATA
    text = text.replace("\n", "<br>")
    return text.replace("|", "\\|")


def _format_confidence(value: float | str) -> str:
    if isinstance(value, str):
        return _line(value)
    return f"{value:.2f}"


def _table(headers: list[str], rows: list[list[object]]) -> str:
    if not rows:
        return NO_DATA

    header = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(_table_cell(cell) for cell in row) + " |" for row in rows]
    return "\n".join([header, separator, *body])


def _as_consistency_issue(issue: ConsistencyIssue | dict[str, Any]) -> ConsistencyIssue:
    if isinstance(issue, ConsistencyIssue):
        return issue
    return ConsistencyIssue.model_validate(issue)


def _render_consistency_notes(consistency_warnings: list[ConsistencyIssue | dict[str, Any]] | None) -> str | None:
    if not consistency_warnings:
        return None

    rows = [
        [
            warning.level,
            warning.code,
            warning.message,
            warning.path or "-",
            warning.referenced_id or "-",
        ]
        for warning in (_as_consistency_issue(issue) for issue in consistency_warnings)
    ]
    return _table(["Level", "Code", "Message", "Path", "Referenced ID"], rows)


def _render_executive_summary(parsed: EvaluationReport) -> str:
    if parsed.executive_summary is None:
        return "\n".join(
            [
                f"- Target technology: {_line(parsed.target_technology)}",
                f"- Evaluation context: {_line(parsed.evaluation_context)}",
                f"- Verdict: {parsed.verdict}",
                f"- Final score: {parsed.final_score:.2f}",
                f"- Recommendation: {_line(parsed.recommendation)}",
            ]
        )

    summary = parsed.executive_summary
    return "\n\n".join(
        [
            f"**One-sentence verdict:** {_line(summary.one_sentence_verdict)}",
            _labeled_list("Key reasons", summary.key_reasons),
            _labeled_list("Major risks", summary.major_risks),
            f"**Best fit:** {_line(summary.best_fit)}",
        ]
    )


def _render_technology_overview(parsed: EvaluationReport) -> str:
    if parsed.technology_overview is None:
        return f"**Target technology:** {_line(parsed.target_technology)}\n\n**Report title:** {_line(parsed.title)}"

    overview = parsed.technology_overview
    return "\n\n".join(
        [
            f"**Description:** {_line(overview.description)}",
            f"**Problem addressed:** {_line(overview.problem_addressed)}",
            _labeled_list("Primary use cases", overview.primary_use_cases),
            _labeled_list("Key features", overview.key_features),
            _labeled_list("Target users", overview.target_users),
        ]
    )


def _render_adoption_recommendation(parsed: EvaluationReport) -> str:
    if parsed.adoption_plan is None:
        return _line(parsed.recommendation)

    plan = parsed.adoption_plan
    return "\n\n".join(
        [
            f"**Recommendation:** {_line(plan.recommendation)}",
            _labeled_list("Suggested next steps", plan.suggested_next_steps),
            _labeled_list("Validation plan", plan.validation_plan),
            f"**Rollout strategy:** {_line(plan.rollout_strategy)}",
            f"**Decision deadline:** {_line(plan.decision_deadline)}",
        ]
    )


def render_evaluation_report_markdown(
    report: EvaluationReport | dict[str, Any],
    consistency_warnings: list[ConsistencyIssue | dict[str, Any]] | None = None,
) -> str:
    """Render an EvaluationReport into the fixed Technology Evaluation Report Markdown structure."""
    parsed = _as_report(report)
    consistency_notes = _render_consistency_notes(consistency_warnings)

    criteria_rows = [
        [
            criterion.name,
            criterion.description,
            f"{criterion.weight:.2f}",
            f"{criterion.score:.1f}",
            criterion.rationale,
            ", ".join(criterion.evidence_ids) if criterion.evidence_ids else NO_DATA,
        ]
        for criterion in parsed.criteria
    ]
    evidence_rows = [
        [
            evidence.id or NO_DATA,
            evidence.claim,
            evidence.evidence_summary,
            evidence.source_title,
            evidence.source_url,
            evidence.source_type,
            evidence.trust_level,
            evidence.support_status,
            _format_confidence(evidence.confidence),
            f"{evidence.relevance:.2f}",
            evidence.notes or NO_DATA,
        ]
        for evidence in parsed.evidence_items
    ]
    alternative_rows = [
        [
            option.name,
            option.description,
            option.category,
            "; ".join(option.strengths) if option.strengths else NO_DATA,
            "; ".join(option.weaknesses) if option.weaknesses else NO_DATA,
            "; ".join(option.best_fit_use_cases) if option.best_fit_use_cases else NO_DATA,
            "; ".join(option.risks) if option.risks else NO_DATA,
        ]
        for option in parsed.alternatives
    ]
    experiment_rows = [
        [
            experiment.name,
            experiment.description,
            experiment.command or NO_DATA,
            "Yes" if experiment.success else "No",
            experiment.logs_summary,
            f"{experiment.reproducibility_score:.2f}",
            experiment.notes or NO_DATA,
        ]
        for experiment in parsed.experiments
    ]
    capability_rows = [
        [
            capability.name,
            capability.description,
            ", ".join(capability.evidence_ids) if capability.evidence_ids else NO_DATA,
            capability.maturity_level or NO_DATA,
            "; ".join(capability.limitations) if capability.limitations else NO_DATA,
        ]
        for capability in parsed.core_capabilities
    ]
    risk_rows = [
        [
            risk.name,
            risk.description,
            risk.severity,
            risk.likelihood,
            risk.mitigation or NO_DATA,
            ", ".join(risk.evidence_ids) if risk.evidence_ids else NO_DATA,
        ]
        for risk in parsed.risk_register
    ]
    open_question_rows = [
        [
            question.question,
            question.why_it_matters,
            question.suggested_validation or NO_DATA,
        ]
        for question in parsed.open_questions
    ]
    reference_rows = (
        [
            [
                reference.title,
                reference.url,
                reference.source_type,
                reference.publisher or NO_DATA,
                reference.accessed_at or NO_DATA,
                reference.notes or NO_DATA,
            ]
            for reference in parsed.references
        ]
        if parsed.references
        else [
            [
                evidence.source_title,
                evidence.source_url,
                evidence.source_type,
                NO_DATA,
                NO_DATA,
                f"Derived from evidence item {evidence.id}" if evidence.id else "Derived from evidence item",
            ]
            for evidence in parsed.evidence_items
        ]
    )

    sections = [
        "# Technology Evaluation Report",
        "## 1. Executive Summary / 执行摘要",
        _render_executive_summary(parsed),
        "## 2. Final Verdict / 最终结论",
        f"**Verdict:** {parsed.verdict}\n\n**Final score:** {parsed.final_score:.2f}",
        "## 3. Evaluation Context / 评估背景",
        _line(parsed.evaluation_context),
        "## 4. Technology Overview / 技术概览",
        _render_technology_overview(parsed),
        "## 5. Core Capabilities / 核心能力",
        _table(
            ["Capability", "Description", "Evidence IDs", "Maturity Level", "Limitations"],
            capability_rows,
        ),
        "## 6. Evidence Matrix / 证据矩阵",
        _table(
            [
                "ID",
                "Claim",
                "Evidence",
                "Source Title",
                "Source URL",
                "Source Type",
                "Trust",
                "Support",
                "Confidence",
                "Relevance",
                "Notes",
            ],
            evidence_rows,
        ),
        "## 7. Evaluation Scorecard / 评分卡",
        _table(
            ["Criterion", "Description", "Weight", "Score", "Rationale", "Evidence IDs"],
            criteria_rows,
        ),
        "## 8. Alternative Comparison / 替代方案对比",
        _table(
            ["Name", "Description", "Category", "Strengths", "Weaknesses", "Best Fit Use Cases", "Risks"],
            alternative_rows,
        ),
        "## 9. Hands-on Validation / 实验验证",
        _table(
            ["Name", "Description", "Command", "Success", "Logs Summary", "Reproducibility", "Notes"],
            experiment_rows,
        ),
        "## 10. Risk Register / 风险清单",
        _table(
            ["Risk", "Description", "Severity", "Likelihood", "Mitigation", "Evidence IDs"],
            risk_rows,
        )
        if parsed.risk_register
        else _list(parsed.risks),
        "## 11. Adoption Recommendation / 采用建议",
        _render_adoption_recommendation(parsed),
        "## 12. Open Questions / 待确认问题",
        _table(["Question", "Why It Matters", "Suggested Validation"], open_question_rows),
        *(["### Consistency Notes / 一致性备注", consistency_notes] if consistency_notes is not None else []),
        "## 13. References / 参考资料",
        _table(["Title", "URL", "Source Type", "Publisher", "Accessed At", "Notes"], reference_rows),
    ]

    return "\n\n".join(sections) + "\n"

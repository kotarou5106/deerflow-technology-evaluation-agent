"""Technology evaluation domain models and deterministic scoring helpers."""

from deerflow.evaluation.consistency import (
    ConsistencyCheckResult,
    ConsistencyIssue,
    check_evaluation_report_consistency,
)
from deerflow.evaluation.engine import (
    build_scorecard_result,
    calculate_weighted_score,
    classify_verdict,
    summarize_scorecard,
    validate_criteria_weights,
)
from deerflow.evaluation.report_renderer import render_evaluation_report_markdown
from deerflow.evaluation.schemas import (
    AdoptionPlan,
    CoreCapability,
    EvaluationCriterion,
    EvaluationReport,
    EvidenceItem,
    ExecutiveSummary,
    ExperimentResult,
    OpenQuestion,
    ReferenceItem,
    RiskItem,
    ScorecardResult,
    TechnologyOption,
    TechnologyOverview,
)

__all__ = [
    "AdoptionPlan",
    "CoreCapability",
    "ConsistencyCheckResult",
    "ConsistencyIssue",
    "EvidenceItem",
    "EvaluationCriterion",
    "EvaluationReport",
    "ExecutiveSummary",
    "ExperimentResult",
    "OpenQuestion",
    "ReferenceItem",
    "RiskItem",
    "ScorecardResult",
    "TechnologyOption",
    "TechnologyOverview",
    "build_scorecard_result",
    "calculate_weighted_score",
    "check_evaluation_report_consistency",
    "classify_verdict",
    "render_evaluation_report_markdown",
    "summarize_scorecard",
    "validate_criteria_weights",
]

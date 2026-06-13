"""Structured data models for technology research and evaluation."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

TrustLevel = str
SupportStatus = str
Verdict = Literal["Recommended", "Recommended with constraints", "Not recommended", "Insufficient evidence"]


class EvidenceItem(BaseModel):
    """A sourced evidence record tied to a specific technical claim."""

    id: str | None = Field(default=None, description="Stable identifier used by criteria evidence_ids.")
    claim: str = Field(..., description="The technical claim being evaluated.")
    evidence_summary: str = Field(..., description="Concise summary of the source evidence.")
    source_title: str = Field(..., description="Human-readable source title.")
    source_url: str = Field(..., description="Canonical source URL.")
    source_type: str = Field(..., description="Official docs, GitHub, paper, benchmark, issue, blog, community, etc.")
    trust_level: TrustLevel = Field(..., description="Source trust tier.")
    support_status: SupportStatus = Field(..., description="How the evidence relates to the claim.")
    confidence: float | str = Field(..., description="Confidence in this evidence interpretation.")
    relevance: float = Field(..., ge=0.0, le=1.0, description="Relevance to the current adoption decision.")
    notes: str | None = Field(default=None, description="Caveats, contradictions, or context.")


class EvaluationCriterion(BaseModel):
    """One weighted scoring dimension in the technology evaluation rubric."""

    name: str
    description: str
    weight: float = Field(..., ge=0.0, le=1.0)
    score: float = Field(..., ge=1.0, le=5.0)
    rationale: str
    evidence_ids: list[str] = Field(default_factory=list)


class TechnologyOption(BaseModel):
    """A target or alternative technology option."""

    name: str
    description: str
    category: str
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    best_fit_use_cases: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)


class ExperimentResult(BaseModel):
    """A reproducible hands-on validation result."""

    name: str
    description: str
    command: str | None = None
    success: bool
    logs_summary: str
    reproducibility_score: float = Field(..., ge=0.0, le=1.0)
    notes: str | None = None


class CoreCapability(BaseModel):
    """A structured capability claim backed by evidence."""

    name: str
    description: str
    evidence_ids: list[str] = Field(default_factory=list)
    maturity_level: str | None = None
    limitations: list[str] = Field(default_factory=list)


class RiskItem(BaseModel):
    """A structured adoption risk with mitigation and evidence links."""

    name: str
    description: str
    severity: str
    likelihood: str
    mitigation: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)


class OpenQuestion(BaseModel):
    """A decision-relevant unknown that should not be guessed."""

    question: str
    why_it_matters: str
    suggested_validation: str | None = None


class ReferenceItem(BaseModel):
    """A source reference used by the technology evaluation."""

    title: str
    url: str
    source_type: str
    publisher: str | None = None
    accessed_at: str | None = None
    notes: str | None = None


class TechnologyOverview(BaseModel):
    """Structured overview of the evaluated technology."""

    description: str
    problem_addressed: str | None = None
    primary_use_cases: list[str] = Field(default_factory=list)
    key_features: list[str] = Field(default_factory=list)
    target_users: list[str] = Field(default_factory=list)


class ExecutiveSummary(BaseModel):
    """Structured executive summary for the adoption decision."""

    one_sentence_verdict: str
    key_reasons: list[str] = Field(default_factory=list)
    major_risks: list[str] = Field(default_factory=list)
    best_fit: str | None = None


class AdoptionPlan(BaseModel):
    """Structured recommendation and adoption plan."""

    recommendation: str
    suggested_next_steps: list[str] = Field(default_factory=list)
    validation_plan: list[str] = Field(default_factory=list)
    rollout_strategy: str | None = None
    decision_deadline: str | None = None


class EvaluationReport(BaseModel):
    """Structured report payload for a technology adoption decision."""

    title: str
    target_technology: str
    evaluation_context: str
    verdict: Verdict
    final_score: float = Field(..., ge=0.0, le=5.0)
    criteria: list[EvaluationCriterion] = Field(default_factory=list)
    evidence_items: list[EvidenceItem] = Field(default_factory=list)
    alternatives: list[TechnologyOption] = Field(default_factory=list)
    experiments: list[ExperimentResult] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    recommendation: str
    executive_summary: ExecutiveSummary | None = None
    technology_overview: TechnologyOverview | None = None
    core_capabilities: list[CoreCapability] = Field(default_factory=list)
    risk_register: list[RiskItem] = Field(default_factory=list)
    open_questions: list[OpenQuestion] = Field(default_factory=list)
    references: list[ReferenceItem] = Field(default_factory=list)
    adoption_plan: AdoptionPlan | None = None


class ScorecardResult(BaseModel):
    """Deterministic scoring output derived from weighted criteria."""

    final_score: float = Field(..., ge=0.0, le=5.0)
    verdict: Verdict
    criteria_count: int
    evidence_coverage: float = Field(..., ge=0.0, le=1.0)
    summary: str
    warnings: list[str] = Field(default_factory=list)

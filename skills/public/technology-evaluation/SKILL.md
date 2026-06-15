---
name: technology-evaluation
description: Use this skill when deciding whether a technology, framework, library, platform, model, protocol, database, tool, or architecture should be adopted. Produces evidence-backed technology evaluation reports with explicit claims, evidence, scoring, alternatives, risks, experiments, and adoption recommendations.
---

# Technology Evaluation Skill

This skill turns technology research into an adoption decision. It is not ordinary deep research. The central question is always:

**Is this technology worth adopting for the stated context, and under what constraints?**

Every important judgment must be backed by evidence. Separate **Claim**, **Evidence**, and **Conclusion** throughout the work.

## When To Use

Use this skill for:

- Evaluating a new framework, library, platform, API, model, database, protocol, cloud service, infrastructure tool, or architecture pattern.
- Comparing alternatives before adoption.
- Auditing whether an existing technology choice should continue.
- Assessing maturity, maintainability, ecosystem health, performance, security, cost, licensing, migration effort, or operational risk.

Do not use this skill for broad educational summaries unless the user asks for an adoption decision.

## Required Workflow

### 1. Technology Boundary / 技术边界确认

Before researching, define the evaluation boundary:

- Target technology and exact scope: product, repo, package, version, managed service, protocol, or architectural pattern.
- Adoption context: team size, workload, scale, environment, language/runtime, compliance needs, budget, migration constraints.
- Decision horizon: immediate trial, production adoption, migration, replacement, or long-term strategic bet.
- Out-of-scope areas: explicitly state what will not be evaluated.

If the boundary is unclear and affects the decision, ask a clarification question before proceeding.

### 2. Research Questions / 研究问题拆解

Break the adoption decision into concrete research questions. At minimum cover:

- What problem does this technology solve better than current options?
- What are its core capabilities and limits?
- How mature and actively maintained is it?
- How strong is the ecosystem and documentation?
- What are the operational, security, licensing, and cost risks?
- What alternatives should be compared?
- What must be validated hands-on before adoption?

### 3. Source Strategy / 来源策略

Prefer high-trust sources in this order:

1. Official documentation, specs, API references, migration guides.
2. Official GitHub repositories, changelogs, release notes, issue trackers, discussions, security advisories.
3. Peer-reviewed papers, preprints with clear methodology, reproducible benchmarks, technical standards.
4. Engineering blogs from teams using the technology in production, with concrete architecture and operational details.
5. Independent benchmarks and postmortems with reproducible methodology.
6. Community discussions only as weak signals, especially for developer experience and common failure modes.
7. Marketing pages, vendor claims, unsourced social posts, and SEO articles are low-weight unless corroborated by stronger evidence.

Use `web_fetch` for important sources; do not rely only on snippets.

### 4. Evidence Standard / 证据标准

Record evidence as structured items:

- Claim: the precise technical or adoption claim.
- Evidence: source-backed summary, with URL and source type.
- Support status: supports, partially supports, contradicts, or unclear.
- Trust level: high, medium, or low.
- Confidence and relevance: explain why the evidence matters for the adoption decision.

Important judgments require at least one high-trust source or multiple medium-trust sources. If evidence is missing, mark the judgment as insufficient evidence instead of guessing.

### 5. Claim Verification / 主张验证

For every major claim:

- Check whether the claim comes from official sources, independent validation, or marketing language.
- Look for contradictions in issues, release notes, benchmark methodology, and migration reports.
- Distinguish proven capabilities from roadmap promises.
- Distinguish general capability from fit for the user's context.
- Avoid converting popularity into suitability without supporting evidence.

Use this structure in notes and reports:

```markdown
Claim: ...
Evidence: ...
Conclusion: ...
```

### 6. Evaluation Rubric / 评估量表

Use a 1-5 score for each criterion:

- 5: Strong evidence of excellent fit; low unresolved risk.
- 4: Good fit; manageable constraints.
- 3: Plausible fit; meaningful unknowns or operational caveats.
- 2: Weak fit; important gaps or high adoption cost.
- 1: Poor fit; major blockers or unacceptable risk.

Weights must sum to approximately 1.0. Recommended default criteria:

| Criterion | Default Weight | What To Assess |
|---|---:|---|
| Problem Fit | 0.20 | Does it solve the target problem better than current options? |
| Technical Capability | 0.20 | Feature completeness, architecture, performance envelope, integration points. |
| Maturity & Maintenance | 0.15 | Release cadence, issue health, backwards compatibility, stability. |
| Ecosystem & Documentation | 0.10 | Docs quality, examples, integrations, community and vendor support. |
| Operational Complexity | 0.15 | Deployment, observability, debugging, scaling, SRE burden. |
| Security, Compliance & License | 0.10 | Security posture, dependency risk, license compatibility, compliance fit. |
| Cost & Migration Effort | 0.10 | Runtime cost, switching cost, training, migration risk. |

Customize criteria and weights when the user's context requires it.

### 6.1 Deterministic Scorecard Tool / 确定性评分工具

Before generating the **Evaluation Scorecard** or **Final Verdict**, if the `evaluation_scorecard` tool is available, call it to calculate `final_score` and `verdict`.

Responsibilities:

- Evidence / 证据: collected first by the lead agent and, when useful, researcher subagents.
- Criteria / 评分维度: organized by the lead agent from the rubric and user context.
- Score / 分项分数: assigned by the lead agent from evidence-backed rationale on a 1-5 scale.
- Weighted final_score / 加权总分: calculated by `evaluation_scorecard`.
- Verdict / 结论分类: classified by `evaluation_scorecard`.

Do not invent or freely write the final weighted score when the tool is available. Use the tool result in the report, and explain any warnings such as insufficient evidence or critical risks.

### 7. Alternative Comparison / 替代方案对比

Always identify realistic alternatives, including:

- Current incumbent or "do nothing".
- Direct competitors.
- Adjacent approaches or simpler substitutes.
- Managed vs self-hosted options when applicable.

Compare alternatives on fit, maturity, operational burden, ecosystem, risk, and switching cost. Do not recommend a target technology without explaining why alternatives are weaker or better for the specific context.

### 8. Experiment Notes / 实验验证记录

When the user asks for validation, or when claims are too important to trust from docs alone, propose or run small experiments:

- Installation or quickstart reproducibility.
- Minimal integration path.
- Performance sanity check.
- API ergonomics check.
- Migration spike.
- Failure mode or rollback test.

Record command, environment assumptions, success/failure, logs summary, reproducibility score, and notes. If experiments are not run, list the recommended experiments and mark the evidence gap.

### 9. Risk Assessment / 风险评估

Maintain a risk register:

- Risk description.
- Severity and likelihood.
- Evidence behind the risk.
- Mitigation.
- Adoption impact.

Critical risks include licensing incompatibility, unmaintained project, unresolved security issues, missing production requirement, unacceptable operational burden, or evidence gaps in a decision-critical area. Critical risk prevents a simple "Recommended" verdict even if the score is high.

### 10. Final Recommendation / 最终建议

Final verdict must be one of:

- Recommended
- Recommended with constraints
- Not recommended
- Insufficient evidence

State the recommendation plainly, then list conditions:

- Adopt now.
- Pilot first.
- Adopt only for specific use cases.
- Defer until risks are resolved.
- Reject for this context.

### 11. Dual Report Artifacts / 双产物报告

When producing the final Technology Evaluation Report, create two artifacts when the file/artifact tools are available:

1. Markdown report: for human reading, using the fixed report structure below.
2. EvaluationReport JSON artifact: for system reuse and future frontend rendering.

The JSON artifact must conform to the `EvaluationReport` schema and include target_technology, evaluation_context, verdict, final_score, criteria, evidence_items, alternatives, experiments, risks, and recommendation.

Consistency rules:

- Markdown `final_score` and `verdict` must match the `evaluation_scorecard` tool result.
- EvaluationReport JSON `final_score` and `verdict` must match the same `evaluation_scorecard` tool result.
- JSON `criteria`, `evidence_items`, `alternatives`, `experiments`, and `risks` must reflect the report content.
- Do not allow the Markdown report and JSON artifact to give conflicting conclusions.
- Use the `evaluation_report_artifact` tool when available to validate and write the structured JSON artifact.

### 12. Report Assembly / 报告组装流程

At the final report stage, prefer the report assembly workflow when the `evaluation_report_assembly` tool is available:

1. Form a complete `EvaluationReport` payload from the collected evidence, criteria, alternatives, experiments, risks, and recommendation.
2. Use `evaluation_scorecard` to calculate `final_score` and `verdict`, then put those exact values into the `EvaluationReport` payload.
3. Use `evaluation_report_assembly` to generate both the EvaluationReport JSON artifact and the Technology Evaluation Report Markdown from the same payload.
4. Treat the EvaluationReport payload as the single source of truth.
5. Do not freely write separate Markdown and JSON artifacts that may diverge.

The Markdown renderer should be deterministic: it should render verdict, final_score, criteria, evidence, alternatives, experiments, risks, and recommendation from the `EvaluationReport` payload instead of inventing or reinterpreting them.

When constructing the `EvaluationReport` payload, fill the structured fields whenever evidence supports them:

- `executive_summary`: one-sentence verdict, key reasons, major risks, and best-fit context.
- `technology_overview`: description, problem addressed, primary use cases, key features, and target users.
- `core_capabilities`: capability records linked to `evidence_ids`; include limitations and maturity level when known.
- `risk_register`: structured risk analysis with severity, likelihood, mitigation, and `evidence_ids`.
- `open_questions`: uncertain decision-critical items and suggested validation; put unknowns here instead of guessing.
- `references`: final source list with title, URL, source type, publisher/access date when known, and notes.
- `adoption_plan`: recommendation, next steps, validation plan, rollout strategy, and decision deadline when applicable.

Keep the legacy `risks` field as a short risk summary when useful. Use `risk_register` for detailed risk analysis. Keep the legacy `recommendation` field for compatibility, and use `adoption_plan` for structured adoption guidance.

Use this compact canonical `EvaluationReport` skeleton when constructing the payload. Preserve the object/list shapes exactly; replace placeholder strings with evidence-backed content:

```json
{
  "title": "LangGraph Technology Evaluation",
  "target_technology": "LangGraph",
  "evaluation_context": "Evaluate LangGraph for long-running AI agent workflows.",
  "verdict": "Recommended with constraints",
  "final_score": 3.85,
  "criteria": [
    {
      "name": "Problem Fit",
      "description": "Fit for the stated adoption context.",
      "weight": 0.25,
      "score": 4.0,
      "rationale": "Evidence-backed scoring rationale.",
      "evidence_ids": ["ev-1"]
    }
  ],
  "evidence_items": [
    {
      "id": "ev-1",
      "claim": "Specific claim being evaluated.",
      "evidence_summary": "Concise summary of the source evidence.",
      "source_title": "Human-readable source title",
      "source_url": "https://example.com/source",
      "source_type": "official_docs",
      "trust_level": "high",
      "support_status": "supports",
      "confidence": 0.9,
      "relevance": 0.95,
      "notes": "Caveats or context."
    }
  ],
  "alternatives": [
    {
      "name": "Alternative name",
      "description": "What the alternative is.",
      "category": "framework",
      "strengths": ["Where it is strong."],
      "weaknesses": ["Where it is weak."],
      "best_fit_use_cases": ["Best-fit use case."],
      "risks": ["Alternative-specific risk."]
    }
  ],
  "experiments": [
    {
      "name": "Validation experiment",
      "description": "What was or should be validated.",
      "command": null,
      "success": false,
      "logs_summary": "Not run; recommended validation.",
      "reproducibility_score": 0.0,
      "notes": "Experiment caveats."
    }
  ],
  "risks": ["Short risk summary."],
  "recommendation": "Compatibility recommendation string.",
  "executive_summary": {
    "one_sentence_verdict": "One-sentence adoption verdict.",
    "key_reasons": ["Evidence-backed reason."],
    "major_risks": ["Major risk."],
    "best_fit": "Best-fit adoption context."
  },
  "technology_overview": {
    "description": "Technology description.",
    "problem_addressed": "Problem addressed.",
    "primary_use_cases": ["Use case."],
    "key_features": ["Feature."],
    "target_users": ["Target user."]
  },
  "core_capabilities": [
    {
      "name": "Capability name",
      "description": "Capability description.",
      "evidence_ids": ["ev-1"],
      "maturity_level": "maturity label",
      "limitations": ["Known limitation."]
    }
  ],
  "risk_register": [
    {
      "name": "Risk name",
      "description": "Risk description.",
      "severity": "medium",
      "likelihood": "medium",
      "mitigation": "Mitigation plan.",
      "evidence_ids": ["ev-1"]
    }
  ],
  "open_questions": [
    {
      "question": "Decision-relevant unknown?",
      "why_it_matters": "Why this affects adoption.",
      "suggested_validation": "How to validate it."
    }
  ],
  "references": [
    {
      "title": "Source title",
      "url": "https://example.com/source",
      "source_type": "official_docs",
      "publisher": "Publisher",
      "accessed_at": null,
      "notes": "Reference notes."
    }
  ],
  "adoption_plan": {
    "recommendation": "Structured adoption recommendation.",
    "suggested_next_steps": ["Next step."],
    "validation_plan": ["Validation step."],
    "rollout_strategy": "Rollout strategy.",
    "decision_deadline": "Decision timing."
  }
}
```

Avoid these invalid loose shapes:

- Do not set `executive_summary` or `technology_overview` to a string; use the object shapes above.
- Do not use string arrays for `open_questions`; each entry must be an object.
- Do not use strings such as `"high"` for `evidence_items.relevance`; use a number from 0.0 to 1.0.
- Do not omit `title`, `evidence_summary`, `source_title`, `confidence`, `alternatives.category`, or `risk_register.name` / `risk_register.description`.
- Do not set `adoption_plan.validation_plan` to one string; use a list of strings.

Before calling `evaluation_report_assembly`, check evidence consistency:

- Every `criteria.evidence_ids` value should match an existing `evidence_items.id`.
- Every `core_capabilities.evidence_ids` value should match an existing `evidence_items.id`.
- Every `risk_register.evidence_ids` value should match an existing `evidence_items.id`.
- Every important conclusion should be traceable to evidence; if support is weak, use `Insufficient evidence` or add the uncertainty to `open_questions`.
- Do not write unsupported opinions as strong conclusions.
- Keep `references` aligned with evidence sources. If references are not provided, evidence source fields must be strong enough for fallback references.

When the `evaluation_report_validate` tool is available, use it as a preflight step before final assembly:

1. Construct the `EvaluationReport` payload.
2. Call `evaluation_report_validate`.
3. If validation returns errors, fix the payload and validate again.
4. If validation returns only warnings, you may continue to assembly, but preserve the audit signal in Consistency Notes.
5. Call `evaluation_report_assembly` to generate the EvaluationReport JSON artifact and Markdown report.

## Fixed Report Structure

When producing a report, use the template at:

`assets/report_template.md`

The report must include:

- Executive summary.
- Final verdict.
- Evaluation context.
- Technology overview.
- Core capabilities.
- Evidence matrix.
- Evaluation scorecard.
- Alternative comparison.
- Hands-on validation.
- Risk register.
- Adoption recommendation.
- Open questions.
- References.

## Output Rules

- Use the user's language.
- Keep Claim / Evidence / Conclusion separated for important judgments.
- Include inline citations with URLs for source-backed claims.
- Put all sources in the References section.
- If evidence is weak, say so explicitly.
- Never present marketing claims as verified facts unless corroborated.
- Do not hide contradictions; explain how they affect the recommendation.

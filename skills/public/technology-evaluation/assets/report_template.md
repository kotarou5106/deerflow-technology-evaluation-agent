# Technology Evaluation Report

## 1. Executive Summary / 执行摘要

Summarize the adoption decision in 3-5 sentences. Include the target technology, evaluation context, final verdict, final score, strongest reasons, and most important constraints or blockers.

## 2. Final Verdict / 最终结论

Use exactly one verdict:

- Recommended
- Recommended with constraints
- Not recommended
- Insufficient evidence

Explain the decision in terms of adoption readiness. State whether the technology should be adopted now, piloted first, limited to specific use cases, deferred, or rejected for the stated context.

## 3. Evaluation Context / 评估背景

Describe:

- Target technology and evaluated version/scope.
- User or organization context.
- Workloads and use cases under consideration.
- Constraints: scale, runtime, team skill, budget, compliance, timeline, migration limits.
- Explicit out-of-scope areas.

## 4. Technology Overview / 技术概览

Explain what the technology is, what problem it is designed to solve, its architecture or operating model, and its current maturity. Separate official claims from independently verified facts.

Use:

```markdown
Claim: ...
Evidence: ...
Conclusion: ...
```

for major statements.

## 5. Core Capabilities / 核心能力

List the capabilities most relevant to adoption. For each capability include:

- What it does.
- Why it matters for the evaluation context.
- Evidence source.
- Known limits or caveats.

## 6. Evidence Matrix / 证据矩阵

Provide a table of evidence-backed claims.

| ID | Claim | Evidence Summary | Source | Source Type | Trust Level | Support Status | Confidence | Relevance | Notes |
|---|---|---|---|---|---|---|---:|---:|---|
| E1 |  |  |  |  |  | supports / partially_supports / contradicts / unclear |  |  |  |

Important judgments must map to evidence IDs used later in the scorecard.

## 7. Evaluation Scorecard / 评分卡

Use a 1-5 score per criterion. Weights should sum to approximately 1.0.

| Criterion | Weight | Score (1-5) | Rationale | Evidence IDs |
|---|---:|---:|---|---|
| Problem Fit |  |  |  |  |
| Technical Capability |  |  |  |  |
| Maturity & Maintenance |  |  |  |  |
| Ecosystem & Documentation |  |  |  |  |
| Operational Complexity |  |  |  |  |
| Security, Compliance & License |  |  |  |  |
| Cost & Migration Effort |  |  |  |  |

Include the weighted final score and explain why high scores do not override critical risks or insufficient evidence.

## 8. Alternative Comparison / 替代方案对比

Compare the target technology against realistic alternatives, including the current incumbent or "do nothing" option.

| Option | Category | Strengths | Weaknesses | Best Fit Use Cases | Key Risks | Assessment |
|---|---|---|---|---|---|---|
| Target Technology |  |  |  |  |  |  |
| Alternative 1 |  |  |  |  |  |  |
| Alternative 2 |  |  |  |  |  |  |

Conclude why the target is or is not preferable for the stated context.

## 9. Hands-on Validation / 实验验证

Record experiments that were run or should be run before adoption.

| Experiment | Purpose | Command / Method | Success | Logs Summary | Reproducibility Score | Notes |
|---|---|---|---|---|---:|---|
|  |  |  |  |  |  |  |

If no experiments were run, state that clearly and list recommended validation steps.

## 10. Risk Register / 风险清单

List material adoption risks.

| Risk | Severity | Likelihood | Evidence IDs | Impact | Mitigation | Adoption Implication |
|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |

Call out critical risks explicitly. Critical risks prevent a simple "Recommended" verdict.

## 11. Adoption Recommendation / 采用建议

Provide concrete next steps:

- Adoption path: adopt, pilot, constrained adoption, defer, or reject.
- Required conditions before production use.
- Suggested rollout plan.
- Migration considerations.
- Ownership and operational readiness requirements.
- Review checkpoint or reevaluation trigger.

## 12. Open Questions / 待确认问题

List unresolved questions and evidence gaps. For each item explain what decision it affects and how to resolve it.

| Question | Why It Matters | Needed Evidence | Owner / Next Step |
|---|---|---|---|
|  |  |  |  |

## 13. References / 参考资料

List all sources used. Prefer official documentation, official GitHub, release notes, issues, papers, benchmarks, and engineering blogs.

Use standard Markdown links:

- [Source Title](https://example.com) - Source type and why it was used.

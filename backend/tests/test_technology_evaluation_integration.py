from pathlib import Path

from deerflow.agents.lead_agent import prompt as prompt_module
from deerflow.skills.storage.local_skill_storage import LocalSkillStorage
from deerflow.subagents.registry import get_subagent_config

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = REPO_ROOT / "skills"
TECH_EVAL_SKILL = SKILLS_ROOT / "public" / "technology-evaluation" / "SKILL.md"
TECH_EVAL_TEMPLATE = SKILLS_ROOT / "public" / "technology-evaluation" / "assets" / "report_template.md"


def test_technology_evaluation_skill_file_exists_at_public_path():
    assert TECH_EVAL_SKILL.is_file()


def test_technology_evaluation_report_template_has_fixed_sections():
    content = TECH_EVAL_TEMPLATE.read_text(encoding="utf-8")
    expected_sections = [
        "# Technology Evaluation Report",
        "## 1. Executive Summary / 执行摘要",
        "## 2. Final Verdict / 最终结论",
        "## 3. Evaluation Context / 评估背景",
        "## 4. Technology Overview / 技术概览",
        "## 5. Core Capabilities / 核心能力",
        "## 6. Evidence Matrix / 证据矩阵",
        "## 7. Evaluation Scorecard / 评分卡",
        "## 8. Alternative Comparison / 替代方案对比",
        "## 9. Hands-on Validation / 实验验证",
        "## 10. Risk Register / 风险清单",
        "## 11. Adoption Recommendation / 采用建议",
        "## 12. Open Questions / 待确认问题",
        "## 13. References / 参考资料",
    ]

    for section in expected_sections:
        assert section in content


def test_technology_evaluation_skill_is_discovered_by_local_storage():
    storage = LocalSkillStorage(host_path=str(SKILLS_ROOT))

    skills = storage.load_skills(enabled_only=True)

    skill = next(skill for skill in skills if skill.name == "technology-evaluation")
    assert skill.category == "public"
    assert skill.skill_file == TECH_EVAL_SKILL
    assert skill.get_container_file_path() == "/mnt/skills/public/technology-evaluation/SKILL.md"


def test_prompt_contains_technology_evaluation_routing_guidance():
    template = prompt_module.SYSTEM_PROMPT_TEMPLATE

    assert "<technology_evaluation_routing>" in template
    assert "prioritize" in template
    assert "`technology-evaluation` skill" in template
    assert "call `evaluation_scorecard`" in template
    assert "EvaluationReport payload" in template
    assert "`evaluation_report_assembly`" in template
    assert "core_capabilities" in template
    assert "risk_register" in template
    assert "references" in template
    assert "adoption_plan" in template
    assert "evidence_ids traceable" in template
    assert "existing evidence_items ids" in template
    assert "`evaluation_report_validate`" in template
    assert "fix blocking errors" in template
    assert "same verdict and final_score" in template
    assert "fixed Technology Evaluation Report structure" in template


def test_technology_evaluation_skill_mentions_scorecard_tool():
    content = TECH_EVAL_SKILL.read_text(encoding="utf-8")

    assert "evaluation_scorecard" in content
    assert "Weighted final_score / 加权总分" in content
    assert "Verdict / 结论分类" in content


def test_technology_evaluation_skill_mentions_markdown_and_json_artifacts():
    content = TECH_EVAL_SKILL.read_text(encoding="utf-8")

    assert "Markdown report" in content
    assert "EvaluationReport JSON artifact" in content
    assert "evaluation_report_artifact" in content
    assert "conflicting conclusions" in content


def test_technology_evaluation_skill_mentions_report_assembly():
    content = TECH_EVAL_SKILL.read_text(encoding="utf-8")

    assert "Report Assembly / 报告组装流程" in content
    assert "evaluation_report_assembly" in content
    assert "single source of truth" in content
    assert "Do not freely write separate Markdown and JSON artifacts" in content


def test_technology_evaluation_skill_mentions_structured_report_fields():
    content = TECH_EVAL_SKILL.read_text(encoding="utf-8")

    for field in [
        "executive_summary",
        "technology_overview",
        "core_capabilities",
        "risk_register",
        "open_questions",
        "references",
        "adoption_plan",
    ]:
        assert field in content


def test_technology_evaluation_skill_mentions_evidence_consistency():
    content = TECH_EVAL_SKILL.read_text(encoding="utf-8")

    assert "Before calling `evaluation_report_assembly`, check evidence consistency" in content
    assert "criteria.evidence_ids" in content
    assert "core_capabilities.evidence_ids" in content
    assert "risk_register.evidence_ids" in content
    assert "existing `evidence_items.id`" in content


def test_technology_evaluation_skill_mentions_validate_before_assembly():
    content = TECH_EVAL_SKILL.read_text(encoding="utf-8")

    assert "evaluation_report_validate" in content
    assert "preflight step before final assembly" in content
    assert "fix the payload and validate again" in content
    assert "evaluation_report_assembly" in content


def test_technology_evaluation_subagents_are_registered():
    evidence = get_subagent_config("evidence-researcher")
    alternative = get_subagent_config("alternative-analyst")
    experiment = get_subagent_config("experiment-runner")

    assert evidence is not None
    assert evidence.skills == ["technology-evaluation", "deep-research", "github-deep-research"]
    assert "Claim" in (evidence.system_prompt or "")

    assert alternative is not None
    assert alternative.skills == ["technology-evaluation", "deep-research", "github-deep-research"]
    assert "Best-fit use cases" in (alternative.system_prompt or "")

    assert experiment is not None
    assert experiment.skills == ["technology-evaluation"]
    assert "ExperimentResult" in (experiment.system_prompt or "")


def test_config_example_documents_technology_evaluation_subagent_overrides():
    content = (REPO_ROOT / "config.example.yaml").read_text(encoding="utf-8")

    assert "evidence-researcher:" in content
    assert "alternative-analyst:" in content
    assert "experiment-runner:" in content
    assert "- technology-evaluation" in content

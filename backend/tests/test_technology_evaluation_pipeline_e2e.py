import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from deerflow.agents.lead_agent import prompt as prompt_module
from deerflow.evaluation.schemas import EvaluationReport
from deerflow.skills.storage.local_skill_storage import LocalSkillStorage
from deerflow.subagents.registry import get_subagent_config
from deerflow.tools.builtins import evaluation_report_validate_tool, evaluation_scorecard_tool
from deerflow.tools.builtins.evaluation_report_assembly_tool import write_assembled_evaluation_report
from deerflow.tools.tools import get_available_tools

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = REPO_ROOT / "skills"
LANGGRAPH_EXAMPLE_DIR = REPO_ROOT / "examples" / "technology-evaluation" / "langgraph"

FIXED_SECTIONS = [
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


def _make_minimal_config():
    config = MagicMock()
    config.tools = []
    config.models = []
    config.tool_search.enabled = False
    config.skill_evolution.enabled = False
    config.sandbox = MagicMock()
    config.acp_agents = {}
    return config


def _criteria() -> list[dict]:
    return [
        {
            "name": "Problem Fit",
            "description": "Fit for long-running AI agent workflows.",
            "weight": 0.25,
            "score": 4.2,
            "rationale": "Strong fit for graph-shaped, stateful workflows.",
            "evidence_ids": ["ev-docs-persistence"],
        },
        {
            "name": "Technical Capability",
            "description": "Durable execution, state, and control-flow capability.",
            "weight": 0.25,
            "score": 4.0,
            "rationale": "Core orchestration and persistence capabilities are well aligned.",
            "evidence_ids": ["ev-docs-persistence"],
        },
        {
            "name": "Maturity & Maintenance",
            "description": "Project maintenance, release activity, and ecosystem maturity.",
            "weight": 0.20,
            "score": 3.6,
            "rationale": "Adoption is plausible but production operations still require validation.",
            "evidence_ids": ["ev-github-maintenance"],
        },
        {
            "name": "Operational Complexity",
            "description": "Debugging, observability, and state management burden.",
            "weight": 0.15,
            "score": 3.4,
            "rationale": "Graph state and checkpointing add operational concepts teams must learn.",
            "evidence_ids": ["ev-engineering-ops"],
        },
        {
            "name": "Ecosystem & Alternatives",
            "description": "Documentation, examples, integrations, and relative fit versus alternatives.",
            "weight": 0.15,
            "score": 3.8,
            "rationale": "LangGraph is strong for durable workflows but not always the simplest option.",
            "evidence_ids": ["ev-github-maintenance"],
        },
    ]


def _report(scorecard: dict) -> dict:
    return {
        "title": "LangGraph Technology Evaluation",
        "target_technology": "LangGraph",
        "evaluation_context": "Evaluate LangGraph for long-running AI agent workflows.",
        "verdict": scorecard["verdict"],
        "final_score": scorecard["final_score"],
        "criteria": scorecard["criteria"],
        "evidence_items": [
            {
                "id": "ev-docs-persistence",
                "claim": "LangGraph is designed around graph-based stateful agent orchestration with persistence concepts.",
                "evidence_summary": "Official documentation describes graph state, checkpoints, and long-running workflow control.",
                "source_title": "LangGraph Persistence Documentation",
                "source_url": "https://langchain-ai.github.io/langgraph/concepts/persistence/",
                "source_type": "official_docs",
                "trust_level": "high",
                "support_status": "supports",
                "confidence": 0.9,
                "relevance": 0.95,
                "notes": "Use live documentation during a full research run to verify current APIs.",
            },
            {
                "id": "ev-github-maintenance",
                "claim": "LangGraph has an active open-source project and ecosystem around LangChain.",
                "evidence_summary": "Repository and release activity should be checked during live research before final adoption.",
                "source_title": "LangGraph GitHub Repository",
                "source_url": "https://github.com/langchain-ai/langgraph",
                "source_type": "official_github",
                "trust_level": "high",
                "support_status": "supports",
                "confidence": 0.8,
                "relevance": 0.85,
                "notes": "This deterministic test uses representative source metadata, not live repository inspection.",
            },
            {
                "id": "ev-engineering-ops",
                "claim": "Long-running workflows require explicit validation of checkpoint storage, observability, and recovery.",
                "evidence_summary": "Engineering evaluation should include failure injection and recovery tests before production rollout.",
                "source_title": "Production Agent Workflow Operations Notes",
                "source_url": "https://example.com/engineering/agent-workflow-ops",
                "source_type": "engineering_blog",
                "trust_level": "medium",
                "support_status": "partially_supports",
                "confidence": 0.7,
                "relevance": 0.8,
                "notes": "Representative evidence item used to exercise consistency and risk handling.",
            },
        ],
        "alternatives": [
            {
                "name": "AutoGen",
                "description": "Multi-agent conversation framework focused on agent collaboration patterns.",
                "category": "agent_framework",
                "strengths": ["Flexible multi-agent conversations", "Good for exploratory prototypes"],
                "weaknesses": ["Less directly focused on durable graph workflow state"],
                "best_fit_use_cases": ["Research prototypes", "Conversational multi-agent experiments"],
                "risks": ["May require extra infrastructure for long-running durable workflows"],
            },
            {
                "name": "CrewAI",
                "description": "Role/task-oriented multi-agent workflow framework.",
                "category": "agent_framework",
                "strengths": ["Simple mental model", "Task delegation ergonomics"],
                "weaknesses": ["Durability and stateful recovery need separate validation"],
                "best_fit_use_cases": ["Role-based automation", "Straightforward task pipelines"],
                "risks": ["May be less suitable for complex stateful graph workflows"],
            },
        ],
        "experiments": [
            {
                "name": "Checkpoint recovery spike",
                "description": "Run a minimal graph with checkpoint persistence and simulate interruption/recovery.",
                "command": None,
                "success": False,
                "logs_summary": "Not run in deterministic pipeline e2e; required for live adoption validation.",
                "reproducibility_score": 0.0,
                "notes": "This is a recommended experiment, not an executed result.",
            }
        ],
        "risks": ["Operational complexity around checkpointing and debugging must be validated."],
        "recommendation": "Run a production-like pilot before adopting broadly for long-running workflows.",
        "executive_summary": {
            "one_sentence_verdict": "LangGraph is recommended with constraints for long-running AI agent workflows.",
            "key_reasons": ["Strong fit for stateful graph orchestration", "Good alignment with durable workflow needs"],
            "major_risks": ["Operational complexity", "Need for recovery and observability validation"],
            "best_fit": "Teams building stateful, long-running agent workflows that need explicit control flow.",
        },
        "technology_overview": {
            "description": "LangGraph is a graph-oriented framework for building stateful agent workflows.",
            "problem_addressed": "Coordinating multi-step agent workflows with state, control flow, and persistence.",
            "primary_use_cases": ["Long-running agents", "Human-in-the-loop workflows", "Stateful orchestration"],
            "key_features": ["Graph execution", "Checkpoint persistence", "Stateful control flow"],
            "target_users": ["AI platform teams", "Agent application engineers"],
        },
        "core_capabilities": [
            {
                "name": "Durable stateful orchestration",
                "description": "Represents agent workflows as graphs with explicit state transitions.",
                "evidence_ids": ["ev-docs-persistence"],
                "maturity_level": "production-adjacent",
                "limitations": ["Requires workflow and checkpoint design discipline"],
            }
        ],
        "risk_register": [
            {
                "name": "Operational learning curve",
                "description": "Teams must learn graph debugging, state inspection, and checkpoint recovery.",
                "severity": "medium",
                "likelihood": "medium",
                "mitigation": "Run a pilot with tracing, recovery tests, and rollback criteria.",
                "evidence_ids": ["ev-engineering-ops"],
            }
        ],
        "open_questions": [
            {
                "question": "Does checkpoint storage meet the target system's recovery objectives?",
                "why_it_matters": "Recovery guarantees are central to long-running workflow adoption.",
                "suggested_validation": "Run failure injection against the intended deployment environment.",
            }
        ],
        "references": [
            {
                "title": "LangGraph Persistence Documentation",
                "url": "https://langchain-ai.github.io/langgraph/concepts/persistence/",
                "source_type": "official_docs",
                "publisher": "LangChain",
                "accessed_at": None,
                "notes": "Representative official source for deterministic pipeline validation.",
            },
            {
                "title": "LangGraph Persistence Documentation Duplicate",
                "url": "https://langchain-ai.github.io/langgraph/concepts/persistence/",
                "source_type": "official_docs",
                "publisher": "LangChain",
                "accessed_at": None,
                "notes": "Intentional duplicate to verify Consistency Notes rendering.",
            },
        ],
        "adoption_plan": {
            "recommendation": "Run a constrained production-like pilot before broad adoption.",
            "suggested_next_steps": ["Build a thin workflow slice", "Instrument checkpoint recovery", "Compare against AutoGen and CrewAI"],
            "validation_plan": ["Run quickstart", "Run interruption/recovery test", "Inspect trace/debug workflow"],
            "rollout_strategy": "Adopt for one long-running workflow after pilot evidence is collected.",
            "decision_deadline": "After pilot and recovery tests complete.",
        },
    }


def test_technology_evaluation_deterministic_pipeline_e2e(tmp_path: Path):
    storage = LocalSkillStorage(host_path=str(SKILLS_ROOT))
    skills = storage.load_skills(enabled_only=True)
    assert any(skill.name == "technology-evaluation" for skill in skills)
    assert "`technology-evaluation` skill" in prompt_module.SYSTEM_PROMPT_TEMPLATE
    assert "`evaluation_report_validate`" in prompt_module.SYSTEM_PROMPT_TEMPLATE
    assert "`evaluation_report_assembly`" in prompt_module.SYSTEM_PROMPT_TEMPLATE

    assert get_subagent_config("evidence-researcher") is not None
    assert get_subagent_config("alternative-analyst") is not None
    assert get_subagent_config("experiment-runner") is not None

    config = _make_minimal_config()
    with patch("deerflow.tools.tools.is_host_bash_allowed", return_value=True):
        tools = get_available_tools(include_mcp=False, app_config=config)
    tool_names = {tool.name for tool in tools}
    assert {"evaluation_scorecard", "evaluation_report_validate", "evaluation_report_assembly"} <= tool_names

    scorecard = evaluation_scorecard_tool.invoke(
        {
            "target_technology": "LangGraph",
            "evaluation_context": "Long-running AI agent workflows",
            "criteria": _criteria(),
            "evidence_count": 5,
            "critical_risks": None,
        }
    )
    assert scorecard["final_score"] == 3.85
    assert scorecard["verdict"] == "Recommended with constraints"

    report = _report(scorecard)
    validation = evaluation_report_validate_tool.invoke({"report": report})
    assert validation["passed"] is True
    assert validation["error_count"] == 0
    assert validation["warning_count"] > 0
    assert any(issue["code"] == "duplicate_reference_url" for issue in validation["warnings"])

    artifact = write_assembled_evaluation_report(tmp_path, report)
    json_path = Path(artifact["json_artifact"]["path"])
    markdown_path = Path(artifact["markdown_artifact"]["path"])
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    parsed = EvaluationReport.model_validate(payload)
    markdown = markdown_path.read_text(encoding="utf-8")

    for section in FIXED_SECTIONS:
        assert section in markdown
    assert "### Consistency Notes / 一致性备注" in markdown
    assert "duplicate_reference_url" in markdown
    assert "## 6. Evidence Matrix / 证据矩阵" in markdown
    assert "LangGraph is designed around graph-based stateful agent orchestration" in markdown
    assert "## 7. Evaluation Scorecard / 评分卡" in markdown
    assert "Problem Fit" in markdown
    assert "## 8. Alternative Comparison / 替代方案对比" in markdown
    assert "AutoGen" in markdown
    assert "CrewAI" in markdown
    assert "## 10. Risk Register / 风险清单" in markdown
    assert "Operational learning curve" in markdown

    assert parsed.target_technology == "LangGraph"
    assert parsed.verdict == "Recommended with constraints"
    assert parsed.final_score == 3.85
    assert f"**Verdict:** {parsed.verdict}" in markdown
    assert f"**Final score:** {parsed.final_score:.2f}" in markdown
    assert artifact["consistency_check"]["warnings"]


def test_langgraph_example_artifacts_are_valid():
    example_json = LANGGRAPH_EXAMPLE_DIR / "evaluation_report_langgraph.json"
    example_markdown = LANGGRAPH_EXAMPLE_DIR / "technology_evaluation_report_langgraph.md"
    example_input = LANGGRAPH_EXAMPLE_DIR / "input.md"
    example_readme = LANGGRAPH_EXAMPLE_DIR / "README.md"

    assert example_input.is_file()
    assert example_readme.is_file()
    payload = json.loads(example_json.read_text(encoding="utf-8"))
    parsed = EvaluationReport.model_validate(payload)
    markdown = example_markdown.read_text(encoding="utf-8")

    assert parsed.target_technology == "LangGraph"
    assert parsed.verdict == "Recommended with constraints"
    assert parsed.final_score == 3.85
    for section in FIXED_SECTIONS:
        assert section in markdown
    assert "### Consistency Notes / 一致性备注" in markdown
    assert "duplicate_reference_url" in markdown

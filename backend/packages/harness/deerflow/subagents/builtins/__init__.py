"""Built-in subagent configurations."""

from .bash_agent import BASH_AGENT_CONFIG
from .general_purpose import GENERAL_PURPOSE_CONFIG
from .technology_evaluation import ALTERNATIVE_ANALYST_CONFIG, EVIDENCE_RESEARCHER_CONFIG, EXPERIMENT_RUNNER_CONFIG

__all__ = [
    "GENERAL_PURPOSE_CONFIG",
    "BASH_AGENT_CONFIG",
    "EVIDENCE_RESEARCHER_CONFIG",
    "ALTERNATIVE_ANALYST_CONFIG",
    "EXPERIMENT_RUNNER_CONFIG",
]

# Registry of built-in subagents
BUILTIN_SUBAGENTS = {
    "general-purpose": GENERAL_PURPOSE_CONFIG,
    "bash": BASH_AGENT_CONFIG,
    "evidence-researcher": EVIDENCE_RESEARCHER_CONFIG,
    "alternative-analyst": ALTERNATIVE_ANALYST_CONFIG,
    "experiment-runner": EXPERIMENT_RUNNER_CONFIG,
}

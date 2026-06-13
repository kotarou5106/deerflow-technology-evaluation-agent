"""Write structured technology evaluation reports as JSON artifacts."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Annotated, Any

from langchain.tools import InjectedToolCallId, tool
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from deerflow.evaluation.schemas import EvaluationReport
from deerflow.tools.builtins.present_file_tool import OUTPUTS_VIRTUAL_PREFIX
from deerflow.tools.types import Runtime

_SAFE_FILENAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*\.json$")


def _slugify_target_technology(target_technology: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", target_technology.strip().lower())
    slug = slug.strip("_")
    return slug[:80] or "technology"


def _safe_report_filename(target_technology: str, filename: str | None = None) -> str:
    if filename is None:
        return f"evaluation_report_{_slugify_target_technology(target_technology)}.json"

    candidate = filename.strip()
    if not candidate.endswith(".json"):
        candidate = f"{candidate}.json"

    if "/" in candidate or "\\" in candidate or ".." in candidate:
        raise ValueError("EvaluationReport artifact filename must be a safe JSON basename")
    if not _SAFE_FILENAME_RE.fullmatch(candidate):
        raise ValueError("EvaluationReport artifact filename must contain only letters, numbers, dot, underscore, or hyphen")
    return candidate


def write_evaluation_report_artifact(
    outputs_path: str | Path,
    report: dict[str, Any],
    filename: str | None = None,
) -> dict[str, Any]:
    """Validate and write an EvaluationReport JSON file into the outputs directory."""
    evaluation_report = EvaluationReport.model_validate(report)
    safe_filename = _safe_report_filename(evaluation_report.target_technology, filename)
    outputs_dir = Path(outputs_path).expanduser().resolve()
    outputs_dir.mkdir(parents=True, exist_ok=True)

    output_path = outputs_dir / safe_filename
    content = json.dumps(evaluation_report.model_dump(mode="json"), ensure_ascii=False, indent=2)
    output_path.write_text(content + "\n", encoding="utf-8")

    return {
        "filename": safe_filename,
        "path": str(output_path),
        "virtual_path": f"{OUTPUTS_VIRTUAL_PREFIX}/{safe_filename}",
        "target_technology": evaluation_report.target_technology,
        "verdict": evaluation_report.verdict,
        "final_score": evaluation_report.final_score,
    }


@tool("evaluation_report_artifact", parse_docstring=True)
def evaluation_report_artifact_tool(
    runtime: Runtime,
    report: dict[str, Any],
    tool_call_id: Annotated[str, InjectedToolCallId],
    filename: str | None = None,
) -> Command:
    """Write a structured EvaluationReport JSON artifact for technology evaluation tasks.

    Use this tool at the end of a Technology Research & Evaluation Agent task
    when the Markdown Technology Evaluation Report is ready. It validates the
    supplied payload with the EvaluationReport schema and writes a JSON artifact
    for downstream rendering of Evidence Matrix, Evaluation Scorecard,
    Alternative Comparison, experiments, risks, and recommendation.

    This tool does not call an LLM, search the web, access the network, compute
    scorecards, or generate narrative report text. The final_score and verdict
    should come from the `evaluation_scorecard` tool when it is available.

    Args:
        report: EvaluationReport payload with target_technology, evaluation_context, verdict, final_score, criteria, evidence_items, alternatives, experiments, risks, and recommendation.
        filename: Optional safe JSON basename. If omitted, a filename is generated from target_technology.
    """
    if runtime.state is None:
        return Command(
            update={"messages": [ToolMessage("Error: Thread runtime state is not available", tool_call_id=tool_call_id)]},
        )

    thread_data = runtime.state.get("thread_data") or {}
    outputs_path = thread_data.get("outputs_path")
    if not outputs_path:
        return Command(
            update={"messages": [ToolMessage("Error: Thread outputs path is not available in runtime state", tool_call_id=tool_call_id)]},
        )

    try:
        artifact = write_evaluation_report_artifact(outputs_path, report, filename)
    except ValueError as exc:
        return Command(
            update={"messages": [ToolMessage(f"Error: {exc}", tool_call_id=tool_call_id)]},
        )

    message = json.dumps({"status": "created", **artifact}, ensure_ascii=False)
    return Command(
        update={
            "artifacts": [artifact["virtual_path"]],
            "messages": [ToolMessage(message, tool_call_id=tool_call_id)],
        },
    )

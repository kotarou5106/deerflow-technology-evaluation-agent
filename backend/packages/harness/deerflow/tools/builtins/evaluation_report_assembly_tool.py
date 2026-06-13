"""Assemble technology evaluation JSON and Markdown artifacts from one payload."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Annotated, Any

from langchain.tools import InjectedToolCallId, tool
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from pydantic import ValidationError

from deerflow.evaluation.consistency import check_evaluation_report_consistency
from deerflow.evaluation.report_renderer import render_evaluation_report_markdown
from deerflow.evaluation.schemas import EvaluationReport
from deerflow.tools.builtins.evaluation_report_artifact_tool import (
    _slugify_target_technology,
    write_evaluation_report_artifact,
)
from deerflow.tools.builtins.present_file_tool import OUTPUTS_VIRTUAL_PREFIX
from deerflow.tools.types import Runtime

_SAFE_MARKDOWN_FILENAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*\.md$")


def _safe_markdown_filename(target_technology: str, filename: str | None = None) -> str:
    if filename is None:
        return f"technology_evaluation_report_{_slugify_target_technology(target_technology)}.md"

    candidate = filename.strip()
    if not candidate.endswith(".md"):
        candidate = f"{candidate}.md"

    if "/" in candidate or "\\" in candidate or ".." in candidate:
        raise ValueError("Technology evaluation Markdown filename must be a safe Markdown basename")
    if not _SAFE_MARKDOWN_FILENAME_RE.fullmatch(candidate):
        raise ValueError("Technology evaluation Markdown filename must contain only letters, numbers, dot, underscore, or hyphen")
    return candidate


def write_assembled_evaluation_report(
    outputs_path: str | Path,
    report: dict[str, Any],
    json_filename: str | None = None,
    markdown_filename: str | None = None,
) -> dict[str, Any]:
    """Write EvaluationReport JSON and Markdown artifacts from the same validated payload."""
    parsed_report = EvaluationReport.model_validate(report)
    consistency = check_evaluation_report_consistency(parsed_report)
    if consistency.errors:
        messages = "; ".join(issue.message for issue in consistency.errors)
        raise ValueError(f"EvaluationReport consistency check failed: {messages}")

    markdown = render_evaluation_report_markdown(parsed_report, consistency_warnings=consistency.warnings)
    safe_markdown_filename = _safe_markdown_filename(parsed_report.target_technology, markdown_filename)

    outputs_dir = Path(outputs_path).expanduser().resolve()
    outputs_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = outputs_dir / safe_markdown_filename
    written_paths: list[Path] = []

    try:
        json_artifact = write_evaluation_report_artifact(
            outputs_dir,
            parsed_report.model_dump(mode="json"),
            filename=json_filename,
        )
        written_paths.append(Path(json_artifact["path"]))

        markdown_path.write_text(markdown, encoding="utf-8")
        written_paths.append(markdown_path)
    except Exception:
        for path in written_paths:
            if path.exists():
                path.unlink()
        raise

    markdown_artifact = {
        "filename": safe_markdown_filename,
        "path": str(markdown_path),
        "virtual_path": f"{OUTPUTS_VIRTUAL_PREFIX}/{safe_markdown_filename}",
    }

    return {
        "target_technology": parsed_report.target_technology,
        "verdict": parsed_report.verdict,
        "final_score": parsed_report.final_score,
        "consistency_check": consistency.model_dump(mode="json"),
        "json_artifact": json_artifact,
        "markdown_artifact": markdown_artifact,
        "artifacts": [json_artifact["virtual_path"], markdown_artifact["virtual_path"]],
    }


@tool("evaluation_report_assembly", parse_docstring=True)
def evaluation_report_assembly_tool(
    runtime: Runtime,
    report: dict[str, Any],
    tool_call_id: Annotated[str, InjectedToolCallId],
    json_filename: str | None = None,
    markdown_filename: str | None = None,
) -> Command:
    """Create consistent EvaluationReport JSON and Markdown artifacts from one payload.

    Use this tool at the final stage of a Technology Research & Evaluation Agent
    task after `evaluation_scorecard` has produced the final_score and verdict.
    The supplied EvaluationReport payload is the single source of truth: this
    tool validates it, writes the structured JSON artifact, renders the fixed
    Technology Evaluation Report Markdown from the same data, and exposes both
    files as artifacts.

    This tool does not call an LLM, search the web, access the network, compute
    scorecards, or independently revise the report content.

    Args:
        report: Complete EvaluationReport payload used as the single source of truth.
        json_filename: Optional safe JSON basename for the structured artifact.
        markdown_filename: Optional safe Markdown basename for the rendered report.
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
        artifact = write_assembled_evaluation_report(
            outputs_path,
            report,
            json_filename=json_filename,
            markdown_filename=markdown_filename,
        )
    except (OSError, ValidationError, ValueError) as exc:
        return Command(
            update={"messages": [ToolMessage(f"Error: {exc}", tool_call_id=tool_call_id)]},
        )

    message = json.dumps({"status": "created", **artifact}, ensure_ascii=False)
    return Command(
        update={
            "artifacts": artifact["artifacts"],
            "messages": [ToolMessage(message, tool_call_id=tool_call_id)],
        },
    )

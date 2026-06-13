# Technology Evaluation Live Research E2E

This guide describes how to validate the Technology Research & Evaluation Agent with a real model and live research tools.

Test input:

```text
Evaluate LangGraph for long-running AI agent workflows.
```

## Goal

Confirm that a real DeerFlow run can start from a technology evaluation question and produce:

- Markdown Technology Evaluation Report
- EvaluationReport JSON artifact
- deterministic `final_score` and `verdict`
- Evidence Matrix
- Evaluation Scorecard
- Alternative Comparison
- Risk Register
- Consistency Notes when validation warnings are present
- validate-before-assembly flow

This is a live research validation. It depends on real model credentials and network access, so it is not part of default CI.

## Observed Live Run

On a real live run for the test input above, the agent stream showed the core Technology Research & Evaluation Agent chain being triggered:

```text
tool_names:
- read_file
- web_search
- web_fetch
- evaluation_scorecard
- evaluation_report_validate
- evaluation_report_assembly
- present_files

artifacts:
- /mnt/user-data/outputs/langgraph-technology-evaluation.json
- /mnt/user-data/outputs/langgraph-technology-evaluation-report.md
```

This proves the real agent path can invoke live research tools, deterministic scorecard calculation, validate-before-assembly, report assembly, artifact presentation, and Markdown + JSON artifact output.

The live smoke test intentionally does not grade report content depth. It does not fail because a structured section such as `criteria`, `alternatives`, or `risk_register` is empty. Content quality should be evaluated separately with deterministic fixtures or human review.

## Prerequisites

1. Install project dependencies.

   ```bash
   make install
   ```

2. Create a local `config.yaml` from `config.example.yaml`.

   ```bash
   cp config.example.yaml config.yaml
   ```

3. Configure at least one model in `config.yaml`.

   Model entries live under `models:`. The examples in `config.example.yaml` use environment variables such as:

   ```text
   OPENAI_API_KEY
   ANTHROPIC_API_KEY
   GEMINI_API_KEY
   DEEPSEEK_API_KEY
   VOLCENGINE_API_KEY
   ```

4. Keep secrets outside the repository.

   Use shell exports or a local `.env` file that is not committed:

   ```bash
   export OPENAI_API_KEY="..."
   export TAVILY_API_KEY="..."
   ```

5. Confirm research tools are configured.

   `config.example.yaml` enables `web_search` through DuckDuckGo and `web_fetch` through Jina AI by default. Other providers such as Serper, Tavily, Exa, Browserless, InfoQuest, and Firecrawl can be enabled by editing local `config.yaml` and supplying their API keys through environment variables.

## Start Backend

Frontend is optional for this validation.

Backend-only Gateway API:

```bash
cd backend
make dev
```

This starts the Gateway API and embedded agent runtime on:

```text
http://localhost:8001
```

Full local app:

```bash
make dev
```

This starts the unified local endpoint:

```text
http://localhost:2026
```

## Lowest-Risk Validation Path

Use the Embedded Python Client for the first live research validation.

Why:

- It exercises the same lead agent, skill discovery, tool registry, subagent registry, model config, sandbox state, and artifact state.
- It does not require frontend startup.
- It avoids HTTP/Gateway setup noise while still producing the same `messages-tuple`, `values`, and artifact outputs.

Run the skipped live smoke test explicitly:

```bash
cd backend
TECHNOLOGY_EVALUATION_LIVE_E2E=1 PYTHONPATH=. uv run pytest tests/test_technology_evaluation_live_e2e.py -v -s
```

The test is skipped unless `TECHNOLOGY_EVALUATION_LIVE_E2E=1` is set. It also requires a project-root `config.yaml` with working model credentials.

Optional timeout override:

```bash
TECHNOLOGY_EVALUATION_LIVE_E2E_TIMEOUT_SECONDS=600
```

The timeout is a cost-control guard for the smoke test. It does not raise the agent recursion limit.

## Manual Embedded Client Run

From `backend/`, run:

```bash
PYTHONPATH=. uv run python - <<'PY'
import uuid

from deerflow.client import DeerFlowClient

thread_id = f"tech-eval-live-{uuid.uuid4().hex[:8]}"
prompt = """Evaluate LangGraph for long-running AI agent workflows.

Use the Technology Research & Evaluation Agent workflow. Research real sources, then call evaluation_scorecard, evaluation_report_validate, and evaluation_report_assembly before the final answer. Produce both EvaluationReport JSON and Markdown artifacts.
"""

client = DeerFlowClient(thinking_enabled=False, subagent_enabled=True)
events = list(client.stream(prompt, thread_id=thread_id, recursion_limit=160))

tool_names = []
artifacts = []
for event in events:
    if event.type == "messages-tuple" and event.data.get("type") == "ai":
        for tool_call in event.data.get("tool_calls", []):
            tool_names.append(tool_call.get("name"))
    if event.type == "values":
        artifacts = event.data.get("artifacts", []) or artifacts

print("thread_id:", thread_id)
print("tool_calls:", tool_names)
print("artifacts:", artifacts)
PY
```

## Gateway API Run

The Gateway exposes LangGraph-compatible paths under `/api/langgraph/*` when running through the unified endpoint and native Gateway routes under `/api/*`.

Use Gateway when you specifically need to validate HTTP streaming, browser behavior, or UI artifact download behavior. The Embedded Client path is preferred for the first live research check because it keeps the validation focused on the agent pipeline.

## Expected Observations

During a successful run, inspect streamed `messages-tuple` events and verify tool calls include:

- `web_search` or another configured search provider
- `web_fetch` or another configured fetch/crawl provider
- `evaluation_scorecard`
- `evaluation_report_validate`
- `evaluation_report_assembly`

If subagents are enabled and the model delegates work, tool calls may include:

- `task`
- `evidence-researcher`
- `alternative-analyst`
- `experiment-runner`

Subagent usage is model-dependent. A live run can still validate the core report pipeline without delegation if the lead agent completes the work itself.

## Confirm Artifacts

Inspect `values` events. The final state should include artifact paths similar to:

```text
/mnt/user-data/outputs/evaluation_report_langgraph.json
/mnt/user-data/outputs/technology_evaluation_report_langgraph.md
```

The exact artifact filenames are not part of the contract. Hyphenated names such as these are also valid:

```text
/mnt/user-data/outputs/langgraph-evaluation-report.json
/mnt/user-data/outputs/langgraph-evaluation-report.md
```

With the Embedded Client, artifacts can be read by thread id:

```python
content, mime_type = client.get_artifact(thread_id, "mnt/user-data/outputs/evaluation_report_langgraph.json")
```

The JSON artifact should validate against `EvaluationReport`. The Markdown report should contain the 13 fixed report sections from `skills/public/technology-evaluation/assets/report_template.md`.

## Confirm Markdown and JSON Consistency

Check that:

- JSON `verdict` equals the Markdown Final Verdict.
- JSON `final_score` equals the Markdown score.
- JSON parses as `EvaluationReport`.
- Markdown contains the 13 fixed Technology Evaluation Report sections.
- Consistency Notes appear in Markdown when `evaluation_report_validate` or `evaluation_report_assembly` returns warnings.

Warnings do not block report generation. Consistency errors must block `evaluation_report_assembly` from writing artifacts.

## How to Confirm Tool Calls

For Embedded Client streams:

- AI tool calls appear in `messages-tuple` events with `data.type == "ai"` and `data.tool_calls`.
- Tool results appear in `messages-tuple` events with `data.type == "tool"`.
- Artifacts appear in `values` events under `data.artifacts`.

The live test prints event-derived tool calls and artifact paths with `-s`.

## Common Failure Causes

- `config.yaml` does not exist in the project root.
- The configured model API key is missing or invalid.
- The configured model does not reliably support tool calling.
- Search or fetch provider is blocked by local network policy.
- Search provider rate limits the run.
- The model stops before calling `evaluation_report_assembly`.
- The report payload fails consistency validation because `evidence_ids` do not match `evidence_items`.
- The run needs a higher recursion limit for multi-step research.
- The run exceeds the smoke-test timeout because the model or provider stalls.

## Secrets Reminder

Do not commit:

- `config.yaml` containing real credentials
- `.env` containing real credentials
- copied API tokens in test files, docs, logs, or examples
- live run transcripts that include secrets

Use `.env.example` style placeholders in documentation and environment-variable references in config.

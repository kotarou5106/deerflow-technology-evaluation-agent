# Technology Research & Evaluation Agent

Evidence-backed technology evaluation agent built on DeerFlow.

这个项目用于评估一个技术、框架、协议、模型或开源项目是否值得学习、采用或投入生产试点。它会把模糊的技术问题转成结构化决策报告，并同时输出面向人阅读的 Markdown 报告和面向系统复用的 `EvaluationReport` JSON artifact。

核心定位：

> Technology Research & Evaluation Agent  
> A DeerFlow-based agent that turns vague technology questions into evidence-backed, scorecard-driven, auditable decision reports.

This project is built on DeerFlow and vertically extended for technology research and evaluation.

## Why This Project

普通 deep research agent 往往擅长生成长总结，但技术选型真正需要回答的是：

> 这个技术是否值得采用？在什么条件下值得采用？风险是什么？证据在哪里？

本项目把技术研究与评估流程结构化为：

- source research / 来源研究
- evidence extraction / 证据抽取
- Claim / Evidence / Conclusion 分离
- deterministic scorecard / 确定性评分卡
- evidence consistency check / 证据一致性校验
- report assembly / 报告组装
- JSON + Markdown artifacts / 双产物输出

它不是从零自研的新 agent 框架，而是在 DeerFlow 的 agent harness、skills、tools、subagents、sandbox 和 artifact 基础设施上，垂直扩展出面向技术采用决策的完整工作流。

## Architecture / 架构图

```text
User Question
  -> Lead Agent Routing
  -> technology-evaluation Skill
  -> Evidence Research / Alternative Analysis / Experiment Notes
  -> evaluation_scorecard
  -> evaluation_report_validate
  -> evaluation_report_assembly
  -> EvaluationReport JSON + Markdown Report
```

## Core Features

- **Technology Evaluation Workflow**：围绕“是否值得采用”组织研究，而不是只做资料总结。
- **Evidence Matrix**：把关键 claim 绑定到 evidence，降低无来源观点的权重。
- **Deterministic Evaluation Scorecard**：用非 LLM 的确定性评分引擎计算 `final_score` 和 `verdict`。
- **Alternative Comparison**：对比同类替代方案，分析 trade-off、best-fit use cases 和 risks。
- **Risk Register**：结构化记录风险、严重度、可能性、缓解方式和证据链接。
- **Evidence Consistency Check**：检查缺失 evidence id、低证据数量、source metadata 缺失、异常状态和重复引用。
- **Validate-before-Assembly**：最终组装前先预检 `EvaluationReport` payload，blocking error 会阻止 artifact 写出。
- **Dual Artifacts: JSON + Markdown**：同一份 `EvaluationReport` payload 生成 JSON artifact 和 Markdown report。
- **Live Smoke Test Path**：提供默认跳过的 live smoke test，用于手动验证真实模型和网络下的工具链。
- **DeerFlow Skill / Tool / Subagent Integration**：通过 DeerFlow 的 skill、built-in tool、subagent 和 artifact 机制接入真实运行路径。

## Normal Research Agent vs This Project

| 维度 | Normal research agent | This project |
| --- | --- | --- |
| output | 叙述型总结 | 固定结构的 Technology Evaluation Report |
| evidence traceability | 证据常常隐含在正文里 | Claim / Evidence / Conclusion 分离，并支持 evidence ids |
| scoring | 多数由模型自由生成 | `evaluation_scorecard` 确定性计算 |
| validation | 通常没有结构化预检 | schema validation + evidence consistency check |
| artifacts | 常见为纯文本或临时文件 | `EvaluationReport` JSON + Markdown report |
| auditability | 难以机器检查 | 可检查 JSON、warnings、references、score metadata |

## Example

示例目录：

```text
examples/technology-evaluation/langgraph/
```

示例输入：

```text
Evaluate LangGraph for long-running AI agent workflows.
```

示例产物：

- `examples/technology-evaluation/langgraph/evaluation_report_langgraph.json`
- `examples/technology-evaluation/langgraph/technology_evaluation_report_langgraph.md`

这个示例展示了如何把一个技术评估问题转成结构化报告，包括 verdict、scorecard、evidence、alternatives、risks 和 references。

## Report Output

最终 Markdown 报告遵循固定结构：

- Executive Summary
- Final Verdict
- Evaluation Context
- Technology Overview
- Core Capabilities
- Evidence Matrix
- Evaluation Scorecard
- Alternative Comparison
- Hands-on Validation
- Risk Register
- Adoption Recommendation
- Open Questions
- Consistency Notes
- References

JSON artifact 遵循 `EvaluationReport` schema，便于后续前端渲染 Evidence Matrix、Evaluation Scorecard、Alternative Comparison 和 Risk Register，而不是只能解析 Markdown。

## Frontend EvaluationReport Viewer

当前前端在打开符合 `EvaluationReport` 结构特征的 JSON artifact 时，会使用技术评估专用视图展示核心报告内容，而不是只显示原始 JSON。

该视图会渲染：

- verdict summary
- scorecard
- evidence matrix
- risk register
- alternatives
- references

普通 JSON artifact 仍保持原有 code view 行为。

## Implementation Highlights

本项目新增和改造的核心位置：

- `skills/public/technology-evaluation/`
- `skills/public/technology-evaluation/assets/report_template.md`
- `backend/packages/harness/deerflow/evaluation/`
- `evaluation_scorecard` built-in tool
- `evaluation_report_validate` built-in tool
- `evaluation_report_assembly` built-in tool
- technology evaluation subagents：
  - `evidence-researcher`
  - `alternative-analyst`
  - `experiment-runner`
- deterministic pipeline e2e
- default-skipped live smoke test
- `examples/technology-evaluation/`

这些改造让评分卡从“prompt 生成”升级为“deterministic engine 计算”，让最终报告从“文本产物”升级为“结构化 JSON + 人可读 Markdown”的双产物输出。

## Tests

主要测试类型：

- evaluation engine tests
- scorecard tool tests
- consistency tests
- report renderer / assembly tests
- deterministic pipeline e2e
- default-skipped live smoke test

运行 deterministic tests：

```bash
cd backend
uv run pytest \
  tests/test_evaluation_engine.py \
  tests/test_evaluation_scorecard_tool.py \
  tests/test_evaluation_report_validate_tool.py \
  tests/test_evaluation_consistency.py \
  tests/test_evaluation_report_assembly.py \
  tests/test_technology_evaluation_pipeline_e2e.py
```

运行 live smoke test 的默认跳过路径：

```bash
cd backend
uv run pytest tests/test_technology_evaluation_live_e2e.py -q
```

live smoke test 默认 skip。手动启用需要设置：

```bash
TECHNOLOGY_EVALUATION_LIVE_E2E=1
```

注意：live smoke test 依赖真实模型、网络、search/fetch provider 状态和供应商响应速度，不作为默认 CI。

## Running with DeepSeek

本项目可以使用 OpenAI-compatible provider，例如 DeepSeek。

请只通过环境变量读取 API key，不要把真实 key 写进 `config.yaml`，也不要提交 `.env`。

`.env.example` 风格示例：

```bash
DEEPSEEK_API_KEY=your_deepseek_api_key
```

`config.yaml` 示例：

```yaml
models:
  - name: deepseek-v4-flash
    display_name: DeepSeek V4 Flash
    use: langchain_openai:ChatOpenAI
    model: deepseek-v4-flash
    api_key: $DEEPSEEK_API_KEY
    base_url: https://api.deepseek.com
    request_timeout: 600.0
    max_retries: 2
    max_tokens: 8192
    temperature: 0.2
    supports_thinking: false
    supports_reasoning_effort: false
    supports_vision: false
```

`config.yaml` 和 `.env` 是本地配置文件，不应提交到 GitHub。

## Live E2E

live e2e 操作文档：

```text
examples/technology-evaluation/live_e2e/
```

已经观察到真实 live run 触发了核心工具链：

- `web_search` / `web_fetch`
- `evaluation_scorecard`
- `evaluation_report_validate`
- `evaluation_report_assembly`
- `present_files`
- JSON artifact
- Markdown artifact

这说明 Technology Research & Evaluation Agent 已经可以在真实 agent 运行路径中完成研究、评分、预检、报告组装和 artifact 输出。

同时需要明确：live run 依赖真实模型、网络和 provider 状态，可能较慢，也可能因为供应商、网络或模型 tool calling 行为而波动。它验证 pipeline path，不评估最终报告质量，不作为默认 CI。

## How To Run Locally

安装依赖：

```bash
make install
```

创建本地配置：

```bash
cp config.example.yaml config.yaml
```

把 secrets 放在 `.env` 或 shell 环境变量里，不要提交。

启动完整本地应用：

```bash
make dev
```

只启动 backend：

```bash
cd backend
make dev
```

## Limitations

- live research quality depends on model and search/fetch providers。
- subagent usage is model-dependent。
- smoke test verifies pipeline, not final report quality。
- frontend currently uses DeerFlow's artifact display; dedicated EvaluationReport viewer is future work。
- evidence freshness depends on available sources at run time。

## Roadmap / Future Work

- EvaluationReport viewer in frontend
- more real technology evaluation examples
- replay/golden fixture from live run
- richer source ranking
- deeper experiment runner integration

## Attribution / 致谢

Built on DeerFlow.

This repository vertically extends DeerFlow for technology research and evaluation.

Original DeerFlow project provides the agent harness, skills system, tools, subagents, sandbox, and frontend artifact infrastructure.

原始项目：

- [bytedance/deer-flow](https://github.com/bytedance/deer-flow)
- [DeerFlow website](https://deerflow.tech)

## Documentation Links

- [Contributing Guide](./CONTRIBUTING.md)
- [Security Policy](./SECURITY.md)
- [Code of Conduct](./CODE_OF_CONDUCT.md)
- [Backend Architecture](./backend/README.md)
- [Configuration Guide](./backend/docs/CONFIGURATION.md)

## License

This project follows the original repository license. See [LICENSE](./LICENSE).

## Security

不要提交 `.env`、`config.yaml`、API keys、provider tokens，或包含 secrets 的 live run logs。更多安全说明见 [SECURITY.md](./SECURITY.md)。

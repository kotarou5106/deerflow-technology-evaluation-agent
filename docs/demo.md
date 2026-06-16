# 技术研究与评估 Agent 展示说明

## 1. 项目概览

**项目名称：技术研究与评估 Agent（Technology Research & Evaluation Agent）**

这是一个基于 DeerFlow 的垂直 Agent，用于把模糊的技术选型问题转化为带证据链、评分卡、一致性检查和结构化产物的决策报告。它不是只展示一段聊天结果，而是把技术研究拆成可追踪、可校验、可交付的流程。

当前公开展示以静态 Demo 为主：

- 静态路由：`/demo/technology-evaluation`
- GitHub 仓库：[deerflow-technology-evaluation-agent](https://github.com/kotarou5106/deerflow-technology-evaluation-agent)
- 中文 Demo 截图：

![技术研究与评估 Agent 中文 Demo](images/technology-evaluation/demo-page.png)

## 2. 为什么需要这个 Agent

普通聊天式技术调研很容易停留在“看起来合理”的自然语言回答上，但在工程决策、招聘展示或项目审阅场景中，通常还需要回答这些问题：

- 结论是否有稳定结构，能否被后续系统读取；
- 证据与结论之间是否可以追踪；
- 不同候选方案是否使用同一套评价标准；
- 报告是否存在字段缺失、内部矛盾或未说明的风险；
- 输出能否进入审批、归档、前端展示或后续自动化流程。

本项目用 `EvaluationReport` 作为核心报告结构，用确定性评分卡（Deterministic Evaluation Scorecard）表达评价标准，用结构模式校验（Schema Validation）防止关键字段缺失，用一致性检查（Consistency Check）降低结论与证据不一致的风险，最终生成 JSON 和 Markdown 两种结构化产物（Artifact）。

## 3. 完整工作流

真实链路按照以下顺序执行：

```text
用户问题
→ Technology Evaluation Skill
→ Web Search / Evidence Gathering
→ Alternative Analysis
→ Evaluation Scorecard
→ EvaluationReport Schema Validation
→ Consistency Check
→ Evaluation Report Assembly
→ JSON Artifact
→ Markdown Artifact
```

关键概念：

- 技术评估技能（Technology Evaluation Skill）：面向技术选型问题的专用执行流程。
- 证据收集（Evidence Gathering）：通过 Web Search 和来源整理建立证据矩阵。
- 方案分析（Alternative Analysis）：对目标技术和替代方案进行统一维度比较。
- 评分卡（Evaluation Scorecard）：用固定维度和权重生成可解释的最终评分。
- 结构模式校验（Schema Validation）：在产物写出前校验 `EvaluationReport` 结构。
- 一致性检查（Consistency Check）：检查摘要、评分、风险和建议之间是否互相冲突。
- 产物组装（Artifact Assembly）：将通过校验的报告组装为 JSON 与 Markdown。

## 4. 关键能力

### 证据研究与来源追踪

报告包含 Evidence Matrix，将关键论断、证据文本、来源标题、来源 URL、来源类型、可信度、支持关系和置信度组织在同一结构中。审阅者可以从结论反查证据来源，而不是只能阅读不可验证的摘要。

### 确定性评分卡

确定性评分卡（Deterministic Evaluation Scorecard）使用固定维度、权重和评分规则生成 `final_score` 与 `verdict`。它把“推荐 / 不推荐”变成可审阅的计算结果，避免每次模型自由发挥不同评价口径。

### Schema Validation 与 Consistency Check

结构模式校验（Schema Validation）用于确认报告字段完整、类型正确、结构可被前端和后续系统消费。一致性检查（Consistency Check）用于降低内部矛盾，例如评分偏低但结论强烈推荐、风险与建议不匹配等问题。

### JSON + Markdown 双 Artifact

JSON Artifact 适合系统消费、自动验证、前端渲染和后续自动化。Markdown Artifact 适合人工审阅、展示、归档和在 GitHub 中直接阅读。两者来自同一份报告结构，避免“展示版本”和“系统版本”语义分叉。

### EvaluationReport Viewer

静态 Demo 页面使用 `EvaluationReport Viewer` 渲染真实 fixture，按报告结构展示结论、证据、评分、风险和建议。这让招聘者或审阅者可以直接看到最终产品形态，而不是只看日志或 README。

### 静态 Demo 回放

当前长期展示采用静态回放模式。页面读取已生成的 `EvaluationReport` fixture，不调用后端、不调用大模型，也不消耗在线推理成本。它用于稳定展示真实链路已经生成过的报告，而不是伪装成实时 Agent。

### ECS live deployment proof

项目曾在阿里云 ECS 上完成真实 full-stack 部署，并跑通 DeepSeek、Web Search、评分、校验和产物组装链路。ECS 仅在需要真实演示时临时启动；当前采用节省成本的停机模式。

## 5. 真实线上运行证明

以下只列已经发生过的事实，不包含虚构用户量、准确率、性能提升或商业指标：

- 部署环境为阿里云香港 ECS；
- 操作系统为 Ubuntu 22.04；
- 使用 Docker Compose 完成 full-stack 部署；
- Gateway、Nginx、Frontend 成功启动；
- 公网 `/health` 返回 `healthy`；
- DeerFlow setup 与 workspace 可正常使用；
- DeepSeek 模型调用成功；
- Web Search 与证据整理成功；
- Evaluation Scorecard 成功调用；
- EvaluationReport Validate 通过；
- EvaluationReport Assembly 成功；
- 成功生成 JSON 与 Markdown 两个 Artifact。

该 ECS 当前已经停止，并采用节省成本的停机模式。它不是当前持续在线服务；需要 live demo 时可以临时启动。

## 6. 真实运行产物

真实 ECS live run 生成了两份结构化产物：

- [JSON 报告](../examples/technology-evaluation/live_run/langgraph-technology-evaluation-report.json)
- [Markdown 报告](../examples/technology-evaluation/live_run/langgraph-technology-evaluation-report.md)

JSON 报告适合系统消费、Schema 校验、前端 Viewer 渲染和后续自动化。Markdown 报告适合人工审阅、项目展示和长期归档。

## 7. 静态 Demo

![技术研究与评估 Agent 中文 Demo](images/technology-evaluation/demo-page.png)

静态 Demo 的定位是长期、稳定、低成本展示：

- 页面使用真实 `EvaluationReport` fixture；
- 页面不调用后端和大模型；
- 适合部署到 Vercel 进行长期零成本或低成本展示；
- 与 ECS live run 使用相同的核心报告结构；
- 静态 Demo 不是用来伪装 live Agent，而是用于稳定展示真实链路已经生成过的报告。

## 8. 三种展示模式

| 展示模式 | 用途 | 成本与风险 |
| --- | --- | --- |
| GitHub + README + screenshots | 快速说明项目背景、架构和结果 | 成本最低，适合异步审阅 |
| Vercel static demo | 展示中文产品化页面和 EvaluationReport Viewer | 不需要持续运行后端或模型 |
| ECS live demo | 展示真实 Agent 调用、搜索、评分、校验和 Artifact 生成 | 只在需要真实演示时临时启动 |

这三种模式对应不同审阅深度：GitHub 负责可读性，静态 Demo 负责产品展示，ECS live demo 负责证明链路真的可运行。

## 9. 已验证内容

已完成或已通过的验证包括：

- 前端 lint；
- Next.js production build；
- `/demo/technology-evaluation` 静态预渲染；
- frontend Docker image build；
- EvaluationReport schema tests；
- ECS live run；
- JSON validity；
- Artifact assembly。

这里不虚构测试数量。验证清单的重点是覆盖展示链路、构建链路、报告结构和真实运行产物。

## 10. 限制与成本

需要如实说明的限制：

- 深度技术研究的 token 消耗较大；
- 一次成功 live run 大约消耗 429.6K tokens；
- 真实运行速度受搜索、证据整理、模型调用、评分、校验和组装步骤影响；
- 当前静态 Demo 不代表实时模型调用；
- 结果质量仍依赖证据质量、来源可信度和模型推理能力；
- live demo 需要谨慎控制访问范围，避免公开流量消耗模型额度。

因此，长期展示采用静态回放，真实 ECS live demo 只在需要证明端到端能力时启动。

export const EVALUATION_TOPIC =
  "评估 LangGraph 是否适合作为长期运行 AI Agent 工作流引擎";

export type WorkflowFile = {
  name: string;
  kind: "working" | "artifact";
};

export type WorkflowStep = {
  label: string;
  detail: string;
  file: WorkflowFile;
};

export const EVALUATION_WORKFLOW_STEPS: WorkflowStep[] = [
  {
    label: "解析评估主题",
    detail: "识别评估对象、采用决策与长期运行约束",
    file: { name: "topic-analysis.md", kind: "working" },
  },
  {
    label: "拆解评估维度",
    detail: "建立状态管理、恢复能力、可观测性与成本维度",
    file: { name: "evaluation-dimensions.md", kind: "working" },
  },
  {
    label: "收集证据",
    detail: "汇总官方文档、架构资料与工程实践证据",
    file: { name: "evidence-collection.md", kind: "working" },
  },
  {
    label: "对比替代方案",
    detail: "与 OpenAI Agents SDK、Temporal 等方案横向比较",
    file: { name: "alternative-comparison.md", kind: "working" },
  },
  {
    label: "生成评分矩阵",
    detail: "按权重计算适配度，并保留评分依据",
    file: { name: "scorecard.md", kind: "working" },
  },
  {
    label: "登记风险",
    detail: "记录恢复复杂度、生态锁定与运维风险",
    file: { name: "risk-register.md", kind: "working" },
  },
  {
    label: "执行一致性检查",
    detail: "校验结论、证据、评分与风险是否相互支持",
    file: { name: "consistency-check.md", kind: "working" },
  },
  {
    label: "组装 EvaluationReport.json",
    detail: "生成可供系统读取的结构化评估结果",
    file: { name: "EvaluationReport.json", kind: "artifact" },
  },
  {
    label: "输出 EvaluationReport.md",
    detail: "生成适合评审与归档的可读报告",
    file: { name: "EvaluationReport.md", kind: "artifact" },
  },
];

export function getWorkflowSnapshot(activeIndex: number) {
  const boundedIndex = Math.max(
    0,
    Math.min(activeIndex, EVALUATION_WORKFLOW_STEPS.length),
  );

  return {
    completedSteps: EVALUATION_WORKFLOW_STEPS.slice(0, boundedIndex),
    activeStep: EVALUATION_WORKFLOW_STEPS[boundedIndex],
    visibleFiles: EVALUATION_WORKFLOW_STEPS.slice(0, boundedIndex + 1).map(
      (step) => step.file,
    ),
  };
}

import type { Metadata } from "next";

import { TechnologyEvaluationDemo } from "./_components/technology-evaluation-demo";
import { loadTechnologyEvaluationDemoReport } from "./_lib/load-demo-report";

export const dynamic = "force-static";

export const metadata: Metadata = {
  title: "技术研究与评估 Agent Demo",
  description:
    "基于 DeerFlow 的技术研究与评估 Agent 静态回放页面，展示带证据链、评分卡、结构校验和产物组装的 EvaluationReport。",
};

export default async function TechnologyEvaluationDemoPage() {
  const report = await loadTechnologyEvaluationDemoReport();

  return <TechnologyEvaluationDemo report={report} />;
}

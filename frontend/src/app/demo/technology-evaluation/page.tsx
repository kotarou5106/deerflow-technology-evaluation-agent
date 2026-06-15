import type { Metadata } from "next";

import { TechnologyEvaluationDemo } from "./_components/technology-evaluation-demo";
import { loadTechnologyEvaluationDemoReport } from "./_lib/load-demo-report";

export const dynamic = "force-static";

export const metadata: Metadata = {
  title: "Technology Evaluation Agent Demo",
  description:
    "Static demo of the DeerFlow-based Technology Research & Evaluation Agent.",
};

export default async function TechnologyEvaluationDemoPage() {
  const report = await loadTechnologyEvaluationDemoReport();

  return <TechnologyEvaluationDemo report={report} />;
}

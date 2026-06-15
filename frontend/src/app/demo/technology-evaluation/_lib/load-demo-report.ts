import { readFile } from "node:fs/promises";
import path from "node:path";

import type { EvaluationReportArtifact } from "@/components/workspace/artifacts/evaluation-report-viewer";

export async function loadTechnologyEvaluationDemoReport(): Promise<EvaluationReportArtifact> {
  const reportPath = path.join(
    process.cwd(),
    "..",
    "examples",
    "technology-evaluation",
    "langgraph",
    "evaluation_report_langgraph.json",
  );
  const content = await readFile(reportPath, "utf-8");
  return JSON.parse(content) as EvaluationReportArtifact;
}

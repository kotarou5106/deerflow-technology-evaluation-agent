import { describe, expect, test } from "vitest";

import { parseEvaluationReportArtifact } from "@/components/workspace/artifacts/evaluation-report-viewer";

describe("parseEvaluationReportArtifact", () => {
  test("identifies EvaluationReport JSON artifacts with the expected shape", () => {
    const report = parseEvaluationReportArtifact({
      filepath: "evaluation_report_langgraph.json",
      content: JSON.stringify({
        target_technology: "LangGraph",
        verdict: "Recommended with constraints",
        final_score: 3.85,
        criteria: [],
      }),
    });

    expect(report?.target_technology).toBe("LangGraph");
  });

  test("does not treat ordinary JSON artifacts as EvaluationReport payloads", () => {
    const report = parseEvaluationReportArtifact({
      filepath: "tool-output.json",
      content: JSON.stringify({
        status: "ok",
        records: [{ id: 1 }],
      }),
    });

    expect(report).toBeNull();
  });

  test("ignores invalid JSON and non-json paths", () => {
    expect(
      parseEvaluationReportArtifact({
        filepath: "evaluation_report.json",
        content: "{not-json",
      }),
    ).toBeNull();

    expect(
      parseEvaluationReportArtifact({
        filepath: "evaluation_report.txt",
        content: JSON.stringify({
          target_technology: "LangGraph",
          verdict: "Recommended",
          final_score: 4,
          evidence_items: [],
        }),
      }),
    ).toBeNull();
  });
});

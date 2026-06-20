import { cn } from "@/lib/utils";

import { EvaluationWorkflowDemo } from "../evaluation-workflow-demo";
import { Section } from "../section";

export function SkillsSection({ className }: { className?: string }) {
  return (
    <Section
      className={cn("w-full bg-white/2", className)}
      title="评估工作流"
      subtitle="输入一个技术主题，观看 Agent 如何推进证据、评分、风险与报告交付"
    >
      <div className="mt-10">
        <EvaluationWorkflowDemo />
      </div>
    </Section>
  );
}

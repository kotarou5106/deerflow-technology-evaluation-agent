"use client";

import MagicBento, { type BentoCardProps } from "@/components/ui/magic-bento";

import { Section } from "../section";

const COLOR = "#0a0a0a";
const capabilities: BentoCardProps[] = [
  { color: COLOR, label: "Evidence", title: "证据驱动", description: "围绕公开资料、项目文档、技术生态和风险信息收集证据。" },
  { color: COLOR, label: "Comparison", title: "替代方案比较", description: "将目标技术与可替代方案放入同一评估框架中比较。" },
  { color: COLOR, label: "Scorecard", title: "评分矩阵", description: "围绕适用性、成熟度、工程复杂度、维护成本和风险等维度打分。" },
  { color: COLOR, label: "Risk", title: "风险登记", description: "记录采用过程中的技术风险、部署风险、供应商风险和长期维护风险。" },
  { color: COLOR, label: "Consistency", title: "一致性检查", description: "对评分、风险、结论和采用建议进行一致性校验，减少报告前后矛盾。" },
  { color: COLOR, label: "Artifacts", title: "结构化产物", description: "输出 JSON 与 Markdown 双格式报告，便于下载、复核、归档和展示。" },
];

export function WhatsNewSection() {
  return (
    <Section title="核心能力" subtitle="不是普通聊天 Bot，而是面向技术评估的结构化 Agent 工作流">
      <div className="flex w-full items-center justify-center">
        <MagicBento data={capabilities} />
      </div>
    </Section>
  );
}

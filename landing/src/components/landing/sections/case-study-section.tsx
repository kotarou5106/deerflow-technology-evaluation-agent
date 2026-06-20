import { Card } from "@/components/ui/card";

import { Section } from "../section";

const evaluationCases = [
  {
    title: "评估 LangGraph 是否适合作为长期运行 AI Agent 工作流引擎",
    description: "围绕状态管理、长任务运行、工具调用、可观测性和部署成本进行评估。",
  },
  {
    title: "比较 LangGraph 与 OpenAI Agents SDK 等工作流方案",
    description: "从工作流表达能力、工具生态、工程复杂度和长期维护成本进行对比。",
  },
  {
    title: "评估某个开源项目是否值得引入业务系统",
    description: "结合项目活跃度、文档质量、风险点、替代方案和采用建议形成报告。",
  },
  {
    title: "评估一个新模型 API 是否适合接入产品",
    description: "分析价格、稳定性、上下文长度、工具调用能力、延迟和供应商风险。",
  },
  {
    title: "为一个技术方案生成采用建议",
    description: "输出推荐等级、风险登记、迁移路径和阶段性落地计划。",
  },
  {
    title: "生成结构化技术调研报告",
    description: "将调研过程沉淀为 JSON 与 Markdown 双格式产物，便于归档和展示。",
  },
];

export function CaseStudySection({ className }: { className?: string }) {
  return (
    <Section className={className} title="示例评估场景" subtitle="这些是该 Agent 适合处理的技术评估任务">
      <div className="container-md mt-8 grid grid-cols-1 gap-4 px-4 md:grid-cols-2 md:px-20 lg:grid-cols-3">
        {evaluationCases.map((caseStudy, index) => (
          <Card
            key={caseStudy.title}
            className="group/card relative h-64 overflow-hidden border-white/10 bg-zinc-950"
          >
            <div
              className="absolute inset-0 z-0 transition-all duration-300 group-hover/card:scale-110"
              style={{
                background:
                  index % 3 === 0
                    ? "radial-gradient(circle at 20% 20%, rgba(56, 189, 248, 0.32), transparent 34%), linear-gradient(135deg, rgba(12, 12, 18, 1), rgba(39, 39, 42, 0.75))"
                    : index % 3 === 1
                      ? "radial-gradient(circle at 80% 10%, rgba(244, 114, 182, 0.3), transparent 36%), linear-gradient(135deg, rgba(10, 10, 10, 1), rgba(24, 24, 27, 0.82))"
                      : "radial-gradient(circle at 65% 35%, rgba(52, 211, 153, 0.26), transparent 38%), linear-gradient(135deg, rgba(9, 9, 11, 1), rgba(31, 41, 55, 0.8))",
              }}
            />
            <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.05)_1px,transparent_1px)] bg-size-[24px_24px] opacity-30" />
            <div className="relative z-10 flex h-full flex-col justify-end p-5">
              <h3 className="text-xl leading-7 font-bold text-shadow-black">{caseStudy.title}</h3>
              <p className="mt-3 text-sm leading-6 text-white/78 text-shadow-black">{caseStudy.description}</p>
            </div>
          </Card>
        ))}
      </div>
    </Section>
  );
}

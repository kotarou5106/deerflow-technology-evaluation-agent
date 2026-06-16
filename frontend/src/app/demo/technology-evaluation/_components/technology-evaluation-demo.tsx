import {
  ArrowUpRightIcon,
  CheckCircle2Icon,
  ClipboardCheckIcon,
  DatabaseIcon,
  GitBranchIcon,
  GithubIcon,
  LockKeyholeIcon,
  SearchCheckIcon,
  ServerIcon,
} from "lucide-react";
import type { ReactNode } from "react";

import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { EvaluationReportViewer } from "@/components/workspace/artifacts/evaluation-report-viewer";
import type { EvaluationReportArtifact } from "@/components/workspace/artifacts/evaluation-report-viewer";
import { cn } from "@/lib/utils";

const GITHUB_URL =
  "https://github.com/kotarou5106/deerflow-technology-evaluation-agent";

const WORKFLOW_STAGES = [
  "问题定义",
  "证据研究",
  "方案比较",
  "确定性评分",
  "Schema 校验",
  "一致性检查",
  "JSON / Markdown 产物",
];

const RUN_PROOFS = [
  "阿里云 ECS 全栈部署成功",
  "DeerFlow Gateway 健康检查成功",
  "DeepSeek 模型调用成功",
  "Web Search 与证据整理成功",
  "Evaluation Scorecard 调用成功",
  "EvaluationReport Validate 通过",
  "EvaluationReport Assembly 成功",
  "生成 JSON 和 Markdown 两个 Artifact",
];

export function TechnologyEvaluationDemo({
  report,
}: {
  report: EvaluationReportArtifact;
}) {
  return (
    <main className="bg-background text-foreground min-h-screen">
      <section className="border-b">
        <div className="mx-auto grid w-full max-w-7xl gap-8 px-5 py-8 md:px-8 lg:min-h-[86vh] lg:grid-cols-[minmax(0,0.96fr)_minmax(420px,1.04fr)] lg:items-center lg:py-10">
          <div className="flex max-w-3xl flex-col gap-6">
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant="secondary">中文项目展示</Badge>
              <Badge variant="outline">静态回放，不调用后端</Badge>
            </div>
            <div className="space-y-4">
              <h1 className="max-w-3xl text-4xl leading-tight font-semibold tracking-normal md:text-5xl">
                技术研究与评估 Agent
              </h1>
              <p className="text-muted-foreground max-w-2xl text-lg leading-8">
                技术研究与评估 Agent（Technology Research & Evaluation
                Agent）基于
                DeerFlow，将模糊的技术选型问题转化为带证据链、评分卡、结构校验和可交付产物的决策报告。
              </p>
              <p className="text-muted-foreground max-w-2xl leading-7">
                这是基于真实 EvaluationReport fixture
                的静态回放页面。页面不调用后端和大模型，但相同报告结构已经在 ECS
                真实运行中通过 DeepSeek、评分、校验和组装链路真实生成。
              </p>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              <Signal
                icon={<GitBranchIcon className="size-4" />}
                label="示例问题"
                value="评估 LangGraph 是否适合长任务、多步骤的 AI Agent 工作流"
              />
              <Signal
                icon={<DatabaseIcon className="size-4" />}
                label="回放数据"
                value="使用已生成的 EvaluationReport JSON，由产品内 Viewer 直接渲染"
              />
            </div>

            <div className="flex flex-wrap gap-3">
              <a className={cn(buttonVariants({ size: "lg" }))} href="#report">
                查看结构化报告
              </a>
              <a
                className={cn(
                  buttonVariants({ variant: "outline", size: "lg" }),
                )}
                href={GITHUB_URL}
                rel="noopener noreferrer"
                target="_blank"
              >
                <GithubIcon className="size-4" />
                查看源码
                <ArrowUpRightIcon className="size-4" />
              </a>
            </div>
          </div>

          <Card className="rounded-lg shadow-none">
            <CardContent className="p-5">
              <div className="mb-4 flex items-center justify-between gap-3">
                <div>
                  <h2 className="text-base font-semibold">工作流链路</h2>
                  <p className="text-muted-foreground mt-1 text-sm">
                    从开放式问题到结构化产物（Artifact），每一步都对应可检查的中间结果。
                  </p>
                </div>
                <ServerIcon className="text-muted-foreground size-5 shrink-0" />
              </div>
              <ol className="grid gap-3">
                {WORKFLOW_STAGES.map((stage, index) => (
                  <li
                    className="grid grid-cols-[32px_minmax(0,1fr)] items-center gap-3 rounded-md border p-3"
                    key={stage}
                  >
                    <span className="bg-muted text-muted-foreground flex size-8 items-center justify-center rounded-md text-sm font-medium">
                      {index + 1}
                    </span>
                    <span className="min-w-0 font-medium">{stage}</span>
                  </li>
                ))}
              </ol>
            </CardContent>
          </Card>
        </div>
      </section>

      <section className="border-b">
        <div className="mx-auto grid w-full max-w-7xl gap-4 px-5 py-6 md:grid-cols-3 md:px-8">
          <Signal
            icon={<CheckCircle2Icon className="size-4" />}
            label="确定性报告结构"
            value="评分卡（Evaluation Scorecard）和 EvaluationReport 使用稳定字段表达方案、证据、风险和结论。"
          />
          <Signal
            icon={<ClipboardCheckIcon className="size-4" />}
            label="校验与一致性"
            value="模式校验（Schema Validation）和一致性检查（Consistency Check）用于发现结构缺失和结论冲突。"
          />
          <Signal
            icon={<LockKeyholeIcon className="size-4" />}
            label="公开演示安全"
            value="静态页面不会暴露模型密钥，也不会触发实时 Agent 运行或额外推理成本。"
          />
        </div>
      </section>

      <section className="border-b">
        <div className="mx-auto grid w-full max-w-7xl gap-6 px-5 py-8 md:px-8 lg:grid-cols-[0.78fr_1.22fr]">
          <div>
            <Badge variant="outline">真实运行证明</Badge>
            <h2 className="mt-3 text-2xl font-semibold tracking-normal">
              已在 ECS 上跑通过完整链路
            </h2>
            <p className="text-muted-foreground mt-3 leading-7">
              这里不展示虚构指标，只列出已经发生过的工程事实：从部署、健康检查、模型调用，到证据整理、评分、校验、组装和双
              Artifact 生成。
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            {RUN_PROOFS.map((proof) => (
              <div
                className="bg-card text-card-foreground flex items-start gap-3 rounded-lg border p-4"
                key={proof}
              >
                <SearchCheckIcon className="text-muted-foreground mt-0.5 size-4 shrink-0" />
                <span className="text-sm leading-6">{proof}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="report" className="bg-muted/20">
        <div className="mx-auto w-full max-w-7xl px-0 py-6 md:px-8 md:py-8">
          <div className="px-5 md:px-0">
            <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
              <div>
                <h2 className="text-2xl font-semibold tracking-normal">
                  EvaluationReport 报告查看器
                </h2>
                <p className="text-muted-foreground mt-2 max-w-4xl leading-7">
                  下方是同一个结构化报告（EvaluationReport）的产品化查看器。它读取
                  JSON fixture
                  并按报告结构展示结论、证据、评分、风险和建议；在完整链路中也会同步产出
                  JSON 与 Markdown 两个结构化产物（Artifact）。
                </p>
              </div>
              <Badge variant="outline">LangGraph 评估示例</Badge>
            </div>
          </div>
          <div className="bg-background overflow-hidden border md:rounded-lg">
            <EvaluationReportViewer
              className="max-h-none min-h-[720px] px-4 py-4 md:px-5"
              report={report}
            />
          </div>
        </div>
      </section>
    </main>
  );
}

function Signal({
  icon,
  label,
  value,
}: {
  icon: ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="bg-card text-card-foreground rounded-lg border p-4">
      <div className="text-muted-foreground flex items-center gap-2 text-xs font-medium tracking-normal uppercase">
        {icon}
        {label}
      </div>
      <div className="mt-2 text-sm leading-6">{value}</div>
    </div>
  );
}

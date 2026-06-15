import {
  ArrowUpRightIcon,
  CheckCircle2Icon,
  DatabaseIcon,
  GitBranchIcon,
  GithubIcon,
  LockKeyholeIcon,
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
  "Research",
  "Evidence Extraction",
  "Alternative Comparison",
  "Scorecard",
  "Consistency Check",
  "Report Assembly",
];

export function TechnologyEvaluationDemo({
  report,
}: {
  report: EvaluationReportArtifact;
}) {
  return (
    <main className="bg-background text-foreground min-h-screen">
      <section className="border-b">
        <div className="mx-auto grid min-h-[88vh] w-full max-w-7xl gap-8 px-5 py-8 md:px-8 lg:grid-cols-[minmax(0,0.92fr)_minmax(420px,1.08fr)] lg:items-center lg:py-10">
          <div className="flex max-w-3xl flex-col gap-6">
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant="secondary">Static public demo</Badge>
              <Badge variant="outline">No backend required</Badge>
            </div>
            <div className="space-y-4">
              <h1 className="max-w-3xl text-4xl leading-tight font-semibold tracking-normal md:text-5xl">
                Technology Research & Evaluation Agent
              </h1>
              <p className="text-muted-foreground max-w-2xl text-lg leading-8">
                A DeerFlow-based agent that turns technology research into a
                structured evaluation report with evidence, alternatives, risks,
                and a weighted scorecard.
              </p>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              <Signal
                icon={<GitBranchIcon className="size-4" />}
                label="Example input"
                value="Evaluate LangGraph for long-running AI agent workflows"
              />
              <Signal
                icon={<DatabaseIcon className="size-4" />}
                label="Replay fixture"
                value="Prebuilt EvaluationReport JSON rendered by the product viewer"
              />
            </div>

            <div className="flex flex-wrap gap-3">
              <a className={cn(buttonVariants({ size: "lg" }))} href="#report">
                View report
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
                GitHub
                <ArrowUpRightIcon className="size-4" />
              </a>
            </div>
          </div>

          <Card className="rounded-lg shadow-none">
            <CardContent className="p-5">
              <div className="mb-4 flex items-center justify-between gap-3">
                <div>
                  <h2 className="text-base font-semibold">Workflow stages</h2>
                  <p className="text-muted-foreground mt-1 text-sm">
                    The live backend can execute this pipeline; this public demo
                    replays the generated artifact.
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
            label="Productized artifact"
            value="EvaluationReport JSON is rendered as a dedicated assessment view."
          />
          <Signal
            icon={<LockKeyholeIcon className="size-4" />}
            label="Cost protection"
            value="This demo does not expose model keys or trigger live agent runs."
          />
          <Signal
            icon={<ServerIcon className="size-4" />}
            label="Deployment proof"
            value="Live backend deployment remains supported via Docker and ECS."
          />
        </div>
      </section>

      <section id="report" className="bg-muted/20">
        <div className="mx-auto w-full max-w-7xl px-0 py-6 md:px-8 md:py-8">
          <div className="px-5 md:px-0">
            <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
              <div>
                <h2 className="text-2xl font-semibold tracking-normal">
                  Replay EvaluationReport
                </h2>
                <p className="text-muted-foreground mt-2 max-w-3xl">
                  Live backend deployment is supported via Docker/ECS, but this
                  public demo uses a replay fixture to avoid exposing model keys
                  and runtime costs.
                </p>
              </div>
              <Badge variant="outline">LangGraph example</Badge>
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

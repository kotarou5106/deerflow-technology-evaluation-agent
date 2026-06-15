import { ExternalLinkIcon } from "lucide-react";
import type { ReactNode } from "react";

import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

const NO_DATA = "No data provided";

type JsonObject = Record<string, unknown>;

export type EvaluationReportArtifact = JsonObject & {
  target_technology?: unknown;
  evaluation_context?: unknown;
  verdict?: unknown;
  final_score?: unknown;
  criteria?: unknown;
  evidence_items?: unknown;
  alternatives?: unknown;
  risk_register?: unknown;
  open_questions?: unknown;
  references?: unknown;
  executive_summary?: unknown;
  technology_overview?: unknown;
};

export function parseEvaluationReportArtifact({
  content,
  filepath,
}: {
  content: string;
  filepath: string;
}): EvaluationReportArtifact | null {
  if (!filepath.toLowerCase().endsWith(".json")) {
    return null;
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(content);
  } catch {
    return null;
  }

  if (!isObject(parsed)) {
    return null;
  }

  const hasCoreFields =
    "target_technology" in parsed &&
    "verdict" in parsed &&
    "final_score" in parsed;
  const hasEvaluationBody =
    "criteria" in parsed ||
    "evidence_items" in parsed ||
    "risk_register" in parsed;

  return hasCoreFields && hasEvaluationBody ? parsed : null;
}

export function EvaluationReportViewer({
  className,
  report,
}: {
  className?: string;
  report: EvaluationReportArtifact;
}) {
  const executiveSummary = objectValue(report.executive_summary);
  const technologyOverview = objectValue(report.technology_overview);

  return (
    <div
      className={cn(
        "bg-background size-full overflow-auto px-5 py-4 text-sm",
        className,
      )}
    >
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-5 pb-8">
        <Card className="gap-4 rounded-lg py-5 shadow-none">
          <CardHeader className="gap-3 px-5">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div className="min-w-0">
                <CardTitle className="text-xl leading-tight">
                  {textValue(report.target_technology)}
                </CardTitle>
                <p className="text-muted-foreground mt-2 max-w-4xl">
                  {textValue(report.evaluation_context)}
                </p>
              </div>
              <div className="flex shrink-0 flex-wrap items-center gap-2">
                <Badge variant="secondary" className="max-w-72 text-wrap">
                  {textValue(report.verdict)}
                </Badge>
                <Badge variant="outline">
                  Score {textValue(report.final_score)}
                </Badge>
              </div>
            </div>
          </CardHeader>
        </Card>

        <Section title="Executive Summary">
          <Field
            label="One sentence verdict"
            value={executiveSummary?.one_sentence_verdict}
          />
          <FieldList
            label="Key reasons"
            value={executiveSummary?.key_reasons}
          />
          <FieldList
            label="Major risks"
            value={executiveSummary?.major_risks}
          />
          <Field label="Best fit" value={executiveSummary?.best_fit} />
        </Section>

        <Section title="Technology Overview">
          <Field label="Description" value={technologyOverview?.description} />
          <Field
            label="Problem addressed"
            value={technologyOverview?.problem_addressed}
          />
          <FieldList
            label="Primary use cases"
            value={technologyOverview?.primary_use_cases}
          />
          <FieldList
            label="Key features"
            value={technologyOverview?.key_features}
          />
          <FieldList
            label="Target users"
            value={technologyOverview?.target_users}
          />
        </Section>

        <Section title="Evaluation Scorecard">
          <DataTable
            columns={["name", "score", "weight", "rationale", "evidence_ids"]}
            rows={arrayValue(report.criteria)}
          />
        </Section>

        <Section title="Evidence Matrix">
          <DataTable
            columns={[
              "id",
              "claim",
              "evidence_summary",
              "source_type",
              "trust_level",
              "support_status",
              "confidence",
              "source_url",
            ]}
            linkColumns={["source_url"]}
            rows={arrayValue(report.evidence_items)}
          />
        </Section>

        <Section title="Alternative Comparison">
          <AlternativeList alternatives={arrayValue(report.alternatives)} />
        </Section>

        <Section title="Risk Register">
          <DataTable
            columns={[
              "name",
              "severity",
              "likelihood",
              "mitigation",
              "evidence_ids",
            ]}
            rows={arrayValue(report.risk_register)}
          />
        </Section>

        <Section title="Open Questions">
          <DataTable
            columns={["question", "why_it_matters", "suggested_validation"]}
            rows={arrayValue(report.open_questions)}
          />
        </Section>

        <Section title="References">
          <DataTable
            columns={["title", "url", "source_type", "publisher", "notes"]}
            linkColumns={["url"]}
            rows={arrayValue(report.references)}
          />
        </Section>
      </div>
    </div>
  );
}

function Section({ children, title }: { children: ReactNode; title: string }) {
  return (
    <section className="flex flex-col gap-3">
      <h2 className="text-base font-semibold tracking-normal">{title}</h2>
      <div className="bg-card text-card-foreground rounded-lg border p-4">
        {children}
      </div>
    </section>
  );
}

function Field({ label, value }: { label: string; value: unknown }) {
  return (
    <div className="grid gap-1 border-b py-3 first:pt-0 last:border-b-0 last:pb-0 md:grid-cols-[180px_minmax(0,1fr)] md:gap-4">
      <div className="text-muted-foreground font-medium">{label}</div>
      <div className="min-w-0 break-words whitespace-pre-wrap">
        {textValue(value)}
      </div>
    </div>
  );
}

function FieldList({ label, value }: { label: string; value: unknown }) {
  const items = stringListValue(value);
  return (
    <div className="grid gap-1 border-b py-3 first:pt-0 last:border-b-0 last:pb-0 md:grid-cols-[180px_minmax(0,1fr)] md:gap-4">
      <div className="text-muted-foreground font-medium">{label}</div>
      {items.length === 0 ? (
        <div className="text-muted-foreground">{NO_DATA}</div>
      ) : (
        <ul className="min-w-0 list-disc space-y-1 pl-5">
          {items.map((item, index) => (
            <li key={`${item}-${index}`} className="break-words">
              {item}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function DataTable({
  columns,
  linkColumns = [],
  rows,
}: {
  columns: string[];
  linkColumns?: string[];
  rows: unknown[];
}) {
  if (rows.length === 0) {
    return <EmptyState />;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[760px] border-collapse text-left text-sm">
        <thead>
          <tr className="bg-muted/40 border-b">
            {columns.map((column) => (
              <th
                key={column}
                className="text-muted-foreground px-3 py-2 font-medium"
              >
                {formatLabel(column)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rowIndex) => {
            const object = objectValue(row);
            return (
              <tr key={rowIndex} className="border-b last:border-b-0">
                {columns.map((column) => (
                  <td
                    key={column}
                    className="max-w-[320px] px-3 py-3 align-top"
                  >
                    {linkColumns.includes(column) ? (
                      <UrlValue value={object?.[column]} />
                    ) : (
                      <span className="break-words whitespace-pre-wrap">
                        {cellValue(object?.[column])}
                      </span>
                    )}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function AlternativeList({ alternatives }: { alternatives: unknown[] }) {
  if (alternatives.length === 0) {
    return <EmptyState />;
  }

  return (
    <div className="grid gap-3 md:grid-cols-2">
      {alternatives.map((alternative, index) => {
        const item = objectValue(alternative);
        return (
          <article key={index} className="rounded-lg border p-4">
            <div className="flex flex-wrap items-center gap-2">
              <h3 className="font-semibold">{textValue(item?.name)}</h3>
              <Badge variant="outline">{textValue(item?.category)}</Badge>
            </div>
            <div className="mt-3 space-y-3">
              <CompactList label="Strengths" value={item?.strengths} />
              <CompactList label="Weaknesses" value={item?.weaknesses} />
              <CompactList
                label="Best fit use cases"
                value={item?.best_fit_use_cases}
              />
              <CompactList label="Risks" value={item?.risks} />
            </div>
          </article>
        );
      })}
    </div>
  );
}

function CompactList({ label, value }: { label: string; value: unknown }) {
  const items = stringListValue(value);
  return (
    <div>
      <div className="text-muted-foreground text-xs font-medium tracking-normal uppercase">
        {label}
      </div>
      {items.length === 0 ? (
        <div className="text-muted-foreground mt-1">{NO_DATA}</div>
      ) : (
        <ul className="mt-1 list-disc space-y-1 pl-5">
          {items.map((item, index) => (
            <li key={`${item}-${index}`} className="break-words">
              {item}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function UrlValue({ value }: { value: unknown }) {
  const text = typeof value === "string" ? value.trim() : "";
  if (!text) {
    return <span className="text-muted-foreground">{NO_DATA}</span>;
  }

  try {
    const url = new URL(text);
    if (url.protocol !== "http:" && url.protocol !== "https:") {
      throw new Error("Unsupported URL protocol");
    }
  } catch {
    return <span className="break-words whitespace-pre-wrap">{text}</span>;
  }

  return (
    <a
      className="text-primary inline-flex max-w-full items-center gap-1 underline-offset-4 hover:underline"
      href={text}
      rel="noopener noreferrer"
      target="_blank"
    >
      <span className="truncate">{text}</span>
      <ExternalLinkIcon className="size-3 shrink-0" />
    </a>
  );
}

function EmptyState() {
  return (
    <div className="text-muted-foreground rounded-md border border-dashed px-4 py-6 text-center">
      {NO_DATA}
    </div>
  );
}

function isObject(value: unknown): value is JsonObject {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function objectValue(value: unknown) {
  return isObject(value) ? value : undefined;
}

function arrayValue(value: unknown) {
  return Array.isArray(value) ? value : [];
}

function stringListValue(value: unknown) {
  if (!Array.isArray(value)) {
    return [];
  }
  return value
    .map((item) => textValue(item))
    .filter((item) => item !== NO_DATA);
}

function textValue(value: unknown): string {
  if (typeof value === "string") {
    const trimmed = value.trim();
    return trimmed || NO_DATA;
  }
  if (typeof value === "number") {
    return Number.isFinite(value) ? String(value) : NO_DATA;
  }
  if (typeof value === "boolean") {
    return value ? "Yes" : "No";
  }
  return NO_DATA;
}

function cellValue(value: unknown): string {
  if (Array.isArray(value)) {
    const items = stringListValue(value);
    return items.length > 0 ? items.join(", ") : NO_DATA;
  }
  return textValue(value);
}

function formatLabel(value: string) {
  return value.replaceAll("_", " ");
}

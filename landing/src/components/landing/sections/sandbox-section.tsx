"use client";

import { AnimatedSpan, Terminal, TypingAnimation } from "@/components/ui/terminal";

import { Section } from "../section";

export function SandboxSection({ className }: { className?: string }) {
  return (
    <Section className={className} title="工程化部署" subtitle="从 Agent 工作流到公网 HTTPS Demo 的完整交付">
      <div className="mt-8 flex w-full max-w-6xl flex-col items-center gap-12 px-4 lg:flex-row lg:gap-16">
        <div className="w-full flex-1">
          <Terminal className="h-[360px] w-full">
            <TypingAnimation>$ pnpm build</TypingAnimation>
            <AnimatedSpan className="text-green-500">✔ Exported static site to out/</AnimatedSpan>
            <TypingAnimation>$ find out -name index.html</TypingAnimation>
            <AnimatedSpan className="text-zinc-400">out/index.html</AnimatedSpan>
            <TypingAnimation>$ curl -I https://evaluation.kotarou.quest</TypingAnimation>
            <AnimatedSpan className="text-green-500">HTTP/1.1 200 OK</AnimatedSpan>
          </Terminal>
        </div>
        <div className="w-full flex-1 space-y-6">
          <div className="space-y-4">
            <p className="text-sm font-medium tracking-wider text-sky-400 uppercase">Public delivery</p>
            <h2 className="text-4xl font-bold tracking-tight lg:text-5xl">Docker + nginx + HTTPS</h2>
          </div>
          <p className="text-lg text-zinc-400">
            展示站通过静态构建独立交付，不依赖工作区运行时；完整技术评估能力由独立的在线工作区承载。
          </p>
          <div className="flex flex-wrap gap-3 pt-4">
            {["Static Export", "Independent Hosting", "HTTPS", "Edge CDN", "Zero Runtime", "Public Demo"].map((tag) => (
              <span key={tag} className="rounded-full border border-zinc-800 bg-zinc-900 px-4 py-2 text-sm text-zinc-300">
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>
    </Section>
  );
}

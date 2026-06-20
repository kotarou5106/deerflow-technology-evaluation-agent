"use client";

import { ChevronRightIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
import { FlickeringGrid } from "@/components/ui/flickering-grid";
import Galaxy from "@/components/ui/galaxy";
import { cn } from "@/lib/utils";

const LIVE_URL = "https://workspace.evaluation.kotarou.quest";

export function Hero({ className }: { className?: string }) {
  return (
    <section className={cn("relative flex size-full flex-col items-center justify-center", className)}>
      <div className="absolute inset-0 z-0 bg-black/40">
        <Galaxy
          mouseRepulsion={false}
          starSpeed={0.2}
          density={0.6}
          glowIntensity={0.35}
          twinkleIntensity={0.3}
          speed={0.5}
        />
      </div>
      <FlickeringGrid
        className="absolute inset-0 z-0 translate-y-8 mask-radial-from-60% mask-radial-to-95% opacity-45"
        squareSize={4}
        gridGap={4}
        color="white"
        maxOpacity={0.18}
        flickerChance={0.25}
      />
      <div className="container-md relative z-10 mx-auto flex h-screen flex-col items-center justify-center px-4">
        <h1 className="bg-gradient-to-r from-white via-sky-100 to-emerald-200 bg-clip-text text-center text-4xl font-bold text-transparent md:text-6xl">
          技术评估 Agent
        </h1>
        <p className="mt-5 max-w-2xl text-center text-base leading-7 text-white/75 md:text-lg md:leading-8">
          输入一个技术主题、方案或平台，Agent 会围绕证据收集、替代方案比较、评分矩阵、风险登记和结构化报告，系统判断它是否值得采用、适用于什么条件，以及下一步应如何推进。
        </p>
        <div className="mt-8 flex items-center">
          <Button className="size-lg scale-108" size="lg" asChild>
            <a href={LIVE_URL}>
              <span className="text-md">开始技术评估</span>
              <ChevronRightIcon className="size-4" />
            </a>
          </Button>
        </div>
      </div>
    </section>
  );
}

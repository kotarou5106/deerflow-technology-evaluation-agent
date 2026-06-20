"use client";

import {
  Check,
  ChevronRight,
  FileCode2,
  FileText,
  FolderOpen,
  Pause,
  Play,
  RotateCcw,
  Sparkles,
} from "lucide-react";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { useEffect, useMemo, useState } from "react";

import { cn } from "@/lib/utils";

import {
  EVALUATION_TOPIC,
  EVALUATION_WORKFLOW_STEPS,
  getWorkflowSnapshot,
} from "./evaluation-workflow-model";

type PlaybackState = "idle" | "playing" | "paused" | "complete";

export function EvaluationWorkflowDemo() {
  const [activeIndex, setActiveIndex] = useState(0);
  const [playback, setPlayback] = useState<PlaybackState>("idle");
  const reduceMotion = useReducedMotion();
  const snapshot = useMemo(
    () => getWorkflowSnapshot(activeIndex),
    [activeIndex],
  );

  useEffect(() => {
    if (playback !== "playing") return;

    const timer = window.setTimeout(
      () => {
        if (activeIndex >= EVALUATION_WORKFLOW_STEPS.length - 1) {
          setActiveIndex(EVALUATION_WORKFLOW_STEPS.length);
          setPlayback("complete");
          return;
        }
        setActiveIndex((current) => current + 1);
      },
      reduceMotion ? 250 : 1150,
    );

    return () => window.clearTimeout(timer);
  }, [activeIndex, playback, reduceMotion]);

  const start = () => {
    setActiveIndex(0);
    setPlayback("playing");
  };

  const togglePlayback = () => {
    if (playback === "idle" || playback === "complete") {
      start();
    } else {
      setPlayback(playback === "playing" ? "paused" : "playing");
    }
  };

  const progress = Math.round(
    (snapshot.completedSteps.length / EVALUATION_WORKFLOW_STEPS.length) * 100,
  );
  const isStarted = playback !== "idle";

  return (
    <div className="relative mx-auto w-full max-w-6xl px-4 md:px-8">
      <div className="overflow-hidden rounded-2xl border border-white/10 bg-zinc-950 shadow-2xl shadow-black/30">
        <div className="flex flex-col gap-3 border-b border-white/10 bg-zinc-900/70 px-4 py-3 sm:flex-row sm:items-center sm:justify-between sm:px-5">
          <div className="flex items-center gap-3">
            <div className="flex gap-1.5" aria-hidden="true">
              <span className="size-2.5 rounded-full bg-red-400/70" />
              <span className="size-2.5 rounded-full bg-amber-400/70" />
              <span className="size-2.5 rounded-full bg-emerald-400/70" />
            </div>
            <span className="font-mono text-xs text-zinc-400">
              evaluation-agent / workflow-run
            </span>
          </div>
          <div className="flex items-center gap-3">
            <span className="font-mono text-xs text-zinc-500">
              {playback === "complete"
                ? "9 / 9 · COMPLETE"
                : `${snapshot.completedSteps.length} / 9 · ${playback.toUpperCase()}`}
            </span>
            <button
              type="button"
              onClick={togglePlayback}
              className="inline-flex h-8 items-center gap-2 rounded-md border border-white/10 bg-white/5 px-3 text-xs font-medium text-zinc-200 transition hover:border-sky-400/40 hover:bg-sky-400/10 focus-visible:ring-2 focus-visible:ring-sky-400 focus-visible:outline-none"
              aria-label={
                playback === "playing"
                  ? "暂停评估演示"
                  : playback === "complete"
                    ? "重新播放评估演示"
                    : "播放评估演示"
              }
            >
              {playback === "playing" ? (
                <Pause className="size-3.5" fill="currentColor" />
              ) : playback === "complete" ? (
                <RotateCcw className="size-3.5" />
              ) : (
                <Play className="size-3.5" fill="currentColor" />
              )}
              {playback === "playing"
                ? "暂停"
                : playback === "complete"
                  ? "重新播放"
                  : "播放演示"}
            </button>
          </div>
        </div>

        <div className="grid min-h-[620px] lg:grid-cols-[0.82fr_1.18fr]">
          <div className="border-b border-white/10 bg-black/30 p-5 lg:border-r lg:border-b-0 lg:p-6">
            <div className="mb-5 flex items-center gap-2 font-mono text-xs text-zinc-500">
              <FolderOpen className="size-4 text-sky-400" />
              <span>evaluation-agent/</span>
            </div>
            <div
              className="min-h-[360px] space-y-2"
              aria-label="评估产物文件树"
            >
              <AnimatePresence initial={false}>
                {(isStarted ? snapshot.visibleFiles : []).map((file, index) => {
                  const isActive =
                    playback !== "complete" && index === activeIndex;
                  return (
                    <motion.div
                      key={file.name}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      className={cn(
                        "flex items-center gap-3 rounded-md border px-3 py-2.5 font-mono text-sm",
                        isActive
                          ? "border-sky-400/30 bg-sky-400/10 text-sky-100"
                          : file.kind === "artifact"
                            ? "border-emerald-400/20 bg-emerald-400/8 text-emerald-300"
                            : "border-transparent text-zinc-400",
                      )}
                    >
                      {file.name.endsWith(".json") ? (
                        <FileCode2 className="size-4 shrink-0" />
                      ) : (
                        <FileText className="size-4 shrink-0" />
                      )}
                      <span className="truncate">{file.name}</span>
                      {isActive ? (
                        <span className="ml-auto size-1.5 animate-pulse rounded-full bg-sky-300" />
                      ) : (
                        <Check className="ml-auto size-3.5 text-emerald-400" />
                      )}
                    </motion.div>
                  );
                })}
              </AnimatePresence>
              {!isStarted && (
                <div className="flex min-h-[280px] flex-col items-center justify-center gap-3 text-center text-zinc-600">
                  <FolderOpen className="size-8" strokeWidth={1.25} />
                  <p className="max-w-48 text-sm leading-6">
                    运行后，工作文件与报告产物将在这里逐步生成
                  </p>
                </div>
              )}
            </div>
            <div className="mt-5 border-t border-white/10 pt-4">
              <div className="mb-2 flex items-center justify-between font-mono text-[11px] text-zinc-500">
                <span>RUN PROGRESS</span>
                <span>{progress}%</span>
              </div>
              <div className="h-1 overflow-hidden rounded-full bg-zinc-800">
                <motion.div
                  className="h-full rounded-full bg-sky-400"
                  animate={{ width: `${progress}%` }}
                  transition={{ duration: reduceMotion ? 0 : 0.35 }}
                />
              </div>
            </div>
          </div>

          <div className="flex min-w-0 flex-col bg-zinc-950">
            <div className="flex items-center gap-2 border-b border-white/10 px-5 py-4">
              <span
                className={cn(
                  "size-2 rounded-full",
                  playback === "playing"
                    ? "animate-pulse bg-emerald-400"
                    : "bg-zinc-600",
                )}
              />
              <span className="text-sm font-medium text-zinc-300">
                Evaluation Agent
              </span>
              <span className="ml-auto font-mono text-[11px] text-zinc-600">
                deterministic demo
              </span>
            </div>

            <div className="flex-1 space-y-5 overflow-hidden p-4 sm:p-6">
              <div className="ml-auto max-w-[92%] rounded-xl rounded-tr-sm border border-sky-400/20 bg-sky-500/10 px-4 py-3">
                <div className="mb-1.5 font-mono text-[10px] tracking-wider text-sky-400 uppercase">
                  输入技术评估主题
                </div>
                <p className="text-sm leading-6 text-zinc-100 sm:text-[15px]">
                  {EVALUATION_TOPIC}
                </p>
              </div>

              {!isStarted ? (
                <button
                  type="button"
                  onClick={start}
                  className="group flex w-full items-center justify-center gap-3 rounded-xl border border-dashed border-white/15 bg-white/3 py-8 text-zinc-300 transition hover:border-sky-400/40 hover:bg-sky-400/5 focus-visible:ring-2 focus-visible:ring-sky-400 focus-visible:outline-none"
                >
                  <span className="flex size-11 items-center justify-center rounded-full bg-white/8 transition group-hover:bg-sky-400/15">
                    <Play className="ml-0.5 size-5" fill="currentColor" />
                  </span>
                  <span className="text-left">
                    <span className="block text-sm font-medium">
                      Click to play
                    </span>
                    <span className="mt-1 block text-xs text-zinc-500">
                      查看 Agent 如何完成评估链路
                    </span>
                  </span>
                </button>
              ) : (
                <div className="space-y-2" aria-live="polite">
                  {EVALUATION_WORKFLOW_STEPS.map((step, index) => {
                    const isDone = index < activeIndex;
                    const isActive =
                      index === activeIndex && playback !== "complete";
                    if (!isDone && !isActive) return null;

                    return (
                      <motion.div
                        key={step.label}
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        className={cn(
                          "flex gap-3 rounded-lg px-3 py-2.5",
                          isActive && "bg-white/4",
                        )}
                      >
                        <span
                          className={cn(
                            "mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-full border",
                            isDone
                              ? "border-emerald-400/30 bg-emerald-400/10 text-emerald-400"
                              : "border-sky-400/40 bg-sky-400/10 text-sky-300",
                          )}
                        >
                          {isDone ? (
                            <Check className="size-3" />
                          ) : (
                            <ChevronRight className="size-3 animate-pulse" />
                          )}
                        </span>
                        <div className="min-w-0">
                          <div
                            className={cn(
                              "text-sm font-medium",
                              isDone ? "text-zinc-400" : "text-zinc-100",
                            )}
                          >
                            {step.label}
                          </div>
                          {isActive && (
                            <p className="mt-1 text-xs leading-5 text-zinc-500">
                              {step.detail}
                            </p>
                          )}
                        </div>
                        {isActive && (
                          <span className="ml-auto font-mono text-[10px] text-sky-400">
                            RUNNING
                          </span>
                        )}
                      </motion.div>
                    );
                  })}
                </div>
              )}

              <AnimatePresence>
                {playback === "complete" && (
                  <motion.div
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="rounded-xl border border-emerald-400/20 bg-emerald-400/5 p-4"
                  >
                    <div className="mb-3 flex items-center gap-2 text-sm font-medium text-emerald-300">
                      <Sparkles className="size-4" />
                      评估完成 · 建议有条件采用
                    </div>
                    <div className="grid gap-2 sm:grid-cols-2">
                      {["EvaluationReport.json", "EvaluationReport.md"].map(
                        (file) => (
                          <div
                            key={file}
                            className="flex items-center gap-2 rounded-md border border-white/8 bg-black/20 px-3 py-2 font-mono text-xs text-zinc-300"
                          >
                            {file.endsWith("json") ? (
                              <FileCode2 className="size-3.5 text-sky-400" />
                            ) : (
                              <FileText className="size-3.5 text-emerald-400" />
                            )}
                            {file}
                          </div>
                        ),
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

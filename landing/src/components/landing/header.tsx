import Link from "next/link";

import { cn } from "@/lib/utils";

const LIVE_URL = "https://workspace.evaluation.kotarou.quest";

export function Header({ className }: { className?: string }) {
  return (
    <header
      className={cn(
        "container-md fixed top-0 right-0 left-0 z-20 mx-auto flex h-16 items-center justify-between backdrop-blur-xs",
        className,
      )}
    >
      <Link href="/" aria-label="技术评估 Agent 首页">
        <h1 className="font-serif text-xl">技术评估 Agent</h1>
      </Link>
      <nav className="ml-auto flex items-center text-sm font-medium" aria-label="主导航">
        <a
          href={LIVE_URL}
          className="text-secondary-foreground hover:text-foreground transition-colors"
        >
          开始评估
        </a>
      </nav>
      <hr className="from-border/0 via-border/70 to-border/0 absolute top-16 right-0 left-0 z-10 m-0 h-px w-full border-none bg-linear-to-r" />
    </header>
  );
}

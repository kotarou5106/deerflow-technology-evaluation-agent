import { AuroraText } from "@/components/ui/aurora-text";
import { Button } from "@/components/ui/button";

import { Section } from "../section";

const LIVE_URL = "https://workspace.evaluation.kotarou.quest";

export function CommunitySection() {
  return (
    <Section
      title={<AuroraText colors={["#60A5FA", "#F0ABFC", "#34D399"]}>开始一次技术评估</AuroraText>}
      subtitle="输入一个技术、方案、平台、论文或开源项目，让 Agent 生成一份可复核的评估报告。"
    >
      <div className="flex justify-center">
        <Button className="text-xl" size="lg" asChild>
          <a href={LIVE_URL}>开始技术评估</a>
        </Button>
      </div>
    </Section>
  );
}

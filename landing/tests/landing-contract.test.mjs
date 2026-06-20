import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const read = (path) => readFileSync(new URL(`../${path}`, import.meta.url), "utf8");

test("the extracted workflow keeps all nine evaluation phases and both reports", () => {
  const model = read("src/components/landing/evaluation-workflow-model.ts");
  const demo = read("src/components/landing/evaluation-workflow-demo.tsx");

  assert.equal((model.match(/label: "/g) ?? []).length, 9);
  assert.match(model, /EvaluationReport\.json/);
  assert.match(model, /EvaluationReport\.md/);
  assert.match(demo, /暂停评估演示/);
  assert.match(demo, /重新播放评估演示/);
});

test("all three landing CTAs use the workspace origin", () => {
  const source = [
    read("src/components/landing/header.tsx"),
    read("src/components/landing/hero.tsx"),
    read("src/components/landing/sections/community-section.tsx"),
  ].join("\n");

  assert.equal(
    (source.match(/https:\/\/workspace\.evaluation\.kotarou\.quest/g) ?? [])
      .length,
    3,
  );
  assert.doesNotMatch(source, /evaluation-live\.kotarou\.quest/);
  assert.doesNotMatch(source, /href=["'{/]*\/workspace/);
});

test("landing sources contain no full-stack runtime dependencies or retired brands", () => {
  const source = [
    read("src/app/layout.tsx"),
    read("src/app/page.tsx"),
    read("src/components/landing/header.tsx"),
    read("src/components/landing/hero.tsx"),
    read("src/components/landing/footer.tsx"),
  ].join("\n");

  assert.doesNotMatch(source, /next\/headers|cookies\(|headers\(|process\.env|NEXT_PUBLIC_/);
  assert.doesNotMatch(source, /DeerFlow|Portfolio|GitHub|Star on GitHub|Join the Community/);
});

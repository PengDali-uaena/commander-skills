#!/usr/bin/env node
// 一次性归一：把 BODY.md 里某一侧专属的写法换成立中立说法。
import { readFileSync, writeFileSync, readdirSync, existsSync } from "node:fs";
import { join } from "node:path";
import { homedir } from "node:os";

const SRC = join(homedir(), ".agents", "skill-src");
const SUBS = [
  [/再 Read 不超过/g, "再读不超过"],
  [/\bRead\b/g, "读"],
  [/DSH 的 read/g, "read 工具"],
  [/todo_write/g, "步骤清单"],
  [/@([a-z][a-z0-9-]{2,})\b/g, "$1"],
];

let n = 0;
for (const name of readdirSync(SRC)) {
  const p = join(SRC, name, "BODY.md");
  if (!existsSync(p)) continue;
  const before = readFileSync(p, "utf8");
  let after = before;
  for (const [re, to] of SUBS) after = after.replace(re, to);
  if (after !== before) { writeFileSync(p, after); n++; }
}
console.log(`normalized ${n} BODY.md`);

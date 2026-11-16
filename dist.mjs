#!/usr/bin/env node
// 把 <本仓>/<name>/BODY.md + META.json 分发成 Pi / DSH / Cursor 三侧的 SKILL.md。
// 用法：
//   node dist.mjs           写入三侧（目标目录不存在就跳过）
//   node dist.mjs --check   只检查，生成物与主体不一致就非 0 退出
//   PI_SKILLS_DIR / DSH_SKILLS_DIR / CURSOR_SKILLS_DIR 覆盖默认的输出目录。
// 三侧目录里只有 SKILL.md 是生成物，其余附件（脚本、references/）由各侧自己维护。

import { readFileSync, writeFileSync, readdirSync, existsSync, statSync } from "node:fs";
import { join } from "node:path";
import { homedir } from "node:os";

const SRC = process.env.SKILL_SRC || join(homedir(), ".agents", "skill-src");
const home = homedir();
const side = (envName, ...fallback) => {
  const dir = process.env[envName] || join(home, ...fallback);
  const shown = dir.startsWith(home) ? "~" + dir.slice(home.length) : dir;
  return { dir, root: shown.replace(/\/?$/, "/") };
};
const SIDES = {
  pi: side("PI_SKILLS_DIR", ".pi", "agent", "skills"),
  dsh: side("DSH_SKILLS_DIR", ".dsh", "skills"),
  cursor: side("CURSOR_SKILLS_DIR", ".cursor", "skills"),
};
const MARK = "<!-- GENERATED：本文件由 ~/.agents/skill-src/dist.mjs 生成，改 BODY.md 后重跑；手改会被覆盖 -->";
const check = process.argv.includes("--check");

let written = 0;
let drifted = 0;
let skipped = 0;

for (const name of readdirSync(SRC)) {
  const dir = join(SRC, name);
  if (!statSync(dir).isDirectory()) continue;
  const bodyPath = join(dir, "BODY.md");
  const metaPath = join(dir, "META.json");
  if (!existsSync(bodyPath) || !existsSync(metaPath)) continue;

  const body = readFileSync(bodyPath, "utf8").replace(/\s+$/, "");
  const meta = JSON.parse(readFileSync(metaPath, "utf8"));

  for (const [side, { dir: outRoot, root }] of Object.entries(SIDES)) {
    const front = meta[side]?.frontmatter;
    const outPath = join(outRoot, name, "SKILL.md");
    if (!front) continue;
    if (!existsSync(join(outRoot, name))) { skipped++; continue; }

    const rendered = `---\n${front}\n---\n\n${MARK}\n\n${body
      .split("{{SKILL_DIR}}")
      .join(root + name + "/")
      .split("{{SKILLS_ROOT}}")
      .join(root)}\n`;

    const current = existsSync(outPath) ? readFileSync(outPath, "utf8") : null;
    if (current === rendered) continue;

    if (check) {
      console.error(`drift: ${outPath}`);
      drifted++;
    } else {
      writeFileSync(outPath, rendered);
      written++;
    }
  }
}

if (check) {
  if (drifted) { console.error(`\n${drifted} 个生成物与 BODY.md 不一致`); process.exit(1); }
  console.log("ok: 生成物与主体一致");
} else {
  console.log(`wrote ${written} file(s), skipped ${skipped} missing side dir(s)`);
}

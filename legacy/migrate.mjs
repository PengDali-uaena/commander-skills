#!/usr/bin/env node
// 一次性迁移：把 Pi / Cursor 两侧同名 skill 的 frontmatter 收进 META.json，
// 正文以 Cursor 版为基线落到 BODY.md（之后人工合并 Pi 独有内容）。
import { readFileSync, writeFileSync, readdirSync, mkdirSync, existsSync } from "node:fs";
import { join } from "node:path";
import { homedir } from "node:os";

const PI = join(homedir(), ".pi", "agent", "skills");
const CU = join(homedir(), ".cursor", "skills");
const SRC = join(homedir(), ".agents", "skill-src");

const split = (txt) => {
  const m = txt.match(/^---\n([\s\S]*?)\n---\n/);
  if (!m) return { frontmatter: null, body: txt };
  return { frontmatter: m[1], body: txt.slice(m[0].length).replace(/^\n+/, "") };
};
const norm = (body, name) =>
  body
    .replace(/~\/\.cursor\/skills\//g, "{{SKILLS_ROOT}}")
    .replace(/~\/\.pi\/agent\/skills\//g, "{{SKILLS_ROOT}}")
    .replace(new RegExp(`\\{\\{SKILLS_ROOT\\}\\}${name}/`, "g"), "{{SKILL_DIR}}")
    .replace(/\s+$/, "");

const names = readdirSync(PI).filter((n) => existsSync(join(CU, n, "SKILL.md")) && existsSync(join(PI, n, "SKILL.md")));
const made = [];
for (const name of names) {
  const pi = split(readFileSync(join(PI, name, "SKILL.md"), "utf8"));
  const cu = split(readFileSync(join(CU, name, "SKILL.md"), "utf8"));
  const dir = join(SRC, name);
  if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
  writeFileSync(join(dir, "META.json"), JSON.stringify({ pi: { frontmatter: pi.frontmatter }, cursor: { frontmatter: cu.frontmatter } }, null, 2) + "\n");
  writeFileSync(join(dir, "BODY.md"), norm(cu.body, name) + "\n");
  made.push(name);
}
console.log(`migrated ${made.length}: ${made.join(" ")}`);

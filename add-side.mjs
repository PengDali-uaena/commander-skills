#!/usr/bin/env node
// 一次性：把某一侧现有 SKILL.md 的 frontmatter 补进各 META.json。
// 用法：node add-side.mjs dsh ~/.dsh/skills
import { readFileSync, writeFileSync, readdirSync, existsSync } from "node:fs";
import { join } from "node:path";
import { homedir } from "node:os";

const [side, dirArg] = process.argv.slice(2);
if (!side || !dirArg) { console.error("usage: node add-side.mjs <side> <skills-dir>"); process.exit(1); }
const root = dirArg.replace(/^~/, homedir());
const SRC = join(homedir(), ".agents", "skill-src");

let added = 0;
let missing = [];
for (const name of readdirSync(SRC)) {
  const metaPath = join(SRC, name, "META.json");
  if (!existsSync(metaPath)) continue;
  const src = join(root, name, "SKILL.md");
  const meta = JSON.parse(readFileSync(metaPath, "utf8"));
  if (!existsSync(src)) { missing.push(name); continue; }
  const m = readFileSync(src, "utf8").match(/^---\n([\s\S]*?)\n---\n/);
  if (!m) { console.error(`no frontmatter: ${src}`); continue; }
  meta[side] = { frontmatter: m[1] };
  writeFileSync(metaPath, JSON.stringify(meta, null, 2) + "\n");
  added++;
}
console.log(`${side}: +${added} frontmatter, ${missing.length} skill(s) absent on that side${missing.length ? ": " + missing.join(" ") : ""}`);

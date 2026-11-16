#!/usr/bin/env node
// 把 <本仓>/<name>/BODY[.<lang>].md + META[.<lang>].json 分发成各 agent 侧的 SKILL.md，
// 并把 <name>/assets/** 原样同步过去。
// 用法：
//   node dist.mjs                    写入全部已存在的目标目录，默认中文
//   node dist.mjs --lang en          渲染英文版（缺 BODY.en.md 的 skill 回落中文并提示）
//   node dist.mjs --lang en --strict 缺英文版就非 0 退出，不回落
//   node dist.mjs --check            只检查，生成物与主体不一致就非 0 退出
//   目标目录用环境变量覆盖：PI_SKILLS_DIR / DSH_SKILLS_DIR / CURSOR_SKILLS_DIR /
//   AGENTS_SKILLS_DIR / CLAUDE_SKILLS_DIR。目标目录不存在就跳过；
//   正文里可用 {{SRC_ROOT}}（源仓路径）指回本仓，克隆在哪都对。
//   ~/.agents/skills 是 Pi / Cursor / Codex 共用的那个。
// 侧里只有 SKILL.md 和 assets/ 是生成物，其余文件（learned.md、tune-log.md 等）本机自己维护。

import { readFileSync, writeFileSync, readdirSync, existsSync, statSync, mkdirSync } from "node:fs";
import { join, dirname } from "node:path";
import { homedir } from "node:os";
import { fileURLToPath } from "node:url";

// 源仓就是 dist.mjs 自己所在的目录：仓克隆在哪都能跑；SKILL_SRC 可覆盖。
const SRC = process.env.SKILL_SRC || dirname(fileURLToPath(import.meta.url));
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
  agents: side("AGENTS_SKILLS_DIR", ".agents", "skills"),
  claude: side("CLAUDE_SKILLS_DIR", ".claude", "skills"),
};
const MARK = "<!-- GENERATED：本文件由 skill 源仓的 dist.mjs 生成，改 BODY.md 后重跑；手改会被覆盖 -->";

// <name>/assets/** 里的附件（脚本、references/）同样分发，路径原样保留，只去掉 assets/ 这一层。
function collectAssets(root) {
  if (!existsSync(root)) return [];
  const out = [];
  const walk = (dir, prefix) => {
    for (const entry of readdirSync(dir)) {
      if (entry.startsWith(".")) continue;
      const full = join(dir, entry);
      const rel = prefix ? prefix + "/" + entry : entry;
      if (statSync(full).isDirectory()) walk(full, rel);
      else out.push({ rel, content: readFileSync(full, "utf8") });
    }
  };
  walk(root, "");
  return out;
}

// 替换 profile 占位符；剩下的 {{X}} 一律算错，不静默发出去。
function applyProfile(text, name) {
  let out = text;
  for (const [key, value] of Object.entries(PROFILE)) {
    out = out.split(`{{${key}}}`).join(value);
  }
  const left = [...new Set((out.match(/\{\{[A-Z0-9_]+\}\}/g) || []))];
  for (const token of left) unknown.push(`${name}: ${token}`);
  return out;
}
const check = process.argv.includes("--check");

// 本机覆盖值：profile.default.json 进仓，profile.local.json 只在本机存在（已 gitignore）。
function loadProfile() {
  const read = (f) => (existsSync(f) ? JSON.parse(readFileSync(f, "utf8")) : {});
  const merged = { ...read(join(SRC, "profile.default.json")), ...read(join(SRC, "profile.local.json")) };
  merged.style = { ...(read(join(SRC, "profile.default.json")).style || {}), ...(read(join(SRC, "profile.local.json")).style || {}) };
  return merged;
}

function flatten(obj, prefix = "", out = {}) {
  for (const [k, v] of Object.entries(obj)) {
    const key = `${prefix}${k.replace(/([a-z0-9])([A-Z])/g, "$1_$2").toUpperCase()}`;
    if (v && typeof v === "object") flatten(v, `${key}_`, out);
    else out[key] = String(v);
  }
  return out;
}

const PROFILE = flatten(loadProfile());
const unknown = [];
const langArg = process.argv.indexOf("--lang");
const langFile = join(SRC, ".skill-lang");
const langDefault = existsSync(langFile) ? readFileSync(langFile, "utf8").trim() : "zh";
let lang = (langArg > -1 ? process.argv[langArg + 1] : process.env.SKILL_LANG || langDefault || "zh").toLowerCase();
const strict = process.argv.includes("--strict");

let written = 0;
let drifted = 0;
let skipped = 0;
const fellBack = [];
const missingStrict = [];

for (const name of readdirSync(SRC)) {
  if (name.startsWith(".")) continue;
  const dir = join(SRC, name);
  if (!statSync(dir).isDirectory()) continue;
  if (name.startsWith("_") || name.startsWith(".")) continue;
  if (!existsSync(join(dir, "BODY.md"))) continue;
  const localized = lang === "zh" ? null : join(dir, `BODY.${lang}.md`);
  const hasLocalized = localized && existsSync(localized);
  if (localized && !hasLocalized) {
    fellBack.push(name);
    if (strict) { missingStrict.push(name); continue; }
  }
  const bodyPath = hasLocalized ? localized : join(dir, "BODY.md");
  const metaPath = hasLocalized && existsSync(join(dir, `META.${lang}.json`))
    ? join(dir, `META.${lang}.json`)
    : join(dir, "META.json");
  if (!existsSync(bodyPath) || !existsSync(metaPath)) continue;

  const body = readFileSync(bodyPath, "utf8").replace(/\s+$/, "");
  const meta = JSON.parse(readFileSync(metaPath, "utf8"));
  const assets = collectAssets(join(dir, "assets"));

  for (const [side, { dir: outRoot, root }] of Object.entries(SIDES)) {
    const front = meta[side]?.frontmatter;
    const outPath = join(outRoot, name, "SKILL.md");
    if (!front) continue;
    if (!existsSync(join(outRoot, name))) { skipped++; continue; }

    const rendered = `---\n${applyProfile(front, name)}\n---\n\n${MARK}\n\n${applyProfile(body
      .split("{{SKILL_DIR}}")
      .join(root + name + "/")
      .split("{{SKILLS_ROOT}}")
      .join(root)
      .split("{{SRC_ROOT}}")
      .join(SRC), name)}\n`;

    const current = existsSync(outPath) ? readFileSync(outPath, "utf8") : null;
    if (current !== rendered) {
      if (check) {
        console.error(`drift: ${outPath}`);
        drifted++;
      } else {
        writeFileSync(outPath, rendered);
        written++;
      }
    }

    for (const { rel, content } of assets) {
      const target = join(outRoot, name, rel);
      const existing = existsSync(target) ? readFileSync(target, "utf8") : null;
      if (existing === content) continue;
      if (check) {
        console.error(`drift: ${target}`);
        drifted++;
      } else {
        mkdirSync(dirname(target), { recursive: true });
        writeFileSync(target, content);
        written++;
      }
    }
  }
}

if (check) {
  if (fellBack.length) console.log(`fallback to zh (${lang} missing): ${fellBack.join(", ")}`);
  if (unknown.length) { console.error(`未定义的 profile 占位符：\n  ${unknown.join("\n  ")}`); process.exit(1); }
  if (drifted) { console.error(`\n${drifted} 个生成物与 BODY.md 不一致`); process.exit(1); }
  if (missingStrict.length) { console.error(`--strict: 缺 ${lang} 版：${missingStrict.join(", ")}`); process.exit(1); }
  console.log("ok: 生成物与主体一致");
} else {
  if (fellBack.length) console.log(`fallback to zh (${lang} missing): ${fellBack.join(", ")}`);
  if (unknown.length) { console.error(`未定义的 profile 占位符：\n  ${unknown.join("\n  ")}`); process.exit(1); }
  if (missingStrict.length) { console.error(`--strict: 缺 ${lang} 版：${missingStrict.join(", ")}`); process.exit(1); }
  console.log(`wrote ${written} file(s), skipped ${skipped} missing side dir(s)`);
}

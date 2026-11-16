#!/usr/bin/env node
// 仓库自检（不依赖已安装的 skills 目录，CI 与本地都能跑）：
//   1. 每个 skill 目录有 BODY.md + META.json，五侧 frontmatter 齐全
//   2. 译文正文与中文正文的标题树一致
//   3. 正文里的占位符都在 profile.default.json 里定义
//   4. 已跟踪文件里没有个人信息 / 公司信息 / 密钥形状的字符串
// 用法：node tools/verify.mjs

import { readFileSync, readdirSync, existsSync, statSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const SIDES = ["pi", "cursor", "dsh", "agents", "claude"];
const BUILTIN = new Set(["SKILL_DIR", "SKILLS_ROOT", "SRC_ROOT"]);
const LEAK =
  "pengdali|kitar|@gmail|prod_aws_deploy|deploy_web_prod|sk-[A-Za-z0-9]{24,}|api[_-]?key|BEGIN (RSA|OPENSSH|PRIVATE)";

const errors = [];
const skills = readdirSync(ROOT).filter(
  (n) => !n.startsWith("_") && !n.startsWith(".") && statSync(join(ROOT, n)).isDirectory() && existsSync(join(ROOT, n, "BODY.md")),
);

function flatten(obj, prefix = "", out = {}) {
  for (const [k, v] of Object.entries(obj)) {
    const key = `${prefix}${k.replace(/([a-z0-9])([A-Z])/g, "$1_$2").toUpperCase()}`;
    if (v && typeof v === "object") flatten(v, `${key}_`, out);
    else out[key] = String(v);
  }
  return out;
}

let profile = {};
try {
  profile = flatten(JSON.parse(readFileSync(join(ROOT, "profile.default.json"), "utf8")));
} catch (e) {
  errors.push(`profile.default.json 无法解析：${e.message}`);
}

// 标题树只比骨架（层级序列），不比文字：译文的标题本来就是另一种语言。
const headings = (text) =>
  text
    .split("\n")
    .filter((l) => /^#{1,6} /.test(l))
    .map((l) => (l.match(/^#+/) || [""])[0].length)
    .join(",");

for (const name of skills) {
  const dir = join(ROOT, name);
  if (!existsSync(join(dir, "META.json"))) {
    errors.push(`${name}: 缺 META.json`);
    continue;
  }
  let meta;
  try {
    meta = JSON.parse(readFileSync(join(dir, "META.json"), "utf8"));
  } catch (e) {
    errors.push(`${name}: META.json 无法解析：${e.message}`);
    continue;
  }
  if (!meta.pi?.frontmatter) errors.push(`${name}: META.json 至少要有 pi 侧 frontmatter`);
  for (const side of Object.keys(meta)) {
    if (!SIDES.includes(side)) { errors.push(`${name}: META.json 有未知的侧 ${side}`); continue; }
    const fm = meta[side]?.frontmatter;
    if (!fm) errors.push(`${name}: ${side} 侧 frontmatter 为空`);
    else if (!/^name: /m.test(fm)) errors.push(`${name}: ${side} frontmatter 缺 name`);
    else if (!new RegExp(`^name: ${name}$`, "m").test(fm)) errors.push(`${name}: ${side} frontmatter 的 name 与目录名不一致`);
    else if (!/^description: /m.test(fm)) errors.push(`${name}: ${side} frontmatter 缺 description`);
  }

  const zh = readFileSync(join(dir, "BODY.md"), "utf8");
  for (const file of [join(dir, "META.json"), join(dir, "BODY.md")]) {
    const text = readFileSync(file, "utf8");
    for (const token of new Set(text.match(/\{\{[A-Z0-9_]+\}\}/g) || [])) {
      const key = token.slice(2, -2);
      if (!BUILTIN.has(key) && !(key in profile)) errors.push(`${name}: 未定义的占位符 ${token}（${file.split("/").pop()}）`);
    }
  }

  for (const file of readdirSync(dir)) {
    const m = file.match(/^BODY\.([a-z]{2})\.md$/);
    if (!m) continue;
    const translated = readFileSync(join(dir, file), "utf8");
    if (headings(translated) !== headings(zh)) errors.push(`${name}: BODY.${m[1]}.md 的标题树与 BODY.md 不一致`);
    const localizedMeta = join(dir, `META.${m[1]}.json`);
    if (!existsSync(localizedMeta)) { errors.push(`${name}: 有 ${file} 但缺 META.${m[1]}.json`); continue; }
    let lm;
    try {
      lm = JSON.parse(readFileSync(localizedMeta, "utf8"));
    } catch (e) {
      errors.push(`${name}: META.${m[1]}.json 无法解析：${e.message}`);
      continue;
    }
    // 少一侧就等于那一侧悄悄没有英文版，渲染时静默跳过
    for (const side of Object.keys(meta)) {
      if (!lm[side]) errors.push(`${name}: META.${m[1]}.json 缺 ${side} 侧（META.json 有）`);
    }
    for (const side of Object.keys(lm)) {
      if (!meta[side]) errors.push(`${name}: META.${m[1]}.json 多出 ${side} 侧（META.json 没有）`);
    }
  }
}

let tracked = [];
try {
  tracked = execFileSync("git", ["ls-files", "-z"], { cwd: ROOT, encoding: "utf8" })
    .split("\0")
    .filter(Boolean);
} catch {
  errors.push("不是 git 仓库，无法做敏感词扫描");
}

const leak = new RegExp(LEAK, "i");
const self = "tools/verify.mjs";
for (const file of tracked) {
  if (file === self || file === "LICENSE" || file.startsWith("legacy/") || file.startsWith(".githooks/")) continue;
  let text;
  try {
    text = readFileSync(join(ROOT, file), "utf8");
  } catch {
    continue;
  }
  text.split("\n").forEach((line, i) => {
    if (leak.test(line)) errors.push(`${file}:${i + 1}: 命中敏感词 -> ${line.trim().slice(0, 100)}`);
  });
}

if (errors.length) {
  console.error(`verify: ${errors.length} 个问题`);
  for (const e of errors) console.error("  " + e);
  process.exit(1);
}
console.log(`verify: ok（${skills.length} 个 skill）`);

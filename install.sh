#!/usr/bin/env bash
# 一键把本仓渲染进各 agent 的 skills 目录。
#
# 用法：
#   ./install.sh                 自动探测已装的 agent，逐个渲染（默认中文）
#   ./install.sh --lang en       渲染英文版
#   ./install.sh --dirs agents,claude   只写这两处（可选：pi / cursor / dsh / agents / claude）
#   ./install.sh --dry-run       只打印将要做什么
#   ./install.sh --no-hooks      不设置 core.hooksPath
#
# 侧与目录的对应：
#   agents -> ~/.agents/skills   Pi / Cursor / Codex 共用，推荐只装这一份
#   claude -> ~/.claude/skills   Claude Code 只认这个目录
#   pi     -> ~/.pi/agent/skills
#   cursor -> ~/.cursor/skills
#   dsh    -> ~/.dsh/skills

set -euo pipefail

REPO="$(cd "$(dirname "$0")" && pwd)"
SIDE_NAMES="pi cursor dsh agents claude"
LANG_SEL="${SKILL_LANG:-zh}"
DIRS=""
DRY_RUN=""
HOOKS=1

while [ $# -gt 0 ]; do
  case "$1" in
    --lang) LANG_SEL="$2"; shift 2 ;;
    --lang=*) LANG_SEL="${1#*=}"; shift ;;
    --dirs) DIRS="$2"; shift 2 ;;
    --dirs=*) DIRS="${1#*=}"; shift ;;
    --dry-run|-n) DRY_RUN=1; shift ;;
    --no-hooks) HOOKS=0; shift ;;
    -h|--help) sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "未知参数：$1" >&2; exit 2 ;;
  esac
done

dir_for() {
  case "$1" in
    pi) echo "$HOME/.pi/agent/skills" ;;
    cursor) echo "$HOME/.cursor/skills" ;;
    dsh) echo "$HOME/.dsh/skills" ;;
    agents) echo "$HOME/.agents/skills" ;;
    claude) echo "$HOME/.claude/skills" ;;
  esac
}

if [ -z "$DIRS" ]; then
  detected=""
  for probe in pi cursor dsh; do
    if [ -d "$HOME/.$probe" ]; then detected="$detected $probe"; fi
  done
  has_claude=""
  if [ -d "$HOME/.claude" ]; then has_claude="claude"; fi

  own=$(printf '%s\n' $detected | grep -c . || true)
  if [ -z "$detected" ]; then
    # 什么都没装：按推荐布局写共享目录
    DIRS="agents"
  elif [ "$own" -ge 2 ]; then
    # 装了多个：写共享目录，避免同一个 skill 被两个目录各发现一次
    DIRS="agents"
  else
    DIRS="$(echo $detected)"
  fi
  if [ -n "$has_claude" ]; then DIRS="$DIRS claude"; fi
  DIRS="$(echo $DIRS | tr ' ' ',')"
fi

echo "仓库：$REPO"
echo "语言：$LANG_SEL"
echo "目标：$DIRS"

for s in $(echo "$DIRS" | tr ',' ' '); do
  case " $SIDE_NAMES " in
    *" $s "*) ;;
    *) echo "未知目标：${s}（可选 ${SIDE_NAMES}）" >&2; exit 2 ;;
  esac
  target="$(dir_for "$s")"
  if [ -n "$DRY_RUN" ]; then
    echo "  ${s} -> ${target}（将创建 $(ls -d "$REPO"/*/ | wc -l | tr -d ' ') 个 skill 目录）"
    continue
  fi
  mkdir -p "$target"
  for d in "$REPO"/*/; do
    name="$(basename "$d")"
    if [ -f "$d/BODY.md" ]; then mkdir -p "$target/$name"; fi
  done
done

if [ -n "$DRY_RUN" ]; then
  echo "（dry-run，未写入）"
  exit 0
fi

# 未选中的侧指向不存在的目录，dist.mjs 会跳过
run_dist() {
  env \
    PI_SKILLS_DIR="$(pick pi "$HOME/.pi/agent/skills")" \
    CURSOR_SKILLS_DIR="$(pick cursor "$HOME/.cursor/skills")" \
    DSH_SKILLS_DIR="$(pick dsh "$HOME/.dsh/skills")" \
    AGENTS_SKILLS_DIR="$(pick agents "$HOME/.agents/skills")" \
    CLAUDE_SKILLS_DIR="$(pick claude "$HOME/.claude/skills")" \
    node "$REPO/dist.mjs" --lang "$LANG_SEL" "$@"
}

pick() {
  case ",$(echo "$DIRS" | tr ' ' ',')," in
    *",$1,"*) echo "$2" ;;
    *) echo "$HOME/.commander-skills-unused/$1" ;;
  esac
}

printf '%s\n' "$LANG_SEL" > "$REPO/.skill-lang"

run_dist

if [ "$HOOKS" = "1" ]; then
  git -C "$REPO" config core.hooksPath .githooks 2>/dev/null \
    && echo "已设置 core.hooksPath = .githooks" \
    || echo "（跳过 hooks：不是 git 仓库）"
fi

run_dist --check
echo
echo "完成。让 agent 重新扫描：Pi 里 /reload，或重开一次会话；/skill:commander 可验证。"

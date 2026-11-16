#!/usr/bin/env bash
# 一键把本仓渲染进各 agent 的 skills 目录，或把装进去的东西撤掉。
#
# 用法：
#   ./install.sh                 自动探测已装的 agent，逐个渲染（默认中文）
#   ./install.sh --lang en       渲染英文版
#   ./install.sh --dirs agents,claude   只写这两处（可选：pi / cursor / dsh / agents / claude）
#   ./install.sh --dry-run       只打印将要做什么
#   ./install.sh --no-hooks      不设置 core.hooksPath
#   ./install.sh --clean-old     清掉上次装过、这次没选的侧（否则同一个 skill 会被两个目录各发现一次）
#   ./install.sh --uninstall     删掉装进去的 SKILL.md 与 assets/，本机自有文件不动
#   ./install.sh --version       打印版本
#
# 侧与目录的对应：
#   agents -> ~/.agents/skills   Pi / Cursor / Codex 共用，推荐只装这一份
#   claude -> ~/.claude/skills   Claude Code 只认这个目录
#   pi     -> ~/.pi/agent/skills
#   cursor -> ~/.cursor/skills
#   dsh    -> ~/.dsh/skills

set -euo pipefail

REPO="$(cd "$(dirname "$0")" && pwd)"
VERSION="$(cat "$REPO/VERSION" 2>/dev/null || echo dev)"
SIDE_NAMES="pi cursor dsh agents claude"
LANG_SEL="${SKILL_LANG:-zh}"
DIRS=""
DRY_RUN=""
HOOKS=1
UNINSTALL=0
CLEAN_OLD=0

while [ $# -gt 0 ]; do
  case "$1" in
    --lang) LANG_SEL="$2"; shift 2 ;;
    --lang=*) LANG_SEL="${1#*=}"; shift ;;
    --dirs) DIRS="$2"; shift 2 ;;
    --dirs=*) DIRS="${1#*=}"; shift ;;
    --dry-run|-n) DRY_RUN=1; shift ;;
    --no-hooks) HOOKS=0; shift ;;
    --clean-old) CLEAN_OLD=1; shift ;;
    --uninstall) UNINSTALL=1; shift ;;
    --version) echo "commander-skills $VERSION"; exit 0 ;;
    -h|--help) sed -n '2,25p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "未知参数：$1" >&2; exit 2 ;;
  esac
done

# 按 .generated 清单删掉某一侧装进去的东西；本机自有文件与别人同名 skill 都不动。
removed=0
kept=0
remove_side() {
  target="$(dir_for "$1")"
  [ -d "$target" ] || return 0
  for d in "$REPO"/*/; do
    name="$(basename "$d")"
    [ -f "$d/BODY.md" ] || continue
    file="$target/$name/SKILL.md"
    man="$target/$name/.generated"
    if [ -f "$man" ]; then
      if [ -n "$DRY_RUN" ]; then
        echo "  将按 .generated 清理 ${target}/${name}（$(grep -c . "$man") 个文件）"
        continue
      fi
      while IFS= read -r rel; do
        [ -n "$rel" ] && rm -f "$target/$name/$rel"
      done < "$man"
      rm -f "$man"
      find "$target/$name" -mindepth 1 -type d -empty -delete 2>/dev/null || true
      if rmdir "$target/$name" 2>/dev/null; then
        removed=$((removed + 1))
      else
        echo "  保留 ${target}/${name}（里面还有本机自有文件）"
        kept=$((kept + 1))
      fi
    elif [ -f "$file" ] && grep -q "GENERATED" "$file"; then
      # 老版本没写清单：退回到「按标记删 SKILL.md + assets/」
      if [ -n "$DRY_RUN" ]; then
        echo "  将删除 ${target}/${name}/SKILL.md"
        continue
      fi
      rm -f "$file"
      rm -rf "$target/$name/assets"
      if rmdir "$target/$name" 2>/dev/null; then
        removed=$((removed + 1))
      else
        echo "  保留 ${target}/${name}（里面还有本机自有文件）"
        kept=$((kept + 1))
      fi
    fi
  done
}

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

  # 卸载时还要覆盖上次装过的侧，否则残留找不到
  if [ "$UNINSTALL" = "1" ] && [ -f "$REPO/.installed" ]; then
    DIRS="$(cat "$REPO/.installed")"
  else
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
fi

for s in $(echo "$DIRS" | tr ',' ' '); do
  case " $SIDE_NAMES " in
    *" $s "*) ;;
    *) echo "未知目标：${s}（可选 ${SIDE_NAMES}）" >&2; exit 2 ;;
  esac
done

if [ "$UNINSTALL" = "1" ]; then
  echo "版本：$VERSION"
  echo "仓库：$REPO"
  echo "目标：$DIRS"
  removed=0
  kept=0
  for s in $(echo "$DIRS" | tr ',' ' '); do
    remove_side "$s"
  done
  if [ -n "$DRY_RUN" ]; then
    echo "（dry-run，未删除）"
    exit 0
  fi
  git -C "$REPO" config --unset core.hooksPath 2>/dev/null || true
  rm -f "$REPO/.installed"
  echo "已清理 ${removed} 个 skill 目录；${kept} 个因含本机文件被保留。"
  exit 0
fi

echo "版本：$VERSION"
echo "仓库：$REPO"
echo "语言：$LANG_SEL"
echo "目标：$DIRS"

# 上次装过、这次没选的侧：留着会让同一个 skill 被两个目录各发现一次
prev="$(cat "$REPO/.installed" 2>/dev/null || true)"
stale=""
if [ -n "$prev" ]; then
  for s in $(echo "$prev" | tr ',' ' '); do
    case ",$DIRS," in
      *",$s,"*) ;;
      *) stale="$stale $s" ;;
    esac
  done
  stale="${stale# }"
fi
if [ -n "$stale" ]; then
  if [ "$CLEAN_OLD" = "1" ]; then
    echo "清理上次装过的侧：$stale"
    for s in $stale; do remove_side "$s"; done
    prev="$DIRS"
  else
    echo "注意：这些侧上次装过、这次没选，旧文件仍在，同一个 skill 会被重复发现：$stale" >&2
    echo "      清理：./install.sh --clean-old（本机自有文件不会被动）" >&2
  fi
fi

for s in $(echo "$DIRS" | tr ',' ' '); do
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
# 记录「装过哪些侧」，含这次没选但还没清的那些，下次才能提示 --clean-old
printf '%s\n' "$(echo "$prev" | tr ',' '\n' | { cat; echo "$DIRS" | tr ',' '\n'; } | grep -v '^$' | sort -u | paste -sd, -)" > "$REPO/.installed"

run_dist

if [ "$HOOKS" = "1" ]; then
  git -C "$REPO" config core.hooksPath .githooks 2>/dev/null \
    && echo "已设置 core.hooksPath = .githooks" \
    || echo "（跳过 hooks：不是 git 仓库）"
fi

run_dist --check
echo
echo "完成。让 agent 重新扫描：Pi 里 /reload，或重开一次会话；/skill:commander 可验证。"

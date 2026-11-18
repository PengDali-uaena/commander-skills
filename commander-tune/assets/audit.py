#!/usr/bin/env python3
"""commander-tune 会话审计：统计 Pi 会话里 skill 的调用与用户反馈。

用法：
  python3 audit.py                 # 近 14 天，全部仓库
  python3 audit.py --days 30       # 扩大窗口；--days 0 表示不限
  python3 audit.py --repo my-repo  # 只匹配会话目录名（子串）
  python3 audit.py --skill explain # 打印该 skill 每一轮的提问与下一条反应
  python3 audit.py --json          # 输出机器可读结果

只读某一侧的 sessions 目录（默认 Pi 的 ~/.pi/agent/sessions，用 --sessions 指定别的），不写任何文件。
本文件是 commander-tune 的附属脚本，不属于 dist.mjs 生成物，可直接手改。
"""

import argparse
import glob
import json
import os
import re
import statistics
import time
from collections import Counter

SESSIONS = os.path.expanduser("~/.pi/agent/sessions")  # 可被 --sessions 覆盖
SKILLS = os.path.expanduser("~/.pi/agent/skills")  # 可被 --skills 覆盖
SKILL_PATH = re.compile(r"skills/([a-z0-9][a-z0-9-]*)/SKILL\.md")
ATTACHED = re.compile(r"^<skill name=")
ACK = re.compile(r"^(好|好的|好滴|嗯+|ok|okay|行|可以|继续|是|对|谢谢|收到|y|yes|no|不|别|等一下|稍等)[。！!,.，\s]*$", re.I)
REJECT = re.compile(r"不对|不是这|不是我说|错了|重新|废话|太啰嗦|太长|太多了|简短|精简|看不懂|没改|还是没|又错|都说了|说错|搞错|别加|不用加|多余|信息太多")
REJECT_HEAD = re.compile(r"^(不对|错了|不是这|不是我说|太啰嗦|太长|太多了|简短|精简|看不懂|没改|还是没|又错|说错|搞错|别加|不用加|多余|信息太多)")
# 只有真正把 SKILL.md 内容读出来的命令才算读取；grep / ls / diff / wc 这类只提路径的命令不算。
READ_CMD = re.compile(r"^\s*((cat|bat|less|head|tail|sed\s+-n|nl)\b|\S*\s+(cat|bat|less|head|tail|sed\s+-n)\s)")
SHORT_REJECT_MAX = 60
REPO = re.compile(r"^--(.+)--$")


def repos_label(path):
    m = REPO.match(os.path.basename(os.path.dirname(path)))
    home_slug = os.path.expanduser("~").replace("/", "-")
    return m.group(1).replace(home_slug, "").strip("-") or "(home)" if m else "?"


def skill_reads(tool, args):
    """只把「真正把 SKILL.md 读出来」的 toolCall 算作一次读取。

    grep / ls / diff / wc 这类只是在参数里提到路径的命令不算；同参数的重复调用
    （重试同一条命令）由 load_turns 去重。
    """
    paths = SKILL_PATH.findall(json.dumps(args, ensure_ascii=False))
    if not paths:
        return []
    if tool == "read":
        return paths
    if tool == "bash":
        cmd = str(args.get("command", ""))
        return paths if READ_CMD.match(cmd) else []
    return paths


def load_turns(path, known):
    turns, cur = [], None
    for line in open(path, encoding="utf-8", errors="ignore"):
        try:
            obj = json.loads(line)
        except ValueError:
            continue
        if obj.get("type") != "message":
            continue
        msg = obj["message"]
        role, content = msg.get("role"), msg.get("content")
        if role == "user":
            text = "".join(p.get("text", "") for p in content if isinstance(p, dict)) if isinstance(content, list) else str(content)
            if not text.strip():
                continue
            if cur:
                turns.append(cur)
            cur = {"ts": obj.get("timestamp", "")[:10], "user": text, "reads": [], "seen": set(), "answer": ""}
        elif role == "assistant" and cur is not None and isinstance(content, list):
            for part in content:
                if part.get("type") == "toolCall":
                    key = (part.get("name"), json.dumps(part.get("arguments", {}), ensure_ascii=False, sort_keys=True))
                    if key in cur["seen"]:
                        continue
                    cur["seen"].add(key)
                    for name in skill_reads(part.get("name"), part.get("arguments", {})):
                        if name in known:
                            cur["reads"].append(name)
                elif part.get("type") == "text" and part.get("text", "").strip():
                    cur["answer"] = part["text"]
        elif role == "toolResult" and cur is not None and isinstance(content, list):
            blob = json.dumps(content, ensure_ascii=False)
            for name in SKILL_PATH.findall(blob):
                if name in known and name not in cur["reads"]:
                    cur["reads"].append(name)
    if cur:
        turns.append(cur)
    for t in turns:
        t.pop("seen", None)
    return turns


def drop_live_turn(path, turns, live_window=900):
    """丢掉最后一个还没结束的轮次（会话文件刚写过、该轮还没出文字）。"""
    if not turns:
        return turns
    try:
        age = time.time() - os.path.getmtime(path)
    except OSError:
        return turns
    if age < live_window and not turns[-1]["answer"].strip():
        return turns[:-1]
    return turns


def reaction(text):
    text = text.strip()
    if ACK.match(text):
        return "ack"
    if REJECT_HEAD.match(text) or (len(text) <= SHORT_REJECT_MAX and REJECT.search(text)):
        return "reject"
    return "next"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skills", default=SKILLS, help="skills 目录，默认 Pi 的 ~/.pi/agent/skills")
    ap.add_argument("--sessions", default=SESSIONS, help="sessions 目录，默认 Pi 的 ~/.pi/agent/sessions")
    ap.add_argument("--days", type=int, default=14, help="0 = 不限")
    ap.add_argument("--repo", default="")
    ap.add_argument("--skill", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    skills_dir = os.path.expanduser(args.skills)
    known = set(os.listdir(skills_dir)) if os.path.isdir(skills_dir) else set()
    sessions_dir = os.path.expanduser(args.sessions)
    files = sorted(glob.glob(os.path.join(sessions_dir, "**", "*.jsonl"), recursive=True))
    if args.repo:
        files = [f for f in files if args.repo in os.path.basename(os.path.dirname(f))]

    sessions, turns = 0, []
    for path in files:
        rows = drop_live_turn(path, load_turns(path, known))
        if not rows:
            continue
        sessions += 1
        for row in rows:
            row["repo"] = repos_label(path)
        turns.extend(rows)

    if args.days:
        dates = sorted(t["ts"] for t in turns if t["ts"])
        if dates:
            cutoff = dates[-1]
            import datetime
            end = datetime.date.fromisoformat(cutoff) - datetime.timedelta(days=args.days - 1)
            turns = [t for t in turns if t["ts"] >= end.isoformat()]

    real, attached = [], 0
    for t in turns:
        if ATTACHED.match(t["user"]) or t["user"].startswith("<skill name="):
            attached += 1
        elif ACK.match(t["user"].strip()):
            attached += 1
        else:
            real.append(t)

    def metrics(idx):
        n = len(idx)
        if not n:
            return {}
        ans = [turns[i]["answer"] for i in idx]
        lines = [len([l for l in a.split("\n") if l.strip()]) for a in ans if a]
        return {
            "turns": n,
            "reject": sum(1 for i in idx if i + 1 < len(turns) and reaction(turns[i + 1]["user"]) == "reject"),
            "ack": sum(1 for i in idx if i + 1 < len(turns) and reaction(turns[i + 1]["user"]) == "ack"),
            "median_lines": statistics.median(lines) if lines else 0,
            "empty": sum(1 for a in ans if not a),
            "bold_first": round(100 * sum(1 for a in ans if a.strip().startswith("**")) / max(len([a for a in ans if a]), 1)),
            "abs_path": sum(1 for a in ans if "/Users/" in a),
        }

    index = {id(t): i for i, t in enumerate(turns)}
    per_skill = {}
    for name in sorted(known):
        idx = [index[id(t)] for t in turns if name in t["reads"]]
        if idx:
            per_skill[name] = metrics(idx)

    no_skill = [index[id(t)] for t in real if not t["reads"]]
    summary = {
        "window_days": args.days or "all",
        "sessions": sessions,
        "turns": len(turns),
        "real_requests": len(real),
        "skipped": attached,
        "skill_read_share": round(100 * sum(1 for t in real if t["reads"]) / max(len(real), 1)),
        "no_skill": metrics(no_skill),
        "skills": per_skill,
        "repeat_reads": dict(Counter(n for t in turns for n, c in Counter(t["reads"]).items() if c > 1).most_common()),
    }

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return

    print(f"窗口: {summary['window_days']} 天 | 会话: {sessions} | 消息轮: {len(turns)} | 真实请求: {len(real)}")
    print(f"读过至少一个 skill 的真实请求: {summary['skill_read_share']}% | 无 skill 轮: {len(no_skill)}")
    print(f"无 skill 轮: 首句加粗 {summary['no_skill'].get('bold_first', 0)}% | 绝对路径 {summary['no_skill'].get('abs_path', 0)} 条")
    print(f"同轮重复读: {summary['repeat_reads'] or '无'}")
    print()
    print(f"{'skill':26}{'轮次':>5}{'打回':>5}{'继续':>5}{'中位行':>7}{'空答':>5}{'加粗%':>7}{'绝对路径':>7}")
    for name, m in sorted(per_skill.items(), key=lambda kv: -kv[1]["turns"]):
        print(f"{name:26}{m['turns']:>5}{m['reject']:>5}{m['ack']:>5}{m['median_lines']:>7}{m['empty']:>5}{m['bold_first']:>7}{m['abs_path']:>7}")
    print("\n注：轮次含「改 skill 时顺带读」的轮次；判断效果看「打回」，次数少不等于有问题。")

    if args.skill:
        print(f"\n=== {args.skill} 的每一轮 ===")
        for t in turns:
            if args.skill not in t["reads"]:
                continue
            i = index[id(t)]
            nxt = turns[i + 1]["user"].strip().replace("\n", " ")[:40] if i + 1 < len(turns) else "(end)"
            lines = len([l for l in t["answer"].split("\n") if l.strip()])
            print(f"  {t['ts']} [{t['repo']}] {lines} 行 | 问: {t['user'].strip()[:36]} | 下一条: {nxt}")


if __name__ == "__main__":
    main()

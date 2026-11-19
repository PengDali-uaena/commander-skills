#!/usr/bin/env python3
"""validate_task_doc.py — prd-to-task 文档的结构校验（落盘前必跑，不许自评）。

用法：
  python3 validate_task_doc.py docs/xxxx-task-foo.md
  python3 validate_task_doc.py docs/xxxx-task-foo.md --repo . \
      --nodes docs/feature-a/nodes.tsv --manifest assets.review.tsv
  python3 validate_task_doc.py docs/xxxx-task-foo.md --legacy   # 结构问题降级为 WARN

退出码：0 全过；1 有 FAIL；2 文件读不到。

校验内容：
  1. 头部四行（状态 / 阻塞项 / 需求来源 / 更新时间）
  2. 每个 F 功能点的必填小节齐全且非空
  3. 13 张表的表头列齐全（缺列即 FAIL）
  4. 头部阻塞计数 == 待定项表按阻塞级别的行数
  5. 状态与计数一致
  6. 资产行「导出方式」不得写 export；资源文件必须存在（--repo 生效）
  7. 文档里的 node-id 必须在取证存档里（--nodes 生效）
  8. 验收句黑名单、台账重复关键词、空表
"""

import argparse
import os
import re
import sys

HEADER_FIELDS = ["状态", "阻塞项", "需求来源", "更新时间"]

REQUIRED_SECTIONS = [
    "逻辑",
    "功能与 UI",
    "元素清单",
    "视觉骨架",
    "视觉规格",
    "交互状态",
    "权限与容量",
    "枚举与兜底",
    "状态 → 视觉",
    "UI 资产与图标",
    "接口失败与降级",
    "部分回包与缺失",
    "标识与外部输入",
    "请求预算与缓存",
    "等待回调的超时",
    "新增抽象契约",
    "埋点",
    "双语",
    "验收",
]

# 小节名 -> 表头必须包含的列关键字
SECTION_COLUMNS = {
    "交互状态": ["控件", "点击瞬间", "回包前", "回包后", "失败", "重复点"],
    "权限与容量": ["字段", "来源接口", "还敢点"],
    "枚举与兜底": ["字段", "取值", "未知值"],
    "状态 → 视觉": ["取值", "视觉", "可点性", "上报"],
    "视觉骨架": ["位置", "容器"],
    "视觉规格": ["node", "文字", "尺寸", "间距", "资源逻辑尺寸"],
    "UI 资产与图标": ["复用组件", "来源", "导出方式", "尺寸"],
    "接口失败与降级": ["失败落点", "文案", "重试", "刷新"],
    "部分回包与缺失": ["回包字段组合", "缺失字段处理", "覆盖"],
    "标识与外部输入": ["来源字段", "接收侧", "格式约束", "缺失"],
    "请求预算与缓存": ["触发点", "去重键", "缓存", "清理"],
    "等待回调的超时": ["链路", "等待对象", "超时", "复原"],
    "新增抽象契约": ["消费者", "默认值", "同源"],
}

ACCEPTANCE_BLACKLIST = ["以接口返回为准", "正常展示", "同上", "视情况", "看接口"]
STATE_VALUES = ["进行中", "待定补充", "可执行", "已实现", "已核对"]
NODE_ID = re.compile(r"\b\d{4,}:\d{3,}\b")
ASSET_PATH = re.compile(r"assets/[\w\-./]*\.(?:png|svg)")

fails = []
warns = []


def fail(check, detail):
    fails.append((check, detail))


def warn(check, detail):
    warns.append((check, detail))


def norm(text):
    """小节名归一：去空格、去全角空格、统一箭头。"""
    text = text.replace("　", "").replace(" ", "")
    text = text.replace("→", "→").replace("->", "→")
    return text


def parse_headings(lines):
    """返回 [(level, raw_title, normalized_title, line_index)]"""
    out = []
    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            out.append((len(m.group(1)), m.group(2).strip(), norm(m.group(2).strip()), i))
    return out


def section_body(lines, headings, idx):
    """取出某标题下的内容行（到下一个同级或更高级标题为止）。"""
    level, _, _, start = headings[idx]
    end = len(lines)
    for lv, _, _, i in headings[idx + 1:]:
        if lv <= level:
            end = i
            break
    return lines[start + 1:end]


def find_section(headings, name, within=None):
    """在 headings 里找归一化名字匹配的小节；within=(start,end) 限定范围。"""
    target = norm(name)
    for idx, (level, raw, ntitle, line_no) in enumerate(headings):
        if within and not (within[0] <= line_no < within[1]):
            continue
        if ntitle == target or ntitle.startswith(target):
            return idx
    return None


def tables_in(body):
    """返回该段所有 markdown 表：[(header_cells, data_row_count, first_header_line)]"""
    tables = []
    i = 0
    while i < len(body):
        line = body[i].strip()
        if line.startswith("|") and i + 1 < len(body) and re.match(r"^\|[\s:\-|]+\|$", body[i + 1].strip()):
            header = [c.strip() for c in line.strip("|").split("|")]
            rows = 0
            j = i + 2
            while j < len(body) and body[j].strip().startswith("|"):
                rows += 1
                j += 1
            tables.append((header, rows, i))
            i = j
        else:
            i += 1
    return tables


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("doc")
    ap.add_argument("--repo", default=None, help="仓库根，用于核对资源文件是否落盘")
    ap.add_argument("--nodes", default=None, help="nodes.tsv 取证存档")
    ap.add_argument("--manifest", default=None, help="check_assets 的清单，逐行 path lw lh mode")
    ap.add_argument("--legacy", action="store_true", help="结构问题降级为 WARN（老文档用）")
    args = ap.parse_args()

    if not os.path.isfile(args.doc):
        print(f"validator: 读不到文档 {args.doc}")
        return 2
    with open(args.doc, encoding="utf-8") as fh:
        lines = fh.read().split("\n")

    def structural(check, detail):
        (warn if args.legacy else fail)(check, detail)

    headings = parse_headings(lines)

    # 1. 头部四行
    head_text = "\n".join(lines[:40])
    for field in HEADER_FIELDS:
        if not re.search(rf"^{re.escape(field)}[：:]\s*\S", head_text, re.M):
            structural("头部", f"缺 `{field}：` 行（前 40 行内）")

    # 1b. 复杂度档位 / 技能版本 / node 计数（档位决定必填多少）
    tier = None
    mtier = re.search(r"^复杂度档位[：:]\s*([SML])", head_text, re.M)
    if not mtier:
        structural("复杂度档位", "缺 `复杂度档位：S / M / L` 行（不判档就会要么全填要么全跳）")
    else:
        tier = mtier.group(1)
    if not re.search(r"^技能版本[：:]\s*\S", head_text, re.M):
        warn("技能版本", "缺 `技能版本：<md5 前 8 位> / <时间>` 行，跨 agent 时无法判断跑在哪版技能上")

    doc_nodes = set()
    for line in lines:
        doc_nodes.update(NODE_ID.findall(line))

    S_SKIPPABLE = {"权限与容量", "标识与外部输入", "请求预算与缓存", "等待回调的超时", "新增抽象契约", "部分回包与缺失"}

    # 2. 每个 F 功能点的小节
    feature_blocks = []
    for idx, (level, raw, ntitle, line_no) in enumerate(headings):
        if level in (2, 3) and re.match(r"^F\d", raw.replace(" ", "")):
            end = len(lines)
            for lv, _, _, i in headings[idx + 1:]:
                if lv <= level:
                    end = i
                    break
            feature_blocks.append((raw, line_no, end))
    if not feature_blocks:
        structural("功能点", "没有找到 `## F1 …` 形式的功能点小节")

    for name, start, end in feature_blocks:
        block_lines = lines[start + 1:end]
        skipped = set()
        for line in block_lines:
            m = re.match(r"^\s*(?:>\s*)?表适用性[：:]\s*(.+)$", line)
            if m:
                skip_part = re.sub(r"^\s*跳过\s*", "", m.group(1))
                for token in re.split(r"[、,，/]", skip_part):
                    token = token.strip()
                    if not token:
                        continue
                    if tier == "S" and norm(re.split(r"[（(]", token)[0]) not in {norm(x) for x in S_SKIPPABLE}:
                        warn("表适用性", f"{name} 在 S 档跳过了 `{token.split('（')[0]}`，该表不在 S 档可跳过清单里")
                    if "（" not in token and "(" not in token:
                        warn("表适用性", f"{name} 跳过 `{token}` 没写原因，格式应为 `表适用性：跳过 权限与容量（本功能无后端字段）`")
                    skipped.add(norm(re.split(r"[（(]", token)[0]))
        for sec in REQUIRED_SECTIONS:
            if norm(sec) in skipped:
                continue
            idx = find_section(headings, sec, within=(start + 1, end))
            if idx is None:
                structural("必填小节", f"{name} 缺 `### {sec}`（确实不适用就写 `表适用性：跳过 {sec}（原因）`）")
                continue
            body = section_body(lines, headings, idx)
            content = [l for l in body if l.strip() and not l.strip().startswith("|")]
            has_table = bool(tables_in(body))
            if not content and not has_table:
                structural("空小节", f"{name} 的 `### {sec}` 没有内容（不适用也要写 `无（原因…）`）")

    # 3. 13 张表的列
    for sec, cols in SECTION_COLUMNS.items():
        for name, start, end in feature_blocks:
            idx = find_section(headings, sec, within=(start + 1, end))
            if idx is None:
                continue
            body = section_body(lines, headings, idx)
            tables = tables_in(body)
            if not tables:
                has_na = any(l.strip().startswith("- 无") or "无（" in l for l in body)
                if not has_na:
                    structural("表缺失", f"{name} 的 `{sec}` 没有表，也没写 `无（原因…）`")
                continue
            header = norm("".join(tables[0][0]))
            for col in cols:
                if norm(col) not in header:
                    structural("缺列", f"{name} 的 `{sec}` 表头缺列 `{col}`")
            for header_cells, rows, _ in tables:
                if rows == 0:
                    if sec == "视觉骨架":
                        fail("UI 门禁", f"{name} 的 `视觉骨架` 有表头无数据行：结构没落表就开工，等于让实现自己拼层叠")
                    else:
                        warn("空表", f"{name} 的 `{sec}` 有表头无数据行")

    # 3b. 档位一致性：L 档或 node>20 时视觉规格必须逐区块（≥8 行）
    big = (tier == "L") or len(doc_nodes) > 20
    if big:
        for name, start, end in feature_blocks:
            idx = find_section(headings, "视觉规格", within=(start + 1, end))
            if idx is None:
                continue
            tables = tables_in(section_body(lines, headings, idx))
            rows = sum(r for _, r, _ in tables)
            if rows < 8:
                structural(
                    "档位一致性",
                    f"{name} 是 L 档 / 文档含 {len(doc_nodes)} 个 node，`视觉规格` 只有 {rows} 行（要求 ≥8，逐可见区块）",
                )

    # 4. 阻塞计数
    m = re.search(r"阻塞项[：:]\s*开发\s*(\d+)\s*/\s*联调\s*(\d+)\s*/\s*不阻塞\s*(\d+)", head_text)
    if not m:
        structural("阻塞项", "头部 `阻塞项：开发 X / 联调 Y / 不阻塞 Z` 格式不对或缺失")
    else:
        want = tuple(int(x) for x in m.groups())
        idx = find_section(headings, "待定项")
        if idx is None:
            structural("待定项", "缺 `## 待定项` 表")
        else:
            body = section_body(lines, headings, idx)
            got = [0, 0, 0]
            rows = [l for l in body if l.strip().startswith("|")]
            for row in rows[2:]:
                cells = [c.strip() for c in row.strip().strip("|").split("|")]
                level_cell = " ".join(cells)
                if "阻塞开发" in level_cell:
                    got[0] += 1
                elif "阻塞联调" in level_cell:
                    got[1] += 1
                elif "不阻塞" in level_cell:
                    got[2] += 1
            if tuple(got) != want:
                structural("阻塞计数", f"头部写 {want}，待定项表实际 开发 {got[0]} / 联调 {got[1]} / 不阻塞 {got[2]}")

    # 5. 状态与计数
    mstate = re.search(r"^状态[：:]\s*([^\s（(]+)", head_text, re.M)
    if mstate:
        state = mstate.group(1).strip()
        if state not in STATE_VALUES:
            structural("状态", f"`{state}` 不在 {STATE_VALUES}")
        elif m:
            dev, integ = int(m.group(1)), int(m.group(2))
            if dev > 0 and state in ("可执行", "已实现", "已核对"):
                structural("状态", f"还有 {dev} 个阻塞开发项，状态不能是 `{state}`")
            if dev == 0 and integ == 0 and state == "待定补充":
                warn("状态", "阻塞项归零但状态仍为 `待定补充`")

    # 6. 资产：导出方式写 export、文件是否存在
    for name, start, end in feature_blocks:
        idx = find_section(headings, "UI 资产与图标", within=(start + 1, end))
        if idx is None:
            continue
        body = section_body(lines, headings, idx)
        for line in body:
            if not line.strip().startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            joined = " ".join(cells)
            if re.search(r"\bexport\b", joined, re.I):
                fail("资产", f"{name} 的资产表出现 `export`：展平图无 alpha、自带白/黑底，改 `rawImages` 或让设计给透明导出")
        for token in ASSET_PATH.findall("\n".join(body)):
            if args.repo and not os.path.isfile(os.path.join(args.repo, token)):
                fail("资产", f"{name} 写的资源不存在：`{token}`")
            if args.manifest:
                with open(args.manifest, encoding="utf-8") as fh:
                    listed = fh.read()
                if token not in listed:
                    fail("资产", f"`{token}` 不在 check_assets 清单里，未经透明底 / 尺寸核对")

    # 7. node 取证
    if args.nodes:
        if not os.path.isfile(args.nodes):
            fail("node 取证", f"读不到 {args.nodes}")
        else:
            with open(args.nodes, encoding="utf-8") as fh:
                known = set(NODE_ID.findall(fh.read()))
            missing = sorted(doc_nodes - known)
            if missing:
                fail("node 取证", f"文档有 {len(missing)} 个 node 不在存档：{', '.join(missing[:8])}")
            if not known:
                fail("node 取证", f"{args.nodes} 里没有任何 node-id")
    else:
        warn("node 取证", f"未传 --nodes；文档含 {len(doc_nodes)} 个 node-id，无法核对是否臆造")

    # 8. 验收黑名单 / 台账重复
    for name, start, end in feature_blocks:
        idx = find_section(headings, "验收", within=(start + 1, end))
        if idx is None:
            continue
        body = section_body(lines, headings, idx)
        for line in body:
            for word in ACCEPTANCE_BLACKLIST:
                if word in line:
                    fail("验收", f"{name} 验收句含不可验收表述 `{word}`：{line.strip()[:60]}")

    idx = find_section(headings, "问答台账")
    if idx is None:
        structural("台账", "缺 `## 问答台账` 表")
    else:
        body = section_body(lines, headings, idx)
        seen = {}
        for row in [l for l in body if l.strip().startswith("|")][2:]:
            cells = [c.strip() for c in row.strip().strip("|").split("|")]
            if len(cells) < 3:
                continue
            keyword, status = cells[1], cells[2]
            if not keyword or keyword in ("—", "-"):
                continue
            if keyword in seen:
                fail("台账", f"关键词 `{keyword}` 重复登记（先查台账再提问）")
            seen[keyword] = status
            if status not in ("已答", "已给默认", "已问待答", "作废"):
                warn("台账", f"关键词 `{keyword}` 状态 `{status}` 不在允许值内")

    idx = find_section(headings, "变更记录")
    if idx is None:
        structural("变更记录", "缺 `## 变更记录`")
    else:
        body = [l for l in section_body(lines, headings, idx) if l.strip()]
        if not body:
            structural("变更记录", "变更记录为空")

    # 输出
    for check, detail in fails:
        print(f"FAIL [{check}] {detail}")
    for check, detail in warns:
        print(f"WARN [{check}] {detail}")
    print(
        f"validator: {len(fails)} fail / {len(warns)} warn"
        + (f" | 档位 {tier or '?'}，node {len(doc_nodes)}" if tier or doc_nodes else "")
        + ("（--legacy：结构问题按 WARN 计）" if args.legacy else "")
    )
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

# Figma node 取证（存 `docs/<feature>/nodes.tsv`）

文档里出现的每个 node 都必须在存档里有行。`validate_task_doc.py --nodes` 会核对：文档写了、存档没有 = 臆造 node，FAIL。

## 为什么要存档

只读一次「父节点」，结论会停在「看起来像什么」：2026-11 购后评价踩过两次——示例图 node 属于另一帧（`8699:44309` 与真实 `8773:8439` 混用），某元素先判成「切图 icon」35 轮后核实只是 emoji 文本。存档把「一次读到的结构」变成可复核的固定证据。

## 一次 dump 的写法（Pi codemode / figma MCP）

```js
// @options: {"timeout_ms": 120000}
const ses = await tools.mcp__figma__create_session({
  fileKey: "48J3S2EHlDiYNGF0rIWOrq",
  description: "dump node tree for task doc",
});
const ids = ["8699:33586", "8699:33604", "8750:44439"]; // 文档里要用的全部 node
const code = `
const ids = ${JSON.stringify(ids)};
const rows = [];
function colorOf(fills) {
  try {
    if (!fills || !fills.length) return "";
    return fills.map((f) => {
      const c = f.color || {};
      const hex = [c.r, c.g, c.b].map((v) => Math.round((v == null ? 0 : v) * 255)
        .toString(16).padStart(2, "0")).join("");
      const a = f.opacity == null ? 1 : f.opacity;
      return "#" + hex + (a === 1 ? "" : "@" + a.toFixed(2));
    }).join(" ");
  } catch (e) { return "?"; }
}
function pathOf(n) {
  const out = [];
  let p = n;
  while (p && p.type !== "PAGE" && p.type !== "DOCUMENT") { out.unshift(p.name); p = p.parent; }
  return out.join(" / ");
}
function walk(n, depth) {
  if (depth > 6 || !n) return;
  const b = n.absoluteBoundingBox || {};
  rows.push([
    n.id, n.type, n.visible === false ? "hidden" : "visible",
    (n.name || "").replace(/[\\t\\n]/g, " "),
    pathOf(n).replace(/[\\t\\n]/g, " "),
    n.type === "TEXT" ? (n.characters || "").replace(/[\\t\\n]/g, " ").slice(0, 80) : "",
    colorOf(n.fills),
    b.width == null ? "" : Math.round(b.width * 100) / 100,
    b.height == null ? "" : Math.round(b.height * 100) / 100,
    b.x == null ? "" : Math.round(b.x * 100) / 100,
    b.y == null ? "" : Math.round(b.y * 100) / 100,
  ].join("\\t"));
  for (const c of (n.children || [])) walk(c, depth + 1);
}
for (const id of ids) {
  const n = await figma.getNodeByIdAsync(id);
  if (!n) { rows.push([id, "MISSING", "", "", "", "", "", "", "", "", ""].join("\\t")); continue; }
  walk(n, 0);
}
return rows.join("\\n");
`;
const out = await tools.mcp__figma__run_session({ sessionId: ses.sessionId, code });
return text(out);
```

把返回的文本原样落盘（制表符分隔，一行一个节点）：

```
docs/<feature>/nodes.tsv
```

表头（第一行固定写，判断脚本按列名取）：

```
id	type	visible	name	path	text	fills	w	h	x	y
```

## 落盘后必须核的三件事

1. **帧归属**：目标节点的 `path` 里出现的是本功能那版帧名。同一稿里 `8699` 与 `8773` 常是两个版本，混帧就是「组装了不存在的 UI」。
2. **可见性**：`visible=hidden` 的节点只能当参考，不得作为文案或视觉来源。
3. **文本类判断**：`type=TEXT` 且 `text` 非空 = 该元素是文本，不切图；`type=FRAME` 且无 text 才是可能的切图对象。

文档的「视觉骨架」「视觉规格」「UI 资产与图标」三张表里的每个 node，都要在 `nodes.tsv` 里有行；两个文件对不上时以存档为准并回写文档。

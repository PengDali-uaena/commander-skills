# figma-mcp-assets

本机个人技能：用 Figma MCP 把图标 / 插图落成仓库里的切图。**不进仓库、不约束团队**——别人不装 Figma MCP，用设计给的 SVG 或自己导出的图，同样合法。

触发：使用 Figma MCP、`get_design_context`、`download_assets`、`implement design from Figma`、design-to-code 落图标 / 插图 / 示例图时。

## 何时用

- 会话里能用 figma MCP 工具（`mcp__figma` / `download_assets`），且这轮要落的是图（不是写文档、不是改布局）。
- 只写 task 文档、不落切图：走 `prd-to-task`，本技能只提供它的资源 workflow 细则。
- 没有 MCP：直接结束，让设计给文件或退化成「待定（缺切图）」，不自己抠图。

## 前提

- figma MCP 可用（`mcp__figma__create_session` / `run_session`，或宿主自带的 figma 工具）。
- `oxipng` 已装（`brew install oxipng`），由 `scripts/optimize_png.sh` 调用。
- PNG 复核用 `{{SKILLS_ROOT}}prd-to-task/scripts/check_assets.sh`（同机已装）。

## 策略

| 项 | 策略 |
|----|------|
| 位图倍率 | 一律 `defaultScale: 3` |
| 格式 | 比较 PNG@3x 与 SVG 的 `sizeBytes`，**只比体积**，小者胜（平局取 SVG） |
| PNG 来源 | `rawImages` 里的 @3x 原件（保留 alpha）；**禁止**直接 curl `export`（展平图，`hasAlpha: no`，自带白底 / 黑底） |
| 整张截图类节点 | 示例照片、整卡预览这类节点根上就不透明：`rawImages` 与 `export` 都不透明。清单标 `opaque`，代码里用圆角容器 clip，不许当透明切图肉眼验收 |
| SVG | 直接下载，不压缩、不转 PNG |
| 压缩 | 仅 PNG、仅无损：`scripts/optimize_png.sh`，体积不得变大 |
| 闸门 | 落盘后跑 `check_assets.sh`，`FAIL` 不许进仓库 |

## 流程

### 1. 按节点收集候选

- 每个**独立图标 / 步骤圆标**单独 `nodeId`，不要整张卡片 export 代替多图标。
- 一次 dump 节点结构存 `docs/<feature>/nodes.tsv`（见 `{{SKILLS_ROOT}}prd-to-task/references/figma-node-dump.md`）：确认 `type=TEXT` 的不当图标切、`visible=hidden` 的当参考、父链属于这版帧。
- 对每个节点调用：

```text
download_assets { fileKey, nodeId, defaultScale: 3 }
```

记录：`export` → PNG@3x URL + `sizeBytes`（只比价）；`svgAssets[0]` → SVG URL + `sizeBytes`；`rawImages[]` → 真正的 PNG 候选（按 `format` 取扩展名，选带 alpha 且像素最大的一张）。

### 2. 选型并下载

- `export.sizeBytes <= svg.sizeBytes` → 取 **PNG**：下载 `rawImages` 里选定的那张存为 `{name}.png`；像素大于逻辑尺寸 ×3 时 `sips -z <高> <宽>` 缩到 @3x，不得放大。
- 否则 → 取 **SVG**：下载存为 `{name}.svg`，不压缩。
- 路径：`assets/images/<feature>/...`；**子目录须在 `pubspec.yaml` 单独声明**（只写 `assets/images/order/` 不包含子文件夹）。

### 3. 无损压缩（仅 PNG）

```bash
{{SKILL_DIR}}scripts/optimize_png.sh path/to/file.png
{{SKILL_DIR}}scripts/optimize_png.sh assets/images/order/refund_process/   # 目录
```

压缩后体积变大时会保留原文件。

### 4. 闸门（必须跑）

写清单（路径 / 逻辑宽 / 逻辑高 / `alpha` 或 `opaque`），然后：

```bash
bash {{SKILLS_ROOT}}prd-to-task/scripts/check_assets.sh --repo <仓库根> <清单>
```

- `RGBA + 有透明像素 + 像素 = 逻辑×3` 才算过；输出 `无 alpha 通道 = export 展平图` 时不许落盘。
- 把输出贴进回复（落盘轮次的三行硬证据之一），不写「已压缩」「透明底」这类形容词。

### 5. Flutter 落码约定

- 尺寸 `.cw`、字号 `.csp`（`narrow_content_adaptive.dart`，`checkout_adaptive.dart` 是其 re-export）。
- 逻辑尺寸 → 展示 `L.cw`；资源始终是 `3L` 像素。
- 按扩展名 `Image.asset` / `SvgPicture.asset`。
- 交付前把 node 导出图与真机截图并排看一次：顶栏 / 状态栏底色、文案是否被省略号截断、缩略图逻辑尺寸是否等于稿面。

## download_assets 字段

| 字段 | 含义 |
|------|------|
| `export` | 整节点栅格导出；`defaultScale: 3` 时为 @3x PNG。**只用来比价，不当透明切图** |
| `export.sizeBytes` | 比价用 |
| `svgAssets[]` | 矢量层 SVG，直接下载不压缩 |
| `rawImages[]` | 位图填充原图（带 alpha），按 `format` 取扩展名、选最大像素那张再 `sips -z` 到 @3x |

`defaultFormat` / `defaultScale` 只在明确要其他格式或倍率时覆盖；默认 **scale=3**。

## 透明底与物理像素

- `export` 的 PNG 多为 RGB、无 alpha，图层被压成不透明底（白底 / 黑底），不能当透明切图。
- `rawImages` 是透明 PNG 的正路；`svgAssets` 根节点多为 `fill="none"`，比体积不输时优先。
- 两者都拿不到透明底（节点无 `rawImages` 且 `export` `hasAlpha: no`）→ 让设计给透明导出，不自己抠图。
- 设计逻辑 `L` pt → PNG 约 `3L` px；`hasAlpha` 只能证明通道存在，**有没有真透明像素**看闸门脚本。

## 屏幕适配

- 窄内容页（`maxWidth: 600`）：`narrowContentDesignWidth = 375`，`NarrowContentAdaptiveNum.cw` / `NarrowContentAdaptiveTextNum.csp`。
- 详见当前仓库 `.agents/rules/screen-adaptation.md`（若存在）。

## 资源登记

自己踩过的坑与已落盘的资源登记在 `references/examples.md`：一行一个资源（本地文件 / nodeId / 选用 / 说明）。新落的切图追加一行，写明实测结论（`hasAlpha`、像素、角像素、体积），不写「可用」「正常」这类形容词。

## 常见错误

- 未传 `defaultScale: 3` → 1x 位图，高 DPR 发糊。
- 直接 curl `export` 当 PNG → 展平图无 alpha，白底 / 黑底混进 UI（评价页示例图就是这么翻车的：RGB 462×442、角 `#1e1e1e`）。
- 只跑 `sips -g hasAlpha` 就验收 → 通道存在但全不透明的 RGBA 同样会糊上一层底，必须跑闸门。
- 对 SVG 跑 oxipng / 转 PNG → 无意义，脚本只处理 `.png`。
- 把「整张截图」当透明切图 → 稿面底色跟着进 UI，只能 `opaque` + `clip` 圆角。

## 可见回复

- 落盘轮次给三行硬证据：选了哪些资源（node + 体积比）、`check_assets.sh` 输出、落盘路径。
- 不写形容词（「已优化」「透明底没问题」），只给实测数字。
- 没有要落的图就一句话收尾，不解释流程。

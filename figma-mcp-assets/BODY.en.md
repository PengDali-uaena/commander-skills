# figma-mcp-assets

A local, personal skill: land icons / illustrations as repo assets through Figma MCP. **Not tracked in any repo and never imposed on the team** — a colleague without Figma MCP who uses design-provided SVGs or exports images their own way is equally fine.

Triggers: using Figma MCP, `get_design_context`, `download_assets`, `implement design from Figma`, design-to-code when landing icons / illustrations / example images.

## When to use

- The session has figma MCP tools (`mcp__figma` / `download_assets`) and this turn lands images (not writing a document, not changing layout).
- Writing only a task document without landing assets: use `prd-to-task`; this skill only supplies the asset workflow detail.
- No MCP: stop here — ask design for the file, or record `pending (missing asset)`; never trace the image yourself.

## Prerequisites

- figma MCP available (`mcp__figma__create_session` / `run_session`, or the host's own figma tools).
- `oxipng` installed (`brew install oxipng`), used by `scripts/optimize_png.sh`.
- PNG verification uses `{{SKILLS_ROOT}}prd-to-task/scripts/check_assets.sh` (installed on the same machine).

## Policy

| Item | Policy |
|------|--------|
| Bitmap scale | always `defaultScale: 3` |
| Format | compare `sizeBytes` of PNG@3x vs SVG, **bytes only**, smaller wins (SVG on a tie) |
| PNG source | the @3x original from `rawImages` (alpha preserved); **never** curl `export` directly (flattened, `hasAlpha: no`, white or black baked in) |
| Whole-screenshot nodes | example photos and full-card previews are opaque at the node level: neither `rawImages` nor `export` is transparent. Record `opaque` in the manifest and clip the radius in code; never eyeball it as a transparent asset |
| SVG | download as is, no compression, no PNG conversion |
| Compression | PNG only, lossless only: `scripts/optimize_png.sh`; the file must not grow |
| Gate | run `check_assets.sh` after landing; a `FAIL` never enters the repo |

## Workflow

### 1. Collect candidates per node

- One `nodeId` per **independent icon / step badge**; never export a whole card in place of several icons.
- Dump the node structure once into `docs/<feature>/nodes.tsv` (see `{{SKILLS_ROOT}}prd-to-task/references/figma-node-dump.md`): `type=TEXT` nodes are copy (never sliced), `visible=hidden` is reference only, and the parent chain must belong to this design version.
- For each node call:

```text
download_assets { fileKey, nodeId, defaultScale: 3 }
```

Record: `export` → PNG@3x URL + `sizeBytes` (price comparison only); `svgAssets[0]` → SVG URL + `sizeBytes`; `rawImages[]` → the real PNG candidates (pick by `format`, largest pixel size with alpha).

### 2. Choose and download

- `export.sizeBytes <= svg.sizeBytes` → take **PNG**: download the chosen `rawImages` entry as `{name}.png`; when its pixels exceed logical size ×3, `sips -z <h> <w>` down to @3x — never upscale.
- Otherwise → take **SVG**: save `{name}.svg`, no compression.
- Path: `assets/images/<feature>/...`; **subdirectories must be declared separately in `pubspec.yaml`** (writing `assets/images/order/` does not include subfolders).

### 3. Lossless compression (PNG only)

```bash
{{SKILL_DIR}}scripts/optimize_png.sh path/to/file.png
{{SKILL_DIR}}scripts/optimize_png.sh assets/images/order/refund_process/   # directory
```

The original is kept when compression would grow the file.

### 4. The gate (mandatory)

Write a manifest (path / logical width / logical height / `alpha` or `opaque`), then:

```bash
bash {{SKILLS_ROOT}}prd-to-task/scripts/check_assets.sh --repo <repo root> <manifest>
```

- `RGBA + real transparent pixels + size = logical × 3` is the only pass; `no alpha channel = flattened export` must not land.
- Paste the output into the reply (one of the three hard evidence lines in a landing round); never write adjectives like "optimized" or "transparent ok".

### 5. Flutter conventions

- Sizes `.cw`, type `.csp` (`narrow_content_adaptive.dart`; `checkout_adaptive.dart` re-exports it).
- Logical size → display `L.cw`; assets are always `3L` pixels.
- Pick `Image.asset` / `SvgPicture.asset` by extension.
- Before delivering, put the node export and the device screenshot side by side once: app bar / status bar fill, whether copy is cut with an ellipsis, whether thumbnail logical size matches the design.

## download_assets fields

| Field | Meaning |
|-------|---------|
| `export` | whole-node raster export; @3x PNG at `defaultScale: 3`. **Price comparison only, never a transparent asset** |
| `export.sizeBytes` | for comparison |
| `svgAssets[]` | vector SVG; download as is, no compression |
| `rawImages[]` | bitmap fill originals (with alpha); pick by `format`, largest pixels, then `sips -z` to @3x |

Override `defaultFormat` / `defaultScale` only when a different format or scale is explicitly required; the default is **scale=3**.

## Transparency and physical pixels

- `export` PNGs are usually RGB without alpha — layers flattened onto an opaque fill (white or black), unusable as transparent assets.
- `rawImages` is the path to transparent PNGs; `svgAssets` roots are usually `fill="none"` and win on a tie.
- When neither yields transparency (no `rawImages` and `export` `hasAlpha: no`) → ask design for a transparent export; never trace it yourself.
- Design `L` pt → PNG about `3L` px; `hasAlpha` only proves the channel exists — whether any pixel is actually transparent is what the gate checks.

## Screen adaptation

- Narrow content pages (`maxWidth: 600`): `narrowContentDesignWidth = 375`, `NarrowContentAdaptiveNum.cw` / `NarrowContentAdaptiveTextNum.csp`.
- See `.agents/rules/screen-adaptation.md` in the current repo when it exists.

## Asset registry

Assets already landed and the traps already hit live in `references/examples.md`: one row per asset (local file / nodeId / choice / note). Append a row for every new asset with measured facts (`hasAlpha`, pixels, corner pixels, bytes) — never "usable" or "fine".

## Common mistakes

- Omitting `defaultScale: 3` → 1x bitmaps, blurry on high DPR.
- Curling `export` as PNG → flattened, no alpha, white or black bleeding into the UI (the review page's example images did exactly this: RGB 462×442, corner `#1e1e1e`).
- Accepting on `sips -g hasAlpha` alone → an RGBA image that is fully opaque still lays a background; run the gate.
- Running oxipng on SVG or converting it to PNG → meaningless, the script only handles `.png`.
- Treating a whole screenshot as a transparent asset → the design's background comes along; record `opaque` and clip the radius.

## Visible reply

- A landing round gives three hard evidence lines: which assets (node + byte comparison), the `check_assets.sh` output, and the landing paths.
- No adjectives ("optimized", "transparent is fine") — measured numbers only.
- With nothing to land, close in one line instead of explaining the workflow.

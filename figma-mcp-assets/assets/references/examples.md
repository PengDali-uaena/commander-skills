# 示例：订单详情退款进度卡

`fileKey`: `48J3S2EHlDiYNGF0rIWOrq`

| 本地文件 | Figma nodeId | 选用 | 说明 |
|----------|--------------|------|------|
| `step_applied_done.svg` | `4411:27902` | SVG | MCP PNG 无透明通道 |
| `step_processing_active.svg` | `4411:27876` | SVG | 同上 |
| `step_processing_inactive.svg` | `4411:27857` | SVG | 同上 |
| `step_refunded_inactive.svg` | `4411:27884` | SVG | 同上 |
| `step_refunded_active.svg` | `4411:27936` | SVG | 同上 |
| `urgent_bell.svg` | `4411:27988` | SVG | 同上 |
| `step_check.svg` | `4411:27899` | SVG | 比价更小 |
| `urgent_requested_check.svg` | `4411:28046` | SVG | 比价更小 |

展示尺寸（逻辑 pt）：步骤圆 `40.cw`，小勾 `9×6.5.cw`，铃铛 `13×13.5.cw`。

代码：`lib/features/order/presentation/widgets/order_detail_refund_process_card.dart`

## 示例：购后评价 v2 五档表情（透明 @3x PNG）

`fileKey`: `48J3S2EHlDiYNGF0rIWOrq`

| 本地文件 | Figma nodeId | 选用 | 说明 |
|----------|--------------|------|------|
| `level_*_….png` | `8699:33609` … `33625` | **rawImages 原件** | **禁止** curl `export`（`hasAlpha: no`、白底）；取 `rawImages` 中较小张 RGBA，再 `sips -z 110 116` 到 @3x，最后 `optimize_png.sh` |

代码：`lib/features/order/presentation/utils/order_review_v2_rating_level.dart`

## 示例：购后评价 v2 照片示例缩略图

`fileKey`: `48J3S2EHlDiYNGF0rIWOrq`

| 本地文件 | Figma nodeId | 选用 | 说明 |
|----------|--------------|------|------|
| `example_1.png` | `8773:8439` | **export @3x** | 帧 `评论2.0 / Example photo`；2026-11-19 实测：`export` 落盘为 **RGB 462×442、`hasAlpha: no`、角像素 `#1e1e1e`**（展平图，稿面底色一起带出来）。该节点是整张示例截图，透明底不存在，**只能按 `opaque` 验收**：容器 `ClipRRect` 削圆角 + 尺寸 154×147.cw，不许当透明切图用 |
| `example_2.png` | `8773:8443` | **export @3x** | 同上（`hasAlpha: no`、角 `#1e1e1e`） |

逻辑展示约 `154×147.cw`；落盘路径 `assets/images/order/review/examples/`。清单登记：`examples/example_1.png 153.95 147.25 opaque`、`examples/example_2.png 153.95 147.25 opaque`——`opaque` 行不算通过透明底检查，靠代码 clip 圆角兜住稿面底色；若设计后续给透明导出，再改回 `alpha`。

代码：`lib/features/order/presentation/pages/order_review_v2_page.dart`

## 示例：售后选择弹窗（Warranty / Refund）

`fileKey`: `48J3S2EHlDiYNGF0rIWOrq` · frame `4544:94`

纯文案按钮，无独立图标资源。左 `4537:12934` Refund（`#F3F3F3` + 描边 `#E7EBF3`），右 `4544:118` Warranty（`#1F2937` 白字）；`showBasePopup`。

代码：`lib/features/order/presentation/popup/order_after_sales_service_popup.dart`

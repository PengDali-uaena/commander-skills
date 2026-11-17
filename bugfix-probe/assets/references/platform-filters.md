# 平台筛选格式

只输出实际要抓的平台。用户点了名就只给该平台。没点名时：仓库明显只有 Web 就给 Web；明显只有 Apple 就给 iOS；否则 Android 和 iOS 都给。不编造 subsystem 或 category。

- Android 一行。主 Tag 和本轮 phase 用 `|` 连起来，`|` 左右没有空格。`|` 表示或。这行用于 logcat 搜索框，也是 `adb logcat -e` 的正则。
- iOS 每个要搜的字符串单独一行，至少一行主 Tag。phase 和 Tag 总会出现在同一行时，不要再拆 phase。用户本条说明 iOS 已打开 Regex 时，改为一行 `- iOS Regex：`，用 `|` 连接，不再拆开。
- Web 与 iOS 相同，前缀是 `- Web：`。浏览器控制台按子串匹配。

筛选里的每个 token 必须和代码里的字面量一致。

## 示例

示例只说明形状。Tag、token、路径以当前仓库代码为准。

```
- 阶段性结论：列表为空，读代码像是回调早于订阅，日志还没证实。
- Android：Probe/Inbox|phase_subscribe|phase_callback
- iOS：Probe/Inbox
- 操作路径：杀进程冷启进列表，停 10 秒，把筛选结果贴回来。
- 改动：InboxController 订阅前后各一条 debug。
- Tag：Probe/Inbox
```

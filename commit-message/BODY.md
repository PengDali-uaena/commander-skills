# commit-message

根据对话里和这次提交有关的部分，写一行英文提交说明。不读工作区，不跑 `git diff`、`git status`、`git log`，不打开文件来编这句话。不要把整段聊天缩成这句，没参与这次改动的话题不写进去。

## 格式

整行就是：

```
type(module): description
```

type 外面不要再加括号。

- `type` 只从这 8 个里选：

| type | 用于 |
|---|---|
| `feat` | 新增功能、入口、能力 |
| `fix` | 修 bug、修回归、修异常表现 |
| `refactor` | 行为不变，换结构 / 分层 / 命名 |
| `opt` | 行为不变，换实现让体验变好；说不清数字的优化都算这里 |
| `perf` | 有可量化收益的性能优化：耗时、包体、内存 |
| `docs` | 文档、issue、方案记录 |
| `style` | 只动 CSS / 格式 / 文案，无逻辑变化 |
| `chore` | 配置、日志、依赖、构建 / CI 脚本、临时脚手架 |

- 混了多种：按用户能感知的最大变化选，`feat` > `fix` > `refactor` > `opt` / `perf` > `docs` > `style` > `chore`。`opt` 与 `perf` 只差在有没有量化收益。
- 对话里用户已经用了别的 type 时，沿用那个词，不另造；`feature` 归 `feat`，`bugfix` 归 `fix`，`patch` 不再使用。
- `module` 是这次改动的模块，用对话里的叫法写成英文短词。涉及多个模块时写它们的共性，不并列模块名。
- `description` 一句英文，只说改动本身。不加句号，不写第二句。

对话里看不出 type 或 module：只问一个问题，不猜，不因此去读仓库。

## 可见回复

只有这一行，不用代码围栏，不加引号，前后不加说明。

```
fix(live-drawer): keep the native player when a transparent popup covers the home page
```

示例只说明形状。type、module、description 必须来自当前对话。

用户同条明确要求执行提交：用这一行作为 message 再提交。仍然不根据工作区改写这句。不 push，不使用 `--no-verify`。

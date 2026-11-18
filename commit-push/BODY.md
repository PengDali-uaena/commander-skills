# commit-push

先把提交说明要出来，再用它提交并推送。说明取自 `commit-message`：按 `{{SKILLS_ROOT}}commit-message/SKILL.md` 写一行 `type(module): description`，原样当 `-m` 参数，不改写、不按工作区重编。本轮不改代码，不为过 hook 去修代码。

## 顺序

1. **取说明**。看不出 type 或 module → 只问一句就停，不提交。
2. **提交前看清三件事**（不写进回复）。
   - `git status --porcelain` 为空 → 停，报「没有可提交的改动」，不造空提交。
   - 当前分支是 `dev` / `release` / `main` / `master`，或 detached HEAD → 停，问要提交到哪条分支。不替用户建分支，那是 `branch-create`。
   - 暂存只收本次对话改的文件，按路径逐个 `git add <path>`。有与本次无关的改动（别的话题、未跟踪文件）→ 列出来问一句，不用 `git add -A`、`git add .`。
3. **提交**：`git commit -m "<这一行>"`。不加 `--no-verify`、`--no-gpg-sign`；`--amend` 只在用户明确点名且该提交未推送时用。
   - hook 报错、hook 改了文件、签名失败 → 停，把原文给用户；不重试、不绕过、不改代码去迎合 hook。
4. **推送**：`git push`；当前分支没有上游 → `git push -u origin <当前分支>`。
   - 只推当前分支到同名远端分支。不 force、不 `--force-with-lease`、不删远端分支、不推别的分支。
   - 被拒（non-fast-forward、要先拉取）→ 停，给原文；不自行 rebase、merge 或 force。
   - 无权限、远端拒绝 → 停，给原文。

## 确认

本条已要求「提交 / 提交并推送」→ 直接把第 1～4 步做完。只要说明、没说要提交 → 只给那一行，交回 `commit-message`。

出现下面任一情况先停，只问一句：暂存里混了无关改动、当前分支是集成分支、需要 force、要推的是 `dev` / `release` / `main`。问完即停。

## 可见回复

字段块：每行以 `- ` 开头，字段名加粗后接全角冒号，组内不空行，不用代码围栏，块外不加首句和总结段。

成功时：

```
- **提交**：type(module): description
- **文件**：<进暂存的路径，多个连续多行>
- **推送**：<分支> → origin/<分支>
```

失败时只写做到的那几步，再接失败字段：

```
- **提交**：type(module): description
- **失败**：<哪一步> `git ...`
- **输出**：<报错原文第一行>
- **待确认**：<换分支 / 先拉取 / 改 hook，选哪个>
```

只问一句时只出一行：`- **待确认**：<问题>`。

## 禁止

- 不改那行说明去迎合工作区，不为过 hook 改代码或删断言。
- 不提交不属于本次改动的内容，不 `--no-verify`，不 force，不 `git reset --hard`。
- 不推 `dev` / `release` / `main`，不建分支（`branch-create`），不合并（`branch-merge`），不顺手改代码。

# branch-create

从 dev 或 release 开一个新分支并切过去。只建分支和切换，不改代码、不提交、不 push。

## 何时用

- 用户要为某个目的开新分支，并从 dev 或 release 起。
- 给已有分支改名、切到已有分支、只改代码：不适用。
- 建 worktree：不适用。那是仓库 skill `git-worktree-creator`（用户点名，或产物就是 worktree 时）。

## 先判断（不写进回复）

- **基线**：默认 `origin/dev`。只有 `hotfix`（线上紧急修复）从 `origin/release` 起。用户说「两边都要」或改动要同时进下个版本 → 双基线。
- **命名**：`type/<version>_<branch_name>`。例如 `feature/1.19.2_add-im-topcard`、`hotfix/1.19.1_fix-login-crash`。
- **type**：按目的选一个，不叠两个。仓库已有别的前缀就沿用。
  - `feature`：新功能、需求、交互调整
  - `bugfix`：缺陷修复（在 dev 上验证）
  - `hotfix`：线上紧急修复（从 release 起）
  - `refactor`：不改行为的重构、拆文件
  - `perf`：性能优化（首帧、卡顿、包体积）
  - `chore`：依赖、构建、配置、脚本、CI
  - `docs`：文档、注释、README
  - `test`：测试与用例
  - `experiment`：A/B 实验、灰度开关
  - 目的含糊时按影响面选一个，不新造 type。没有合适项就用 `feature`（dev）或 `hotfix`（release）。
- **version**：取基线 ref 的版本，不读工作区。Flutter：`git show origin/<base>:pubspec.yaml` 里 `version: 1.19.2+34` → `1.19.2`。Web：`package.json` 的 `version`。取不到时用 `git describe --tags --abbrev=0 origin/<base>` 去掉 `v`。仍没有就问一句，不编。版本只留数字和点，不带 `v`、`+build`。
- **branch_name**：把用户目的里的业务词翻成英文 kebab-case，3～5 个词，全小写。不带人名、日期、工单号。目的太泛（「优化一下」）→ 只问一句要改什么。
- 仓库没有 `dev` / `release`（可能是 `develop` / `main`）：列 `git branch -r`，问一句，不猜。
- 同名分支已存在：加 `-2`，或问是否复用。不覆盖。

## 创建前检查

1. 在目标仓库根目录执行。用户给了路径先 cd。当前目录不是 git 仓库 → 停，问路径。
2. `git status --porcelain`：有未提交改动 → 停，问「stash / 先提交 / 带过去」。不自动 stash，不自动提交。
3. `git fetch origin --prune`。基线用远端，不用本地 dev/release。fetch 失败就用现有 `origin/<base>`，并写明可能不是最新。
4. 远端基线确认存在再建。

## 创建

必须带 `--no-track`。不带的话 upstream 指向 dev/release，之后 `git push` 会推到基线。不 `-f`、不 `-B`、不 push、不设 upstream、不 commit。

```bash
git switch --no-track -c feature/<version>_<slug> origin/dev
git switch --no-track -c hotfix/<version>_<slug> origin/release
```

### 双基线

用户明确要「dev 和 release 都建」才建两个。没说双开就只建一个。

dev 侧用目的对应的 type（缺陷用 `bugfix`），release 侧固定 `hotfix`。两边各自取基线版本，版本号不同也不强行统一。默认切到 hotfix。用户点名停哪边就停哪边。

```bash
git branch bugfix/<dev_version>_<slug> origin/dev
git switch --no-track -c hotfix/<release_version>_<slug> origin/release
```

## 确认

仓库规则要求建分支先询问时（例如仓库有自己的分支权限表），先给方案再建。用户本条已说「直接建 / 不用问」才跳过确认。没确认不建。

## 可见回复

只有下面这些行，按 commander「字段块版式」：都以 `- ` 开头，字段名加粗，字段之间不空行，不用代码围栏，块外不加文字。

建之前：

```
- **分支**：feature/<version>_<slug>
- **基线**：origin/dev
- **待确认**：建吗
```

建完：

```
- **分支**：feature/<version>_<slug>
- **基线**：origin/dev
- **状态**：已创建并切换
```

双基线：`- **分支**：` 写两行，连续不空行，再加 `- **落点**：<已切换到哪边>`。失败只写 `- **失败**：` 加命令与错误摘要，不猜原因。

## 禁止

- 不在 dev / release 上直接提交，不删分支，不 force。
- 工作区不干净不硬切。用户没确认不建。

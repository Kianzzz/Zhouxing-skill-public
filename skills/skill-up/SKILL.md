---
name: skill-up
description: 技能管理工具。查看、删除、迭代和备份 Claude Code 的所有 skill。触发场景：(1) 用户说"管理技能"、"查看skill"、"列出技能" (2) 用户想删除或更新某个 skill (3) 用户想同步 skill 到 Git 仓库备份。
---

# Skill Up - 技能管理工具

管理 Claude Code 的所有 skill：查看清单、删除、迭代更新、Git 版本备份。

## 启动流程

skill-up 启动时自动执行以下步骤：

### 1. 扫描所有 skill

运行扫描脚本获取 skill 列表：

```bash
python3 scripts/scan_skills.py --project-path "<项目根目录>"
```

### 2. 展示 skill 清单

以表格形式展示所有 skill。**注意**：需读取每个 skill 的 SKILL.md 内容，提取功能摘要和关联引用信息。

| 序号 | 名称 | 功能 | 描述 | 关联与引用 | 层级 |
|------|------|------|------|------------|------|
| 1 | skill-up | 技能管理 | 查看、删除、迭代... | 调用 skill-creator；读取 .skill-up.json；同步到 Git 仓库 /Users/relax/Zhouxing-skill | 项目 |
| 2 | nanobanana-illustrator | 文章自动配图 | 为文章生成配图... | 调用 Nanobanana API；图片保存到统一目录；读取用户 Markdown 文件 | 项目 |

**列说明**：
- **功能**：简短几个字概括 skill 的核心用途
- **描述**：frontmatter 中的 description（截取前30字）
- **关联与引用**：读取 SKILL.md 后提取以下信息（有哪些写哪些，没有就写「-」）：
  - 调用了哪些**外部 API**（如 Nanobanana API、Chrome DevTools）
  - 依赖了哪些**其他 skill**（如 skill-creator）
  - 需要**读取的文件/配置**（如 .skill-up.json、用户的 Markdown 文件）
  - **输出保存路径**（如图片保存目录、Git 仓库路径）
- **层级**：`项目`（位于 `.claude/skills/`）或 `全局`（位于 `~/.claude/skills/`）

### 3. 检查 Git 同步状态

如果已配置 Git 仓库（见 [config.md](references/config.md)）：
1. 读取 `.skill-up.json` 配置
2. 对比本地 skill 与仓库版本
3. 自动同步有变更的 skill
4. 在表格中标注同步状态

如果未配置，询问用户是否需要配置 Git 备份。

## 操作指令

展示清单后，用户可执行以下操作：

### 删除 skill

用户说：「删除 3」或「删除 skill-name」

执行步骤：
1. 确认删除目标
2. 询问用户确认：「确定要删除 xxx 吗？此操作不可恢复。」
3. 用户确认后，删除 skill 目录
4. 如已配置 Git，同步删除到仓库

### 迭代 skill

用户说：「迭代 2」或「更新 skill-name」

执行步骤：
1. 读取目标 skill 的 SKILL.md
2. 询问用户迭代需求
3. 调用 skill-creator 进行迭代更新
4. 更新完成后，自动同步到 Git 仓库

### 导出到公共仓库

用户说：「导出」或「公开导出」

执行步骤：
1. 读取 `.skill-up.json` 中的 `public_export` 配置
2. 如果未配置，询问用户：公共仓库路径、需要导出的 skill 列表
3. 展示即将导出的 skill 清单，以及每个 skill 的 `.exportignore` 过滤规则
4. 用户确认后，运行导出脚本：

```bash
python3 scripts/export_public.py --repo "<公共仓库路径>" --skills '<skills_json>' --global-exclude '<exclude_json>'
```

5. 展示导出结果：已导出/未变更/已过滤的文件统计

### 刷新列表

用户说：「刷新」

重新扫描并展示 skill 清单。

### 配置 Git 仓库

用户说：「配置仓库」或「设置备份」

执行步骤：
1. 询问 Git 仓库本地路径
2. 验证仓库有效性
3. 创建 `.skill-up.json` 配置文件
4. 执行首次全量同步

## Git 同步

详细配置说明见 [references/config.md](references/config.md)。

同步脚本用法：

```bash
python3 scripts/sync_git.py --repo "<仓库路径>" --skills '<skills_json>'
```

同步逻辑：
1. 对比本地与仓库的 skill 内容哈希
2. 仅同步有变更的 skill
3. 自动更新仓库 README.md（重新生成 Skill 清单表格，追加更新记录）
4. 自动提交并推送，commit 信息格式：`skill-up: 同步 xxx, yyy (2026-02-07 17:50)`

README 自动维护规则：
- 每次同步有变更时，重新生成 Skill 清单表格（序号、名称、功能、描述）
- 在「最近更新」部分追加变更记录，保留最近 10 条
- 新增或删除 skill 时，表格自动增减行

## 公共导出

将选定 skill 过滤后导出到独立的公共仓库，供他人使用。与 Git 同步（完整私有备份）互不影响。

### 与 Git 同步的区别

| | Git 同步 | 公共导出 |
|---|----------|----------|
| 目的 | 完整私有备份 | 分享给他人 |
| 范围 | 所有 skill | 用户选定的 skill |
| 过滤 | 无 | `.exportignore` + 全局排除 |
| 仓库 | `git_repo` | `public_export.git_repo` |

### 导出脚本用法

```bash
python3 scripts/export_public.py --repo "<公共仓库路径>" --skills '<skills_json>' --global-exclude '<exclude_json>'
```

导出逻辑：
1. 读取每个 skill 的 `.exportignore` 文件，过滤个人内容
2. 应用全局排除规则（`__pycache__/`、`.DS_Store` 等）
3. 仅复制通过过滤的文件到公共仓库
4. 生成面向读者的 README.md（含安装说明）
5. 自动提交并推送，commit 前缀：`skill-up(public): 导出 xxx, yyy (时间)`
6. 清理公共仓库中不再导出的 skill 目录

### `.exportignore` 文件

在 skill 目录下创建 `.exportignore` 文件，列出不对外公开的文件路径。语法类似 `.gitignore`：

```
# 注释行
references/my-voice.md
references/expression-library.md
*.secret
```

- 每行一个模式，支持 fnmatch 通配符（`*`、`?`、`[...]`）
- 路径相对于 skill 目录
- 空行和 `#` 开头的行被忽略

## 迭代改进

使用此技能后，如发现问题或有改进建议：

1. 描述遇到的具体问题或低效之处
2. 说明期望的行为或改进方向
3. 我会更新 SKILL.md 或相关资源并重新测试

持续迭代是技能优化的关键。

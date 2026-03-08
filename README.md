# Claude Code Skills

一组可复用的 Claude Code 技能（Skill），覆盖写作、Obsidian、图片生成、微信公众号等场景。

> 此仓库由 [skill-up](skills/skill-up/) 自动导出，已过滤个人配置和私有数据。

## 技能清单

| 序号 | 名称 | 描述 |
|------|------|------|
| 1 | [benchmark-monitor](skills/benchmark-monitor/) | 对标账号分析与选题监控 |
| 2 | [nanobanana-extractor](skills/nanobanana-extractor/) | 从图片逆向工程提取可复用的风格提示词 |
| 3 | [nanobanana-illustrator](skills/nanobanana-illustrator/) | 为Markdown文章自动生成配图并插入 |
| 4 | [obsidian-bases](skills/obsidian-bases/) | 创建和编辑Obsidian Bases文件 |
| 5 | [obsidian-markdown](skills/obsidian-markdown/) | 创建和编辑Obsidian风格的Markdown |
| 6 | [obsidian-plugin-dev](skills/obsidian-plugin-dev/) | Obsidian插件开发专家 |
| 7 | [skill-up](skills/skill-up/) | 技能管理工具 |
| 8 | [style-writing](skills/style-writing/) | 风格学习+内容创作一站式技能 |
| 9 | [wechat-extractor](skills/wechat-extractor/) | 从微信公众号提取文章并保存为Markdown |
| 10 | [wechat-publisher](skills/wechat-publisher/) | 批量发布Markdown文章到微信公众号 |

## 安装方式

### 方法一：手动复制

1. 将需要的 skill 文件夹复制到你的项目 `.claude/skills/` 目录下
2. 根据 skill 的 `SKILL.md` 说明进行个性化配置

### 方法二：克隆整个仓库

```bash
git clone <本仓库地址>
# 将需要的 skill 目录复制到你的项目中
cp -r skills/skill-name /path/to/your/project/.claude/skills/
```

## 注意事项

- 部分 skill 的 `references/` 目录下的个人文件已被过滤，你需要根据 SKILL.md 的说明创建自己的配置
- 每个 skill 的 SKILL.md 是核心入口文件，请先阅读了解用法
- 如果 skill 依赖外部 API（如 Gemini API），你需要自行配置 API Key

## 更新记录

- **2026-03-08** — 导出 benchmark-monitor, nanobanana-extractor, nanobanana-illustrator, obsidian-bases, obsidian-markdown, obsidian-plugin-dev, skill-up, style-writing, wechat-extractor, wechat-publisher

- **2026-03-08** — 首次导出

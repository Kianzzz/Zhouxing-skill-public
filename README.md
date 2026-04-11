# Claude Code Skills

一组可复用的 Claude Code 技能（Skill），覆盖写作、Obsidian、图片生成、微信公众号等场景。

> 此仓库由 [skill-up](skills/skill-up/) 自动导出，已过滤个人配置和私有数据。

## 技能清单

| 序号 | 名称 | 描述 |
|------|------|------|
| 1 | [benchmark-monitor](skills/benchmark-monitor/) |  |
| 2 | [content-pipeline](skills/content-pipeline/) |  |
| 3 | [web-opencli](skills/web-opencli/) |  |
| 4 | [web-search](skills/web-search/) |  |
| 5 | [wechat-extractor](skills/wechat-extractor/) |  |
| 6 | [wechat-publisher](skills/wechat-publisher/) |  |
| 7 | [writing-copilot](skills/writing-copilot/) |  |

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

- **2026-04-11** — 导出 writing-copilot, content-pipeline, web-search, wechat-publisher, benchmark-monitor, web-opencli, wechat-extractor

- **2026-03-08** — 首次导出

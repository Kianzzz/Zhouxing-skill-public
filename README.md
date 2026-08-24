# Claude Code Skills

一组可复用的 Claude Code 技能（Skill），覆盖写作、Obsidian、图片生成、微信公众号等场景。

> 此仓库由 [skill-up](skills/skill-up/) 自动导出，已过滤个人配置和私有数据。

## 技能清单

| 序号 | 名称 | 描述 |
|------|------|------|
| 1 | [writing-copilot](skills/writing-copilot/) | 写作副驾——AI出初稿、用户修正、风格沉淀的写作飞轮 |
| 2 | [content-pipeline](skills/content-pipeline/) | 全自动内容创作流水线：从需求到成稿的一站式自动化 |
| 3 | [web-search](skills/web-search/) | 通用联网搜索工具，支持多平台、多场景的智能搜索和内容提取 |
| 4 | [wechat-publisher](skills/wechat-publisher/) | 批量发布 Markdown 文章到微信公众号 |
| 5 | [benchmark-monitor](skills/benchmark-monitor/) | 对标账号分析与选题监控 |
| 6 | [web-opencli](skills/web-opencli/) | 使用 OpenCLI 浏览器自动化进行网络搜索 |
| 7 | [wechat-extractor](skills/wechat-extractor/) | 从微信公众号提取文章并保存为 Markdown |

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

### 方法三：AI安装
1. 打开skills文件夹，找到需要安装的skill
2. 复制网站链接，发给Claude code（或codex、gemini、openclaw.....）
3. 输入指令：帮我安装这个skill

## 注意事项

- 每个 skill 的 `SKILL.md` 是核心入口文件，Claude Code 通过它理解能力边界和执行流程
- 部分 skill 的个人配置文件（如写作风格、表达库）已被过滤，你需要根据 SKILL.md 的说明创建自己的
- 需要外部 API 的 skill（如 Gemini API、Pexels API）需自行申请 API Key 并配置

---

## 更新记录

- **2026-04-11** — 更新 7 个 skill

- **2026-03-08** — 首次导出

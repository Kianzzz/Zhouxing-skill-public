# Claude Code Skills

一组可复用的 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 技能（Skill），覆盖写作、Obsidian、图片生成、微信公众号等场景。

> 此仓库由 [skill-up](skills/skill-up/) 自动导出，已过滤个人配置和私有数据。

## 什么是 Skill？

Skill 是 Claude Code 的扩展能力包——一个包含 `SKILL.md` 指令文件和可选资源（参考文档、脚本、资产）的文件夹。放入项目的 `.claude/skills/` 目录后，Claude Code 会自动加载并获得对应能力。

## 安装方式

将需要的 skill 文件夹复制到你的项目 `.claude/skills/` 目录下即可：

```bash
# 克隆仓库
git clone https://github.com/Kianzzz/Zhouxing-skill-public.git

# 复制你需要的 skill
cp -r Zhouxing-skill-public/skills/obsidian-markdown /path/to/your/project/.claude/skills/
```

部分 skill 需要额外配置（如 API Key），请参考各自的 `SKILL.md` 说明。

---

## 技能清单

### 写作与内容

#### [style-writing](skills/style-writing/) — 风格学习 + 内容创作

从参考文章中深度分析写作结构档案，或基于已有结构档案 + 素材进行内容创作。支持多风格档案管理。

- **触发方式**：说「风格学习」「风格写作」「仿写」
- **核心流程**：提供参考文章 → 自动提取结构档案 → 基于档案 + 你的素材创作新内容
- **需要配置**：个人知识库文件（`references/personal-kb.md`，已过滤不含在本仓库中，需自行创建）

#### [benchmark-monitor](skills/benchmark-monitor/) — 对标账号分析与选题监控

两大功能：(A) 输入公众号名称，精读近 100 篇文章输出对标权重排序表；(B) 扫描所有对标账号近 7 天内容，通过 5 维评估筛选值得写的选题。

- **触发方式**：说「对标分析」「选题监控」
- **依赖**：需要 wechat-extractor 配合使用
- **需要配置**：`~/.claude/benchmark-monitor-config.json`

---

### 图片生成

#### [nanobanana-illustrator](skills/nanobanana-illustrator/) — 文章自动配图

为 Markdown 文章自动生成配图并插入。支持四种图片来源：AI 风格图、Pexels 真实照片、TMDB 电影剧照、信息图。基于文章内容结构自动判断配图数量和位置。

- **触发方式**：上传文章并指定风格，或说「配图」
- **支持模式**：封面 / 正文配图 / 都要
- **需要配置**：`~/.claude/nanobanana-config.json`（含 Gemini API Key）

#### [nanobanana-extractor](skills/nanobanana-extractor/) — 图片风格提取

从参考图片中逆向工程提取可复用的 AI 出图提示词。支持 6 域分类（摄影人像/摄影场景/绘画写实/绘画风格化/平面设计/通用），自动识别领域并输出结构化英文提示词。

- **触发方式**：上传插画/绘画/摄影参考图，说「提取风格」「学习图片风格」
- **输出**：可复用的英文风格提示词 `.md` 文件
- **需要配置**：`~/.claude/nanobanana-config.json`（含 Gemini API Key）

---

### Obsidian

#### [obsidian-markdown](skills/obsidian-markdown/) — Obsidian Markdown 方言支持

让 Claude Code 理解并正确编辑 Obsidian 专有语法：wikilinks (`[[]]`)、嵌入 (`![[]]`)、callouts、frontmatter 属性、标签等。

- **触发方式**：处理 Obsidian 中的 `.md` 文件时自动激活
- **无需配置**，开箱即用

#### [obsidian-bases](skills/obsidian-bases/) — Obsidian Bases 编辑

创建和编辑 Obsidian Bases（`.base` 文件），支持表格视图、卡片视图、过滤器、公式和汇总。

- **触发方式**：处理 `.base` 文件，或说「创建数据库视图」
- **无需配置**，开箱即用

#### [obsidian-plugin-dev](skills/obsidian-plugin-dev/) — Obsidian 插件开发

帮助零基础用户将模糊想法转化为完整、稳定、可用的 Obsidian 插件。从需求分析到代码交付的全流程支持。

- **触发方式**：说「开发插件」「做一个 Obsidian 插件」
- **内含**：Obsidian API 参考文档、质量检查清单、示例代码

---

### 微信公众号

#### [wechat-extractor](skills/wechat-extractor/) — 微信文章提取

从微信公众号提取文章并保存为 Markdown。三种模式：链接提取（给 URL 直接转换）、账号搜索（搜索公众号批量抓取）、阅读数据获取。

- **触发方式**：给公众号文章链接，或说「提取文章」「搜索账号」
- **需要配置**：`~/.wechat-extractor/config.json`

#### [wechat-publisher](skills/wechat-publisher/) — 微信文章发布

批量发布 Markdown 文章到微信公众号草稿箱。支持多账号管理、代理配置、CSS 主题自动匹配、图片压缩上传。

- **触发方式**：说「发布文章」「发到公众号」
- **需要配置**：`~/.claude/wechat-publisher-config.json`（含公众号 AppID/Secret）

---

### 工具

#### [skill-up](skills/skill-up/) — 技能管理工具

管理 Claude Code 的所有 skill：查看清单、删除、迭代更新、Git 版本备份、公共导出。本仓库就是由它自动导出的。

- **触发方式**：说「管理技能」「查看 skill」「同步」「导出」
- **功能**：扫描所有 skill → 展示清单表格 → 支持删除/迭代/Git 同步/公共导出

---

## 注意事项

- 每个 skill 的 `SKILL.md` 是核心入口文件，Claude Code 通过它理解能力边界和执行流程
- 部分 skill 的个人配置文件（如写作风格、表达库）已被过滤，你需要根据 SKILL.md 的说明创建自己的
- 需要外部 API 的 skill（如 Gemini API、Pexels API）需自行申请 API Key 并配置

---

## 更新记录

- **2026-03-08** — 首次导出

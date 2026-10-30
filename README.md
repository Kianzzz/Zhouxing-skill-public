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
| 8 | [zhouxing-ip-ppt](skills/zhouxing-ip-ppt/) | 品牌锚点绿 #28A85B；角色场景、真实截图与原生文字排版，输出可编辑 PPT |

## zhouxing-IP-PPT

默认采用周行品牌锚点草木绿 `#28A85B`，结合字体层级、统一间距、全身/半身/近景/多人场景及出血构图，制作带真实截图的可编辑幻灯片。支持默认插画、用户卡通 IP 和真人照片。

![默认风格参考](skills/zhouxing-ip-ppt/assets/default-style-reference.png)

- 完整复制 [`skills/zhouxing-ip-ppt`](skills/zhouxing-ip-ppt/)；以 `SKILL.md` 为入口，保留 references、scripts、assets。
- 可用于具备对应工具能力的 agent；`agents/openai.yaml` 是可忽略的 Codex 界面配置。详见 [工具适配与依赖](skills/zhouxing-ip-ppt/references/tool-adapters.md)。
- 需要参考图生图或已有素材、原生幻灯片写入和预览能力。飞书原生稿还需已授权的飞书工具；依赖和字体不会随 Skill 自动安装。
- Python 检查脚本使用标准库；Node 图片合成与字形测量使用 `@napi-rs/canvas`。默认插画由 AI 生成，仍为候选，不代表用户已认可所有生成变体。
- 本 Skill 采用 [MIT 许可](skills/zhouxing-ip-ppt/LICENSE)；设备外框衍生自 devices.css，保留其 [MIT 版权声明](skills/zhouxing-ip-ppt/assets/device-mockups/LICENSE-Devices.css.txt)、源版本和适配说明。本许可不延伸到仓库中的其他 Skill。

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

- **2026-10-30** — 开源 zhouxing-ip-ppt：锚点绿默认主题、可编辑排版与可复用样机

- **2026-04-11** — 更新 7 个 skill

- **2026-03-08** — 首次导出

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
| 8 | [zhouxing-ip-ppt](skills/zhouxing-ip-ppt/) | 角色驱动配色、媒介化动作、分层造景与原生字体设计，默认飞书 PPT |

## zhouxing-IP-PPT

默认输出可编辑的飞书原生幻灯片。按用户指定或角色识别色/衣着确定配色，只有无角色及配色输入时才采用内置草木绿 `#28A85B`。区分2D、3D与真人的动作策略，结合独立造景层、深浅背景节奏、原生展示字与清晰正文，支持真实截图与出血构图。

![无角色输入时的内置2D绿系候选参考](skills/zhouxing-ip-ppt/assets/default-style-reference.png)

- 完整复制 [`skills/zhouxing-ip-ppt`](skills/zhouxing-ip-ppt/)；以 `SKILL.md` 为入口，保留 references、scripts、assets。
- 可用于具备对应工具能力的 agent；`agents/openai.yaml` 是可忽略的 Codex 界面配置。详见 [工具适配与依赖](skills/zhouxing-ip-ppt/references/tool-adapters.md)。
- 优先复用 agent 已有的飞书 PPT 工具；缺少时引导安装官方工具并登录授权。安装阶段不生成试稿，例行依赖由 agent 在实际制作时按需准备。
- 默认流程无需 python-pptx 或 LibreOffice。仅使用内置 Node 合成/测量脚本时需要 `@napi-rs/canvas`，已有等效工具时直接复用；生图或匹配素材仍需由当前环境提供。默认插画由 AI 生成。
- 本 Skill 采用 [MIT 许可](skills/zhouxing-ip-ppt/LICENSE)；设备外框衍生自 devices.css，保留其 [MIT 版权声明](skills/zhouxing-ip-ppt/assets/device-mockups/LICENSE-Devices.css.txt)、源版本和适配说明。本许可不延伸到仓库中的其他 Skill。

### 分享安装口令

把下面这段发给支持 Skill 安装的 agent 即可：

```text
请安装或更新这个 Skill，并按它的默认流程完成必要准备：
https://github.com/Kianzzz/Zhouxing-skill-public/tree/main/skills/zhouxing-ip-ppt
默认制作飞书 PPT，优先复用你已有的飞书工具；没有时引导我安装并授权。
装好后简短告诉我如何开始即可。
```

账号登录、扫码或管理员审批仍需用户本人完成。飞书客户端供查看编辑使用；agent 自动制作还需要相应工具权限。安装本身不创建云文档，首次实际制作时按本次内容检查排版和目标预览。

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

- **2026-10-30** — 角色驱动配色、2D/3D/真人表演策略、分层造景与展示字体设计

- **2026-10-30** — 简化 zhouxing-ip-ppt 安装，默认飞书交付，复用已有工具并按需准备依赖

- **2026-10-30** — 开源 zhouxing-ip-ppt：锚点绿默认主题、可编辑排版与可复用样机

- **2026-04-11** — 更新 7 个 skill

- **2026-03-08** — 首次导出

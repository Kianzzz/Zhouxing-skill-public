---
name: content-pipeline
description: "全自动内容创作流水线：从需求到成稿的一站式自动化。串联素材收集（web-opencli + Obsidian搜索）、内容创作（writing-copilot）、配图生成（nanobanana-illustrator）三大环节，输出带配图的完整文章。触发场景：(1) 用户说'我想写一篇文章'、'写一篇文章'、'写一篇公众号文章' (2) 用户说'全自动写作'、'一键创作' (3) 用户提出完整的写作主题并希望自动化完成。IMPORTANT: 当用户在句子开头使用这些触发词时，必须使用此 skill，即使他们没有明确说'自动化'或'流水线'。"
---

# Content Pipeline - 全自动内容创作流水线

从一个写作需求到一篇带配图的完整文章，完全自动化执行。

## 核心理念

这个 skill 的设计哲学是：**用户只需要提出需求，剩下的全部自动化**。

传统的内容创作需要用户手动：
1. 搜索素材
2. 整理素材
3. 调用写作工具
4. 给文章配图
5. 整理文件

Content Pipeline 把这些步骤全部自动化，用户只需要说"我想写一篇关于XXX的文章"，就能得到一篇完整的、带配图的文章。

## 工作流程

```
用户需求
    ↓
需求分析（判断素材来源策略）
    ↓
素材收集（web-opencli / Obsidian搜索）
    ↓
素材整理（结构化整理）
    ↓
内容创作（writing-copilot）
    ↓
配图生成（nanobanana-illustrator）
    ↓
交付（输出文件路径）
```

## 首次运行配置

第一次使用此 skill 时，会自动进入配置向导，询问以下配置项并保存：

1. **Obsidian Vault 路径** - 你的 Obsidian 知识库位置（用于搜索本地笔记素材）
2. **文章长度偏好** - 选择默认文章长度：
   - 短文（800字左右）- 素材收集较少，快速成稿
   - 普通文章（1000-1500字）- 标准深度，平衡素材量
   - 深度文章（1500字以上）- 大量素材，深入分析
3. **配图类型偏好** - 选择默认配图方式：
   - 仅封面
   - 封面+正文配图
   - 不配图（仅生成文字内容）
4. **配图来源偏好**（如果选择配图）：
   - 风格图（AI 生成风格化插画）
   - 真实照片（从 Pexels 下载）
   - 电影剧照（从 TMDB 获取）
   - 信息图（AI 生成结构化信息图）
5. **配图风格名称**（如果选择风格图）- nanobanana-illustrator 的风格库中的风格名称
6. **失败处理策略** - 遇到问题时是停止还是继续

配置保存在 `~/.claude/skills/content-pipeline/config.json`，后续运行会自动读取。

**每次运行时**：询问用户"使用默认配置还是自定义本次配置？"，允许临时覆盖默认设置。

**输出位置**：文章始终输出到当前工作目录（$PWD），在哪里运行就在哪里输出。

## 执行步骤

### 阶段 1: 配置检查与需求解析

1. **检查配置文件**
   - 读取 `~/.claude/skills/content-pipeline/config.json`
   - 如果不存在，手动询问用户配置项并保存：
     * Obsidian Vault 路径（用于搜索本地笔记素材）
     * 文章长度偏好（short/normal/deep）
     * 配图类型偏好（cover_only/cover_and_content/none）
     * 配图来源偏好（style/photo/movie/infographic）
     * 配图风格名称（如果选择风格图）
     * 失败处理策略（"stop_and_report" 停止并报告，"continue" 尽力继续）
   - 如果存在但包含遗留字段 `output_strategy` 或 `keep_materials`，忽略这些字段
   - 验证配置有效性：
     * 检查 `obsidian_vault_path` 是否存在且可读
     * 如果路径无效，警告用户并询问是否更新

2. **询问本次运行配置**
   - 显示当前默认配置
   - 询问："使用默认配置还是自定义本次配置？"
   - 如果选择自定义，允许临时覆盖：
     * 文章长度（本次）
     * 配图类型（本次）
     * 配图来源（本次）

3. **解析用户需求**
   - 提取写作主题和关键词
   - 识别内容类型（科普、观点、案例分析等）
   - 根据文章长度偏好评估素材需求量：
     * 短文（800字）：2-3 个关键信息点
     * 普通文章（1000-1500字）：3-5 个关键信息点
     * 深度文章（1500字+）：5-8 个关键信息点

4. **制定素材收集策略**
   - 判断是否需要联网搜索（时效性、数据需求、案例需求）
   - 判断是否需要本地搜索（个人经验、已有笔记）
   - 生成搜索关键词列表

**决策逻辑：**
- **需要联网搜索的信号**：
  - 主题包含时间词（"2026"、"最新"、"近期"）
  - 需要数据支撑（"数据"、"报告"、"研究"）
  - 需要案例（"案例"、"实例"、"例子"）
  - 需要热点信息（"热点"、"趋势"、"动态"）
  
- **需要本地搜索的信号**：
  - 主题涉及个人经验（"我的"、"经验"、"总结"）
  - 用户的 Obsidian vault 中可能有相关笔记
  - 需要引用已有的知识体系

### 阶段 2: 素材收集（使用子 agent）

**⚠️ 重要：素材收集应使用 Agent 工具调度子 agent，避免主上下文膨胀。**

1. **创建工作目录**
   - 在当前工作目录（$PWD）下创建 `{主题简称}-{日期}/` 文件夹
   - 例如：`AI写作工具-20260409/`
   - **Why:** 输出跟随用户的工作上下文，在哪里运行就在哪里输出，避免文件分散在不同位置
   - **错误处理**：
     * 检查当前目录是否可写，如果不可写则报错并终止
     * 如果同名文件夹已存在，添加序号后缀（如 `AI写作工具-20260409-2/`）

2. **调度素材收集子 agent**
   
   使用 Agent 工具创建独立的素材收集 agent：
   
   ```
   任务：为文章"{主题}"收集素材
   
   需求：
   - 文章长度：{short/normal/deep}
   - 需要 {2-3/3-5/5-8} 个关键信息点
   
   执行步骤：
   1. 判断是否需要联网搜索（时效性、数据、案例需求）
   2. 判断是否需要本地搜索（个人经验、已有笔记）
   3. 如果需要联网搜索：
      - 优先使用 web-opencli（检测 opencli doctor）
      - 如果不可用，降级到 web-search
      - 将结果保存到 {工作目录}/素材-网络.md
   4. 如果需要本地搜索：
      - 在 {obsidian_vault_path} 中搜索相关笔记
      - 将结果保存到 {工作目录}/素材-本地.md
   5. 合并素材，生成 {工作目录}/素材汇总.md
   
   输出：素材汇总.md 文件路径
   ```
   
   **Why:** 素材收集涉及大量搜索结果和文件读取，使用子 agent 可以避免主上下文被素材内容占满，确保后续阶段有足够的上下文空间。
   
   **How to apply:** 使用 Agent 工具而不是直接执行，等待子 agent 完成后读取素材汇总文件。

3. **验证素材收集结果**
   - 读取 `{工作目录}/素材汇总.md`
   - 检查是否至少有一种素材来源成功
   - 如果素材不足：
     * 根据 `failure_strategy` 配置决定：
       - "stop_and_report"：报告失败原因并终止
       - "continue"：警告用户素材不足，但继续执行

**⚠️ 素材文件保留策略：所有素材文件（素材-网络.md、素材-本地.md、素材汇总.md）都保留在工作目录中，不删除。用户可以随时对比素材和初稿。**

### 阶段 3: 内容创作（使用子 agent）

**⚠️ 重要：内容创作应使用 Agent 工具调度 writing-copilot，避免主上下文膨胀。**

1. **调度 writing-copilot 子 agent**
   
   使用 Agent 工具创建独立的写作 agent：
   
   ```
   使用 writing-copilot skill 创作文章，自动化模式。
   
   素材文件：{工作目录}/素材汇总.md
   输出路径：{工作目录}/初稿.md
   文章长度：约 {800/1200/1800} 字
   ```
   
   **Why:** writing-copilot 的执行过程会产生大量中间内容（多个标题选项、开头选项、质检过程），使用子 agent 可以避免这些内容占用主上下文。
   
   **How to apply:** 使用 Agent 工具调度，传递 skill 名称和参数，等待子 agent 完成后读取初稿文件。不要在主上下文中直接使用 Skill 工具调用 writing-copilot。

2. **验证创作结果**
   
   读取 `{工作目录}/初稿.md`，确认文件包含：
   - 5 个标题选项（第一个已被自动选择）
   - 3 个开头选项（第一个已被自动选择）
   - 经过三层质检的正文
   - 初稿存档（HTML 注释中）
   
   如果文件不完整或质检未执行：
   - 根据 `failure_strategy` 配置决定：
     * "stop_and_report"：报告问题并终止
     * "continue"：使用现有内容继续

### 阶段 4: 配图生成（使用子 agent，可选）

**⚠️ 重要：配图生成应使用 Agent 工具调度 nanobanana-illustrator，避免主上下文膨胀。**

**根据配置决定是否执行此阶段：**
- 如果配图类型为 "none"，跳过此阶段
- 如果配图类型为 "cover_only" 或 "cover_and_content"，执行配图

1. **调度 nanobanana-illustrator 子 agent**
   
   使用 Agent 工具创建独立的配图 agent：
   
   ```
   任务：使用 nanobanana-illustrator skill 为文章配图
   
   参数：
   - 文章路径：{工作目录}/初稿.md
   - 任务类型：{cover_only 对应"仅封面"，cover_and_content 对应"封面+正文配图"}
   - 图片来源：{style/photo/movie/infographic}
   - 风格名称：{如果是 style，传递配置的风格名称}
   - 内容主题：自动检测
   - 文章长度：{short/normal/deep}（用于信息图尺寸选择）
   
   执行：
   直接调用 nanobanana-illustrator skill，传递上述参数。
   nanobanana-illustrator 会分析文章内容，判断配图位置，生成配图并插入 Markdown。
   如果图片来源是信息图，会根据文章长度选择尺寸：
   - short（≤800字）→ 3:4 竖版
   - normal/deep（>800字）→ 16:9 横版
   
   输出：更新后的初稿.md 文件路径
   ```
   
   **Why:** nanobanana-illustrator 的执行过程会产生大量中间内容（场景设计、提示词生成、API 调用结果），使用子 agent 可以避免这些内容占用主上下文。
   
   **How to apply:** 使用 Agent 工具调度，传递 skill 名称和参数（包括文章长度），等待子 agent 完成后读取更新后的文章文件。不要在主上下文中直接使用 Skill 工具调用 nanobanana-illustrator。

2. **验证配图结果**
   
   读取更新后的 `{工作目录}/初稿.md`，检查：
   - 封面图片是否已插入（如果配置要求）
   - 正文配图是否已插入（如果配置要求）
   - 图片路径是否正确
   
   如果配图失败：
   - 根据配置的 `failure_strategy` 决定：
     * "stop_and_report"：报告配图失败原因并终止
     * "continue"：保留无配图的文章，向用户报告配图失败原因

### 阶段 5: 清理与交付

1. **输出结果**
   - 向用户报告最终文件位置
   - 格式：
     ```
     ✅ 文章创作完成！
     
     工作目录：{工作目录路径}
     
     文件清单：
     - 初稿.md（最终文章，{已配图/未配图}）
     - 素材汇总.md（整理后的素材）
     - 素材-网络.md（网络搜索结果，如有）
     - 素材-本地.md（本地笔记素材，如有）
     ```

**⚠️ 素材文件保留：所有素材文件都保留在工作目录中，用户可以随时对比素材和初稿。**

## 错误处理

根据用户配置的失败处理策略：

**策略 A: 停止并报告**（默认）
- 任何环节失败立即停止
- 向用户报告失败原因和已完成的步骤
- 保留已生成的中间文件供用户检查

**策略 B: 尽力继续**（配置值："continue"）
- 素材收集失败：跳过该来源，用已有素材继续
- 配图失败：保留无配图的文章，报告配图失败原因

## 进度跟踪

使用 TaskCreate 和 TaskUpdate 跟踪每个阶段的进度：

1. 配置检查与需求解析
2. 素材收集
3. 素材整理
4. 内容创作
5. 配图生成
6. 清理与交付

每个任务在开始时标记为 `in_progress`，完成时标记为 `completed`。

## 与其他 Skill 的协作

此 skill 是一个**编排器（Orchestrator）**，它不直接执行具体任务，而是调度其他 skill：

- **web-opencli** - 负责网络素材搜索
- **writing-copilot** - 负责内容创作
- **nanobanana-illustrator** - 负责配图生成

调用这些 skill 时，使用 Skill 工具，传递明确的参数和输出路径。

## 配置文件格式

`~/.claude/skills/content-pipeline/config.json`:

```json
{
  "obsidian_vault_path": "/Users/username/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian2025",
  "article_length": "normal",
  "illustration_type": "cover_and_content",
  "illustration_source": "style",
  "illustration_style_name": "用户配图风格",
  "failure_strategy": "stop_and_report"
}
```

**字段说明**：
- `obsidian_vault_path`: Obsidian 知识库路径，用于搜索本地笔记素材
- `article_length`: 文章长度偏好（"short" 800字 / "normal" 1200字 / "deep" 1800字）
- `illustration_type`: 配图类型（"none" 不配图 / "cover_only" 仅封面 / "cover_and_content" 封面+正文）
- `illustration_source`: 配图来源（"style" 风格图 / "photo" 真实照片 / "movie" 电影剧照 / "infographic" 信息图）
- `illustration_style_name`: 配图风格名称（仅当 illustration_source 为 "style" 时需要）
- `failure_strategy`: 失败处理策略（"stop_and_report" 停止并报告 / "continue" 尽力继续）

**输出位置**：文章始终输出到当前工作目录（$PWD），不受配置文件影响。

**素材保留**：所有素材文件始终保留在工作目录中，不删除。

## 使用示例

**示例 1: 基础使用**
```
用户：我想写一篇文章，主题是"AI 写作工具如何改变内容创作行业"
```

Pipeline 会：
1. 判断需要联网搜索（行业趋势、案例）
2. 调用 web-opencli 搜索相关信息
3. 在 Obsidian 中搜索用户已有的相关笔记
4. 整理素材并调用 writing-copilot 创作
5. 调用 nanobanana-illustrator 配图
6. 输出：`AI写作工具-20260409/初稿.md`

**示例 2: 纯本地素材**
```
用户：写一篇文章，总结我这个月的读书笔记
```

Pipeline 会：
1. 判断不需要联网搜索（个人总结）
2. 在 Obsidian 中搜索本月的读书笔记
3. 整理素材并调用 writing-copilot 创作
4. 调用 nanobanana-illustrator 配图
5. 输出：`读书笔记总结-20260409/初稿.md`

## 迭代改进

使用此技能后，如发现问题或有改进建议：

1. 描述遇到的具体问题或低效之处
2. 说明期望的行为或改进方向
3. 我会更新 SKILL.md 或相关资源并重新测试

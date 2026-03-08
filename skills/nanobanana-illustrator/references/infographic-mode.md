# 信息图模式 — 详细参考

## 布局系统

### 布局选择指南

| 布局 | 关键词 | 适用内容 | 信息密度 |
|------|--------|---------|---------|
| **bento-grid** | 模块化网格 | 多维度概览、功能展示、仪表盘 | 高 |
| **timeline** | 时间线 | 发展历程、阶段演进、成长记录 | 中 |
| **funnel** | 漏斗 | 转化流程、筛选过程、层层递进 | 中 |
| **comparison** | 对比 | 两方案对比、优劣分析、前后对比 | 中 |
| **hub-spoke** | 中心辐射 | 核心概念+分支、一个中心多个维度 | 中 |
| **pyramid** | 金字塔 | 层级关系、优先级、马斯洛类结构 | 低-中 |
| **flow** | 流程 | 步骤教程、工作流、决策树 | 中 |
| **checklist** | 清单 | 要点列表、注意事项、行动清单 | 中-高 |
| **iceberg** | 冰山 | 表象vs本质、可见vs隐藏、二层对比 | 中 |
| **tree** | 树形 | 分类体系、组织架构、知识图谱 | 高 |

### 自动推荐规则

根据文章内容自动推荐 2-3 个布局候选：

```
内容特征 → 推荐布局（按优先级）

步骤/流程/教程 → flow > timeline > checklist
对比/选择/优劣 → comparison > bento-grid
多维度/概览/总结 → bento-grid > hub-spoke
层级/优先级/重要性 → pyramid > iceberg
时间线/历程/阶段 → timeline > flow
核心+分支/一对多 → hub-spoke > tree
清单/要点/注意事项 → checklist > bento-grid
分类/体系/结构 → tree > pyramid
表面vs深层/冰山 → iceberg > pyramid
转化/筛选/递减 → funnel > pyramid
```

---

## 视觉风格系统

信息图有两种风格来源：

### A. 内置信息图风格（独立使用时）

| 风格 | 描述 | 适用场景 |
|------|------|---------|
| **clean-modern** | 干净现代，扁平图标，无衬线字体，充足留白 | 商务、科技、教程 |
| **warm-handdrawn** | 手绘感，圆润线条，暖色调，纸质纹理 | 生活、成长、情感 |
| **bold-graphic** | 大色块，强对比，粗字体，冲击力强 | 观点、数据、营销 |
| **FengBo-Style** | 靛蓝底(#1661ab)+白色文字+暖金标签+浅天蓝描述+可爱白色简笔漫画小人 | 风伯IP专属风格，适用所有教程/科技类 |
| **notebook** | 笔记本风格，手写字体，网格背景，荧光笔高亮 | 学习笔记、知识整理 |
| **morandi-journal** | 莫兰迪色系，手账感，纸胶带装饰，温柔质感 | 生活方式、小红书风 |

### B. 复用已有风格库（与文章配图统一时）

当信息图需要与同一篇文章的其他配图（场景图）保持视觉统一时：
1. 从用户风格库中读取对应风格文件
2. 提取配色方案、线条质感等视觉元素
3. 将这些元素应用到信息图模板中
4. 保持信息图的排版结构不变，只替换视觉风格

---

## 内容结构化

### 从文章提取信息图内容

信息图的内容必须从文章原文中准确提取，**禁止改写或概括**。

**提取流程：**

```
1. 通读全文，识别适合做信息图的段落
   适合的内容：
   - 列举的要点/方法/步骤（3-8个）
   - 对比/对照内容
   - 数据/统计
   - 分类/层级结构
   - 流程/时间线

2. 提取结构化内容
   对每个信息点提取：
   - 标题/标签（简短，≤8字）
   - 正文（原文摘取，≤30字/点）
   - 图标关键词（用于匹配图标，英文）
   - 层级关系（平级/从属/递进）

3. 确定信息图标题
   - 从文章标题或该段落标题中提炼
   - ≤15字，概括信息图核心主题

4. 确定副标题（可选）
   - 补充说明或来源标注
   - ≤20字
```

### 文字规范

**硬性要求：**
- 所有文字必须使用中文（除非用户要求其他语言）
- 标题：≤15字，一行为佳
- 要点标签：≤8字
- 要点正文：≤30字/点
- 总文字量控制：单张信息图文字总量 ≤ 200字
- 文字层级清晰：标题 > 要点标签 > 正文 > 注释
- **IP 标签（固定）**：每张信息图左下角或右下角（选空位多的一边）必须包含 `@FengBo` 标签，白色小字，不遮挡主内容。此标签为固定要素，不可省略

**文字精准度检查清单：**
- [ ] 每个字是否正确（无错别字、无笔画错误）
- [ ] 是否有乱码/异形字符
- [ ] 中文是否被替换为英文或其他语言
- [ ] 数字和标点是否正确
- [ ] 文字是否清晰可读（无模糊/重叠）
- [ ] 文字内容是否与原文一致（未被 AI 擅自修改）

---

## 提示词模板

### 基础模板结构

```
[布局指令]
Create a {layout_type} infographic.

[尺寸与方向]
Aspect ratio: {aspect_ratio}. Orientation: {orientation}.

[视觉风格]
Visual style: {style_description}
Color palette: {colors}
Typography: {font_style}

[内容区块]
Title: "{标题}"
Subtitle: "{副标题}"

Section 1: "{要点1标签}"
- Content: "{要点1正文}"
- Icon hint: {icon_keyword}

Section 2: "{要点2标签}"
- Content: "{要点2正文}"
- Icon hint: {icon_keyword}

[...]

[文字约束]
ALL text in the image MUST be in Chinese (Simplified).
Text must be crisp, clear, and perfectly legible.
Every character must be accurate — no garbled, malformed, or invented characters.
Maintain clear visual hierarchy: title > section headers > body text.

[排版约束]
Maintain generous whitespace between sections.
Use consistent alignment throughout.
Icons/illustrations should complement text, not overwhelm it.
```

### 布局特定指令

每个布局类型有额外的结构指令（示例）：

**bento-grid:**
```
Arrange content in a modular grid with varied cell sizes (1x1, 2x1, 1x2, 2x2).
One hero cell for the main title. Supporting cells for each section.
Distinct cell boundaries with consistent spacing.
```

**flow:**
```
Arrange steps in a clear left-to-right (or top-to-bottom) flow.
Connect steps with arrows or lines.
Each step has a number, title, and brief description.
Progressive visual flow from start to end.
```

**comparison:**
```
Split the layout into two distinct sides (left vs right, or top vs bottom).
Use contrasting but harmonious colors for each side.
Align comparison points horizontally for easy scanning.
Clear labels for each side.
```

**funnel:**
```
Wide section at top, progressively narrowing toward bottom.
3-6 horizontal stages, each with a label and metric.
Stage width indicates relative volume/importance.
Distinct colors per stage.
```

---

## 文字审校与迭代编辑

### 三级文字保障机制

#### 第一级：提示词约束（预防）

在提示词中强制要求文字精准：
```
CRITICAL TEXT REQUIREMENTS:
- Every Chinese character must be pixel-perfect and correctly formed
- Do NOT invent, merge, or distort any characters
- If unsure about a character, use a simpler synonym rather than risk error
- Numbers must be exact: "73%" not "78%", "5个" not "3个"
- Punctuation follows Chinese conventions: "，" "。" "、" "：" not ", . / :"
```

#### 第二级：AI 自审（生成后检查）

**每张信息图生成后，必须执行自审流程：**

```
1. 读取生成的图片
2. 逐一核对图中文字与提示词中的原文
3. 检查项：
   a. 字形正确性：每个汉字笔画完整、结构正确
   b. 内容一致性：图中文字与原文完全一致
   c. 数字精确性：所有数字/百分比准确
   d. 排版可读性：文字无重叠、无截断、无模糊
4. 判定：
   → 全部通过 → 交付用户
   → 发现问题 → 进入自动修正（第三级）
```

#### 第三级：基于原图的迭代修正

**核心机制：将原图回传 Gemini API，只修改出错的部分，保持其他所有内容不变。**

```json
{
  "contents": [{"parts": [
    {"text": "Edit this infographic image. Fix ONLY the following text errors, keep everything else (layout, colors, icons, other text) exactly the same:\n1. Change '管理效立' to '管理效率'\n2. Change '5个步聚' to '5个步骤'\nDo not alter any other element."},
    {"inline_data": {"mime_type": "image/png", "data": "原图-base64"}}
  ]}],
  "generationConfig": {
    "responseModalities": ["IMAGE"],
    "imageConfig": {
      "aspectRatio": "原始比例"
    }
  }
}
```

**修正规则：**
- 每次修正只传达需要改的文字，不重述正确的部分
- 明确要求保持所有其他元素不变
- 修正后再次执行第二级自审
- 最多自动修正 3 轮
- 3 轮后仍有问题 → 保留最佳版本，列出剩余问题交付用户

### 用户反馈修正

当用户检查后发现问题或想改文字时：

```
用户反馈类型：
A. 文字错误（"第3个要点写错了，应该是'XXX'不是'YYY'"）
B. 文字修改（"把标题改成'XXX'"）
C. 局部调整（"第2个要点的图标换一个"）

处理方式：统一使用「基于原图的迭代修正」
1. 读取当前版本的图片
2. 构建修正提示词（仅描述需要改的部分）
3. 将原图 + 修正指令发送给 Gemini API
4. 生成修正版
5. 自审修正结果
6. 覆盖原文件
```

---

## 排版设计原则

从 baoyu-skills 系列（slide-deck、cover-image、comic、infographic）提炼的排版经验：

### 留白与密度

- **40-60% 留白**：信息图不是塞满内容，而是让核心信息呼吸
- 信息密度匹配内容复杂度：3-5 个要点用 sparse/balanced 布局，6-8 个用 dense 布局
- 每个区块内部也要有内边距，文字不贴边

### 视觉层级

- **3 层层级足够**：标题（最大最醒目）→ 要点标签（中号加粗）→ 正文（小号常规）
- 用字号差异 > 颜色差异 > 字重差异来建立层级
- 图标/插图是辅助，不应与文字争夺视觉权重

### 一致性控制

- **首图锚定**：如果生成多张信息图（系列），第一张作为视觉锚点，后续图片必须保持配色、字体、图标风格一致
- 使用 Gemini 的 image-to-image 能力：生成后续图片时，将第一张图作为参考图传入
- 同系列信息图使用统一的色板（主色+辅色+强调色，最多 4 色）

### 文字处理核心经验

- **只用原文原词**：标题、要点来自文章原文，禁止 AI 改写或概括（baoyu 的核心原则："preserve all source data verbatim"）
- **中文排版**：标点用中文全角，数字用半角阿拉伯数字
- **简化优于冒险**：如果某个词太长/太复杂可能导致 AI 生图出错，宁可用更短的同义表达，也不冒文字乱码的风险

### 风格微调维度

当用户想要更精细的风格控制时，可在 6 种内置风格基础上叠加 4 个微调轴：

| 维度 | 选项 | 默认 |
|------|------|------|
| **纹理** | clean（干净）/ grid（网格）/ paper（纸质）/ organic（有机） | clean |
| **氛围** | professional（专业）/ warm（温暖）/ cool（冷静）/ vibrant（明快） | 跟随风格 |
| **字体感** | geometric（几何）/ humanist（人文）/ handwritten（手写）/ editorial（编辑） | 跟随风格 |
| **密度** | minimal（极简）/ balanced（均衡）/ dense（紧凑） | balanced |

---

## 独立信息图模式

当用户不是为文章配图，而是直接要求「画一张信息图」时：

**触发判断：**
- 用户直接说「做一张信息图」「画信息图」但没有指定文章
- 用户提供了要可视化的文字内容（非文章文件）

**简化流程：**
```
1. 接收用户提供的内容（文字/要点/数据）
2. AI 推荐 2-3 个布局候选（基于内容结构）
3. 用户选择布局和风格
4. 结构化内容（提取标题、要点、层级）
5. 生成提示词 → 调用 API
6. 文字自审 → 修正
7. 交付用户 → 接受迭代反馈
```

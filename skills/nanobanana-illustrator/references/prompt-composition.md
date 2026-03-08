# 提示词组合与参数化方法

## 核心逻辑

```
最终提示词 = 基础提示词（来自风格文件）
            + 当前分小节标题和关键词
            + 文章主题的语境
            + 替换 {} 占位符的值
```

---

## 步骤 1: 读取风格文件

从用户选择的风格文件中提取两部分：

### 1.1 基础提示词

读取 `II. Style Core - Keep Unchanged` 部分：

```
示例（来自 photo_portrait 风格文件）：

II. Style Core - Keep Unchanged
1. Equipment Simulation: shot on digital mirrorless camera
2. Technical Parameters:
   - Aperture: f/1.4 creating shallow depth of field with creamy bokeh
   - Focal Length: 85mm portrait compression
3. Lighting Setup:
   - Light Type: golden hour sunlight
   - Light Position: Rembrandt lighting
   - Color Temperature: warm 3200K
4. Color Tone: desaturated film look
5. Composition: rule of thirds
6. Post-processing:
   - Saturation: natural
   - Contrast: medium
   - Color Grading: warm shadows cold highlights
```

**提取方法**：
- 保留所有技术参数和风格要素
- 这部分是"不变"的，每张配图都使用
- 去掉列表编号，整理成流畅的文字

### 1.2 可自定义元素

读取 `III. Customizable Elements` 部分：

```
示例：

III. Customizable Elements
1. Subject: {gender}, {age range}, {ethnicity}, {hair style and color}
2. Outfit: {clothing type}, {clothing color}, {accessories}
3. Expression & Pose: {expression}, {body pose}, {hand placement}
4. Setting: {location type}, {environment}, {time of day}
```

**提取方法**：
- 识别所有 `{}` 占位符
- 记录这些占位符对应的含义
- 后续用当前分小节的关键词填充

### 1.3 参考图提取（新增）

从风格文件的 `## 原图参考` 部分提取图片：

**解析规则：**
- 匹配 `![[filename.ext]]` 格式的 wikilinks
- 支持 `.png`, `.jpg`, `.jpeg`, `.webp` 格式
- 搜索路径优先级：
  1. `config.image_output_dir`（配图输出目录）
  2. Obsidian vault 根目录递归搜索
- 多张参考图按出现顺序排列

**用途：**
- 作为 API 调用的视觉参考输入
- 帮助 AI 理解目标风格的具体视觉表现
- 与文字提示词互补，提升风格还原度

**回退策略：**
- 文件不存在 → 警告但不阻断，使用纯文本模式
- 图片过大（>10MB）→ 压缩到合理大小后使用

---

## 步骤 2: 分析当前分小节

对于要配图的每个分小节，提取：

### 2.1 标题和关键词

```python
def extract_section_keywords(title, content):
    """
    从分小节标题和前N字内容中提取关键词
    """

    # 标题本身通常是最重要的关键词
    keywords = []
    keywords.append(title)

    # 从内容开头提取关键词（前200字）
    summary = content[:200]

    # 简单关键词提取：名词、动词、形容词
    important_words = extract_important_words(summary)
    keywords.extend(important_words[:5])

    return keywords

# 示例
title = "了解你的脚型"
content = "跑鞋选择的第一步是了解自己的脚型。常见的脚型有三种..."
keywords = ["脚型分析", "脚型", "跑步", "脚部特征"]
```

### 2.2 情绪内核提取（新增，优先于关键词）

```python
def extract_emotional_core(section_content):
    """
    从分小节内容中提取情绪内核——不是"发生了什么"，而是"让人感到什么"
    这是风格-内容调和的关键输入
    """

    emotional_core = {
        'primary_emotion': '',    # 主要情绪（如：温暖、压迫、失落）
        'tension': '',            # 情感张力（如：期待vs失望、自由vs束缚）
        'atmosphere': '',         # 氛围（如：亲密、孤独、紧张、释然）
    }

    return emotional_core

# 示例
# 文章段落："过年回家，七大姑八大姨轮番上阵，问工资、问对象、问房子"
emotional_core = {
    'primary_emotion': '被审视的压迫感',
    'tension': '亲情的温暖 vs 审视的压迫',
    'atmosphere': '表面热闹实则窒息',
}
```

### 2.3 内容主题语境

```python
def determine_section_context(article_type, section_content):
    """
    根据文章类型和该小节内容，确定语境
    """

    context = {
        'article_type': article_type,  # "科普" / "教程" / "产品评测" 等
        'section_tone': infer_tone(section_content),  # "教学" / "演示" / "比较" 等
        'visual_focus': infer_visual_focus(section_content),  # "对象" / "步骤" / "结果" 等
    }

    return context

# 示例
context = {
    'article_type': '教程',
    'section_tone': '教学',
    'visual_focus': '脚部特征展示'
}
```

---

## 步骤 3: 组合完整提示词

### 3.0 风格-内容调和应用（在组合前执行）

在组合提示词之前，必须先完成风格-内容调和判断（参见 skill.md 阶段 3.5.0）。
调和结果直接决定步骤 3.1 中「场景」部分的内容来源：

| 兼容性 | 场景来源 | 示例 |
|--------|---------|------|
| 🟢 高 | 直接使用文章的具象场景 | 咖啡店聊天 + 线描 → "two people chatting in a café" |
| 🟡 中 | 文章场景骨架 + 替换不兼容细节 | 年夜饭 + 水彩 → "family gathered around dinner table, warm candlelight"（去掉春联红包等中式符号） |
| 🔴 低 | 完全基于情绪内核重构场景 | 被催婚压迫 + 西方油画 → "young person standing alone in a grand baroque ballroom, surrounded by elegantly dressed figures casting scrutinizing gazes" |

**⚠️ 关键：🔴 低兼容时，提示词中不应出现任何原文的具象文化元素，只保留情绪。**

### 3.1 核心提示词框架

```
[基础提示词的共性元素]
featuring {基于调和结果的场景描述}
conveying {情绪内核}
in a {风格自然的视觉环境}
for {目的语境}
```

### 3.2 具体组合示例

**例子 1：🟢 高兼容 — 科普文章 + 健身摄影风格**

原文内容：
```
## 了解你的脚型
跑鞋选择的第一步是了解自己的脚型。常见的脚型有三种：
正常足、高足弓、扁平足...
```

风格文件（假设是健身摄影风格）：
```
II. Style Core
Equipment: shot on digital camera
Lighting: studio strobe, bright clean
Color: vibrant natural colors
Style: clear educational photography
```

生成的提示词：
```
An educational photograph showing different foot types,
shot on digital camera with studio strobe lighting,
bright and clean aesthetic with vibrant natural colors,
featuring clear diagrams or visual demonstrations of normal foot, high arch, and flat foot,
in a professional fitness context,
for teaching and health education,
clear and informative style
```

**例子 2：教程文章 - 步骤演示**

原文内容：
```
## 选择步骤演示
1. 测量你的脚长
2. 确定脚型
3. 查看推荐表
```

风格文件（产品展示风格）：
```
II. Style Core
Equipment: shot on product photography setup
Lighting: soft directional light with rim light
Color: clean, minimal, white/neutral background
Style: product showcase
```

生成的提示词：
```
A step-by-step product demonstration photograph,
shot on professional product photography setup with soft directional lighting,
clean white background with minimal distractions,
featuring hands demonstrating the shoe selection process,
including foot measurement and comparison,
in a clear instructional style,
for a tutorial guide,
high quality product showcase aesthetic
```

**例子 3：🔴 低兼容 — 情感文章 + 西方古典油画风格（需情绪转译）**

原文内容：
```
## 过年回家的第一顿饭
回到家，妈妈早就准备好了一桌子菜。
爸爸开了一瓶白酒，说"回来就好"。
那一刻我觉得这一年的委屈都值了...
```

风格文件（西方古典油画壁画风格）：
```
II. Style Core
Medium: oil painting on canvas
Technique: classical realism with dramatic chiaroscuro
Color palette: rich warm golds, deep crimsons, umber shadows
Composition: baroque diagonal, theatrical staging
Lighting: single strong directional source, Caravaggio-style
```

风格-内容调和分析：
```
情绪内核：归属感、被等待的温暖、辛劳之后的释然
兼容性：🔴 低 — 中式年夜饭场景（圆桌、白酒、家常菜）不属于
  古典油画的视觉世界
转译策略：在油画世界中找到承载"归家、被等待、温暖一餐"
  的等价场景
```

生成的提示词：
```
A classical oil painting in rich baroque style with dramatic chiaroscuro,
depicting a weary traveler arriving at a warmly lit stone cottage,
a modest table set with bread, wine and candlelight awaiting them,
a figure at the doorway turning with an expression of quiet joy,
conveying the profound warmth of homecoming and belonging,
rich warm golds and deep umber shadows,
Caravaggio-style single directional lighting casting long tender shadows,
theatrical yet intimate composition
```

> 注意：没有出现任何中国元素（春联、白酒、圆桌），但完美传达了
> "被等待的温暖""归家的释然"这一情绪内核，且画面天然属于古典油画的视觉世界。

---

## 步骤 4: 处理 {} 占位符

### 4.1 自动填充策略

对于风格文件中的 `{占位符}`，填充值必须基于风格-内容调和结果：

| 占位符 | 🟢 高兼容填充 | 🟡 中兼容填充 | 🔴 低兼容填充 |
|--------|-------------|-------------|-------------|
| `{人物性别}` | 从文章推断 | 从文章推断 | 从文章推断（人物特征可跨文化） |
| `{年龄段}` | 从文章推断 | 从文章推断 | 从文章推断 |
| `{服装}` | 文章描述的服装 | 去文化标记的服装 | **风格世界中的等价服装** |
| `{场景}` | 文章的具象场景 | 场景骨架+替换细节 | **风格世界中的等价场景** |
| `{表情}` | 从情绪推断 | 从情绪推断 | 从情绪推断（表情可跨文化） |

### 4.2 具体替换示例

**🟢 高兼容示例**

原风格文件：
```
III. Customizable Elements
1. Subject: {gender}, {age range}
2. Outfit: {clothing type}, {clothing color}
3. Setting: {location type}, {environment}
4. Expression: {expression}
```

当前分小节：跑鞋选择教程 + 健身摄影风格

替换后：
```
1. Subject: person (unspecified gender), adult
2. Outfit: athletic wear, neutral colors
3. Setting: fitness studio, well-lit environment
4. Expression: focused, instructional
```

**🔴 低兼容示例**

当前分小节：过年回家吃饭 + 西方古典油画风格

替换后（注意场景和服装已完全转译）：
```
1. Subject: young adult, weary but relieved
2. Outfit: travel-worn cloak and boots (NOT 棉袄/羽绒服)
3. Setting: candlelit stone cottage, modest table with bread and wine (NOT 圆桌年夜饭)
4. Expression: quiet joy, the relief of homecoming
```

---

## 步骤 5: 最终提示词整合

### 格式标准化

最终提示词应该：
1. ✅ 是完整英文句子（Nanobanana 偏好）
2. ✅ 包含共性元素（确保风格一致）
3. ✅ 包含该分小节特定内容（关键词、场景）
4. ✅ 避免 tag soup 格式（如：`portrait, 35mm, bokeh`）
5. ✅ 清晰表达生成目的

### 提示词审查清单

```
□ 是否包含基础提示词的所有共性元素？
□ 是否执行了风格-内容调和判断？兼容性级别是什么？
□ 🔴 低兼容时：提示词中是否残留了与风格世界不兼容的具象元素？
□ 🔴 低兼容时：转译后的场景是否天然属于风格的视觉世界？
□ 情绪内核是否在转译后依然清晰可感？
□ 是否有当前分小节的关键词和场景？
□ 是否使用了自然语言而非 tag 格式？
□ 是否有清晰的目的语境（for teaching/for product showcase/etc.）？
□ 是否避免了过度修饰词（太多形容词）？
□ 是否与文章整体主题一致？
□ 生成的图片是否能帮助理解该小节内容？
□ 是否已附带参考图？（如风格文件包含原图参考）
```

---

## 特殊情况处理

### 情况 1: 同一风格多张配图

**问题**：容易导致图片相似度过高

**解决**：
- 保留所有共性元素（确保风格一致）
- 加强每个分小节的**关键词差异化**
- 改变场景或视角来区分

```
配图1（脚型分析）：
"featuring different foot types side-by-side,
close-up view showing arch and ankle structure"

配图2（选择演示）：
"featuring hands measuring and comparing feet,
full body perspective showing shoe fitting process"
```

### 情况 2: 风格文件缺少某些信息

**问题**：比如风格文件很简洁

**解决**：
- 使用风格文件已有的信息
- 从文章主题推断补充信息
- 保持简洁，避免过度编造

```
简洁风格文件：
"Portrait photography, warm lighting, natural colors"

补充后：
"Portrait photography with warm, natural lighting,
featuring [当前分小节的人物描述],
capturing authentic emotion and connection"
```

### 情况 3: 不同文章类型的适配

不同文章类型需要不同的语气和视角：

| 文章类型 | 提示词语境 |
|---------|-----------|
| 科普 | "educational", "informative", "explaining" |
| 教程 | "step-by-step demonstration", "instructional" |
| 产品评测 | "product showcase", "detailed review", "comparison" |
| 旅行 | "scenic photography", "experiential", "atmospheric" |
| 故事 | "narrative scene", "emotional", "cinematic" |

---

## 提示词生成清单

对每个配图位置，执行：

```
1️⃣ 读取风格文件的 Style Core
2️⃣ 提取当前分小节的关键词和场景
3️⃣ 填充 {} 占位符
4️⃣ 组合成流畅的英文句子
5️⃣ 添加文章类型的语境词
6️⃣ 审查是否符合 Nanobanana 黄金法则
7️⃣ 调整和优化
8️⃣ 最终确认
9️⃣ 传递给 API
```

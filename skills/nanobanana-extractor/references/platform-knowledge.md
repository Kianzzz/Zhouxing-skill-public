# Nanobanana 平台特性与最佳实践

## 平台基础

### 核心技术

- 基于 Google Gemini 2.5 Flash Image 模型
- 采用 "Thinking 模式"：先推理构图逻辑，再渲染图像
- 支持最多 14 张参考图（6 张高保真度）
- 擅长对话式编辑和语义理解

### 与其他平台的区别

| 特性 | Nanobanana | Midjourney | DALL-E |
|------|------------|------------|--------|
| 提示词格式 | 自然语言句子 | 关键词+参数 | 自然语言 |
| 长度偏好 | 详细描述更好 | 简洁为主 | 中等长度 |
| 参考图 | 最多14张 | 1张 | 无 |
| 编辑方式 | 对话式 | 变体/重绘 | 局部编辑 |

---

## 黄金法则

### 1. 自然语言优先

**核心原则**：使用完整句子，避免 "tag soup" 格式

❌ 错误示例：
```
woman, red dress, street, night, 4k, realistic, bokeh, cinematic
```

✅ 正确示例：
```
A sophisticated woman in a flowing red dress walks confidently down a rain-soaked cobblestone street at night, illuminated by warm amber streetlights that create a cinematic atmosphere with beautiful bokeh in the background.
```

### 2. 具体性至上

用精确描述替代模糊词汇：

| 模糊 ❌ | 具体 ✅ |
|--------|---------|
| a woman | a sophisticated elderly woman in her 70s |
| nice lighting | soft golden hour sunlight streaming through window |
| good composition | rule of thirds with subject placed at right intersection |
| high quality | shot on Hasselblad medium format with 80mm lens |

### 3. 情境框架

提供 "为什么" 或 "为谁"，帮助模型推断细节：

```
for a Brazilian high-end gourmet cookbook
→ 模型自动推断：专业摆盘、浅景深、温暖光线、精致摆盘

for a tech startup pitch deck
→ 模型自动推断：现代感、简洁、专业、科技蓝色调
```

### 4. 材质和纹理描述

加入表面质感，提升真实感：

```
- matte finish (哑光表面)
- brushed steel (拉丝不锈钢)
- soft velvet (柔软天鹅绒)
- weathered wood (风化木材)
- polished marble (抛光大理石)
- frosted glass (磨砂玻璃)
```

### 5. 空间关系表达

使用清晰的空间描述词：

```
- in the foreground... in the background...
- positioned to the left of... behind...
- illuminated by... creating shadows that...
- reflected in... visible through...
```

---

## 避免 AI 审美陷阱

### 常见问题及解决方案

| 问题 | 解决方案 |
|------|----------|
| 过度饱和的色彩 | 使用 "natural saturation" / "muted tones" |
| 过于完美光滑的皮肤 | 添加 "natural skin texture with visible pores" |
| 过度戏剧化的光影 | 指定 "soft ambient lighting" / "natural daylight" |
| 刻板对称的构图 | 使用 "slightly off-center" / "candid angle" |
| 塑料质感的材质 | 描述 "worn texture" / "natural imperfections" |
| 无灵魂的眼神 | 指定 "genuine emotion" / "looking slightly off-camera" |

### 提升品质的关键词

**真实感类**：
- naturalistic, authentic, candid
- lived-in, imperfect beauty, organic

**质感类**：
- tactile quality, subtle texture, material authenticity
- weathered, aged naturally, well-used

**氛围类**：
- breathing space, layered depth
- understated elegance, refined yet effortless

---

## 负面提示词策略

### 通用负面提示词

```
Negative Prompts: overly saturated colors, plastic skin, unnatural lighting,
stiff poses, dead eyes, over-processed, artificial look, uncanny valley,
generic stock photo feel, oversimplified, cartoonish when realistic intended
```

### 领域特定负面提示词

**人像摄影**：
```
over-smoothed skin, fake bokeh, unnatural eye color, puppet-like pose,
excessive beauty filter, HDR overdone
```

**风景摄影**：
```
oversaturated sky, HDR artifacts, unrealistic colors, lens flare abuse,
over-sharpened, fake clouds
```

**绘画写实**：
```
inconsistent lighting direction, anatomical errors, flat rendering,
muddy colors, visible AI artifacts, uncanny proportions
```

**平面设计**：
```
cluttered layout, inconsistent margins, font conflicts,
poor hierarchy, off-brand colors, amateur composition
```

---

## 对话式编辑技巧

当生成的图片接近目标但有小瑕疵时，使用针对性调整：

```
"Adjust the lighting to be softer and more diffused"
"Move the subject slightly to the left"
"Change the background color from blue to warm amber"
"Add more depth to the shadows"
"Make the skin tone warmer"
"Reduce the saturation by about 20%"
```

### 迭代策略

1. 第一次生成：使用完整详细提示词
2. 微调：针对具体问题给出简短指令
3. 避免：每次都重新生成完整提示词

---

## 多参考图使用

### 高保真度参考（最多6张）

用于主体复刻：
- 人物面部
- 产品外观
- 特定物体

### 低保真度参考（最多8张）

用于风格参考：
- 整体氛围
- 色调风格
- 光影效果

### 指定策略

```
"Use the face from reference image 1 with high fidelity"
"Apply the color grading style from reference image 2"
"Match the lighting setup shown in reference image 3"
```

---

## 技术参数表达

### 摄影参数

```
shot on [camera model] with [lens focal length]mm lens
aperture f/[value] creating [depth of field description]
[shutter speed] capturing [motion effect]
ISO [value] for [grain/noise level]
```

### 光线表达

```
[light type] from [direction] creating [shadow quality]
color temperature around [K value] giving a [mood] feel
[lighting ratio] between highlights and shadows
```

### 后期风格

```
processed with [style] color grading
[contrast level] contrast with [shadow treatment]
[saturation level] saturation emphasizing [color range]
subtle [effect] adding [quality]
```

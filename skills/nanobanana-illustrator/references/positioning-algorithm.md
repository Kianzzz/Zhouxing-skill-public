# 配图位置计算算法

## 核心原则

- 配图位置基于**内容结构**，而非字数间距
- 避开特殊区块（代码、表格、列表）
- 尽量在分小节内容的中段或末尾
- 不强制间距均匀，而是自然分布

---

## 位置选择算法

### 步骤 1: 解析 Markdown 结构

```python
def parse_markdown(content):
    """
    解析 markdown，识别：
    - 所有标题（H1/H2/H3）及其位置
    - 各小节的开始和结束字符位置
    - 特殊区块（代码块、表格、列表）的位置
    """

    sections = []
    for match in re.finditer(r'^(#{1,3})\s+(.+)$', content, re.MULTILINE):
        level = len(match.group(1))
        title = match.group(2)
        start_pos = match.start()

        sections.append({
            'level': level,
            'title': title,
            'start': start_pos,
            'content_start': match.end() + 1  # 标题之后的内容起点
        })

    # 计算每个小节的结束位置
    for i in range(len(sections)):
        if i < len(sections) - 1:
            sections[i]['end'] = sections[i+1]['start']
        else:
            sections[i]['end'] = len(content)

    return sections
```

### 步骤 2: 识别有配图价值的分小节

```python
def identify_sections_for_image(sections, article_type):
    """
    根据内容分析和评分，识别哪些分小节需要配图
    """

    candidates = []

    for section in sections:
        # 跳过 H1（主标题）
        if section['level'] == 1:
            continue

        # 提取该小节内容
        content = content[section['content_start']:section['end']]

        # 计算配图价值评分
        score = evaluate_section(content, article_type, section['title'])

        if score >= 7:
            candidates.append({
                'section': section,
                'score': score,
                'type': 'must_have'
            })
        elif score >= 5:
            candidates.append({
                'section': section,
                'score': score,
                'type': 'optional'
            })

    return candidates
```

### 步骤 3: 在每个分小节中找位置

```python
def find_position_in_section(section_content, section_title):
    """
    在该分小节内找最适合插入配图的位置

    优先级：
    1. 避开特殊区块（代码、表格、列表）
    2. 避开小节开头（需要有足够上下文）
    3. 倾向中段或末尾
    """

    # 删除特殊区块（临时）
    safe_content = section_content
    safe_content = remove_code_blocks(safe_content)
    safe_content = remove_tables(safe_content)
    safe_content = remove_lists(safe_content)

    # 找段落边界
    paragraphs = safe_content.split('\n\n')

    # 选择位置：倾向于后面的段落
    if len(paragraphs) >= 2:
        # 取后 50%-75% 的位置
        target_index = int(len(paragraphs) * 0.6)
        position = sum(len(p) for p in paragraphs[:target_index])
    else:
        # 如果只有一个段落，放在末尾
        position = len(section_content) - 100  # 倒数100字处

    return position
```

### 步骤 4: 验证位置有效性

```python
def validate_position(full_content, section, position):
    """
    确保位置有效，避免：
    - 在代码块中
    - 在表格中
    - 在列表中
    - 离标题太近
    """

    # 检查周围内容
    context_start = max(0, position - 200)
    context_end = min(len(full_content), position + 200)
    context = full_content[context_start:context_end]

    # 检查特殊标记
    if '```' in context:
        # 在代码块中，向前移动
        position = context_start

    if '|' in context and '-' in context:
        # 可能在表格中，向前移动
        position = context_start

    if context.count('-') > 5:
        # 可能在列表中，向前移动
        position = context_start

    # 确保距标题足够远（至少100字）
    section_start = section['content_start']
    if position - section_start < 100:
        position = min(section_start + 200, section['end'])

    return position
```

---

## 完整流程示例

### 示例文章结构

```markdown
# 如何选择跑鞋

## 为什么需要好的跑鞋
这一节是理论... 评分 4 → 不配图

## 了解你的脚型
这一节讲脚型分析... 评分 7 → 配图

## 选择步骤演示
这一节有具体步骤... 评分 9 → 配图

## 热门品牌推荐
这一节是产品列表... 评分 5 → 可选

## 总结建议
这一节是总结... 评分 3 → 不配图
```

### 位置计算过程

```
1️⃣ 解析结构
   识别出4个 H2 分小节

2️⃣ 评分和筛选
   - "了解脚型" (7分) → 必配 ✅
   - "选择步骤" (9分) → 必配 ✅
   - "热门品牌" (5分) → 可选 ⚠️

3️⃣ 配图数决策
   选择 2 张必配 + 1 张可选 = 3 张

4️⃣ 计算每个位置

   分小节1："了解你的脚型"
   ├─ 内容长度：约 800 字
   ├─ 找位置：在该节内容的 60% 处（约 480 字后）
   ├─ 避开代码/表格/列表
   └─ 最终位置：该小节的 "脚型分类总结" 部分后

   分小节2："选择步骤演示"
   ├─ 内容长度：约 1200 字
   ├─ 找位置：在该节内容的 60% 处（约 720 字后）
   └─ 最终位置：该小节的 "实际操作演示" 部分后

   分小节3："热门品牌推荐"（可选）
   ├─ 询问用户是否需要配图
   └─ 如是：在品牌列表后配图展示产品
```

### 生成 Markdown 插入点

```markdown
# 如何选择跑鞋

## 为什么需要好的跑鞋
[原内容不变]

## 了解你的脚型
[前半部分内容]

通过分析这三种脚型...

![脚型分析](../../40-输出/401-图片/跑鞋指南-配图-1.png)

[后半部分内容]

## 选择步骤演示
[前半部分内容]

实际操作时，你需要...

![选择演示](../../40-输出/401-图片/跑鞋指南-配图-2.png)

[后半部分内容]

## 热门品牌推荐
[内容]

![推荐品牌](../../40-输出/401-图片/跑鞋指南-配图-3.png)

## 总结建议
[原内容不变]
```

---

## 特殊情况处理

### 情况 1: 小节内容很短（< 300字）

**策略**：
- 评分 >= 8 → 配图（放在末尾）
- 评分 < 8 → 不配图（太短容易显得突兀）

### 情况 2: 分小节中有多个段落段落

**策略**：
```
优先级：
1. 避开第一段（需要有上文）
2. 选择中间的自然段落边界
3. 避开最后一小段（如果只有1-2句）
```

### 情况 3: 包含代码块的教程

**策略**：
```
优先级：
1. 不要在代码块中插入
2. 可在代码块后插（展示结果）
3. 如有"预期输出"注释，在那之后插
```

### 情况 4: 表格密集的内容

**策略**：
```
- 避免在表格中插入
- 可在表格后插
- 如配图是表格内容的补充，需确保关联性清晰
```

---

## 配图位置检查清单

在最终确认配图位置前，检查：

- [ ] 位置在文章内有充足的上下文（≥100字）
- [ ] 位置不在代码块、表格、列表中间
- [ ] 位置不会破坏列表的连续性
- [ ] 位置在相关内容的逻辑终点
- [ ] 位置前后的过渡自然
- [ ] 配图描述（alt text）与该部分内容关联

---

## 配图间距说明

❌ **不要强制均匀间距**

✅ **让配图自然分布**

原因：
- 配图数量取决于内容结构（不是字数）
- 不同分小节内容长度差异大
- 强制间距会导致不相关内容配图，或相关内容不配图

# 会话标记格式说明

Writing Copilot 在文章 `.md` 文件中使用 HTML 注释块存储会话状态，实现跨会话续写。

## 标记类型

### 1. WC:SESSION — 大纲与进度

```markdown
<!-- WC:SESSION
outline:
  - section: 开头
    status: done
    notes: 用场景切入
    voice_extracted: 2026-03-01
    content_hash: "你有没有过这样的经历——打开电脑想写点东西..."
  - section: 第一部分：为什么会这样
    status: current
    notes: 重点讲三个原因
  - section: 第二部分：怎么解决
    status: pending
  - section: 结尾
    status: pending
last_updated: YYYY-MM-DD
review_enabled: true
-->
```

**字段说明：**
- `outline`: 大纲数组，每个条目包含：
  - `section`: 部分名称
  - `status`: `done` / `current` / `pending`
  - `notes`: 该部分的写作要点（可选）
  - `voice_extracted`: 上次风格提取的日期（可选，仅 `done` 状态的部分会有）
  - `content_hash`: 上次提取时该部分内容前100字的摘要（可选，用于判断内容是否被修改过）
- `last_updated`: 最后更新日期
- `review_enabled`: 审校开关，`true`/`false`

**位置：** 文章文件最顶部，正文之前。

### 2. WC:FRAGMENTS — 碎片想法区

```markdown
<!-- WC:FRAGMENTS
- [第二部分] "像修自行车一样，你得先知道哪个零件坏了"——这个比喻可以用
- [结尾] 回扣开头那个问题
- [未分类] 突然想到的一个金句
-->
```

**格式规则：**
- 每条碎片一行，`-` 开头
- 方括号内标注属于大纲的哪个部分
- 无法确定归属时用 `[未分类]`

**位置：** 正文之后。

### 3. WC:EDITS — 编辑笔记区

```markdown
<!-- WC:EDITS
- 第二段"好的"改成更有力的词
- 开头第一句语气太弱，完稿后加强
- 第三部分的例子不够具体，需要替换
-->
```

**格式规则：**
- 每条编辑笔记一行，`-` 开头
- 描述位置 + 修改意图

**位置：** 碎片区之后，文件末尾。

## 解析规则

1. **读取**：用正则匹配 `<!-- WC:SESSION\n(.*?)\n-->` 提取 YAML 内容，解析为结构化数据
2. **更新**：修改数据后，重新生成整个注释块并替换原位置
3. **清理**：收尾时删除所有 `<!-- WC:` 开头的注释块，保留纯净文章

## 完整文件示例

```markdown
<!-- WC:SESSION
outline:
  - section: 开头
    status: done
    notes: 用场景切入
    voice_extracted: 2026-03-01
    content_hash: "你有没有过这样的经历——打开电脑想写点东西..."
  - section: 第一部分：问题分析
    status: current
    notes: 三个原因
  - section: 第二部分：解决方案
    status: pending
  - section: 结尾
    status: pending
last_updated: 2026-03-01
review_enabled: true
-->

你有没有过这样的经历——打开电脑想写点东西，盯着空白页面半小时，一个字也没写出来。

不是你没想法，而是想法太多了，多到不知道从哪里开始。

这其实是一个很典型的"输入过载"症状。

## 第一部分：问题分析

（正在写...）

<!-- WC:FRAGMENTS
- [第二部分] 可以用"整理衣柜"的比喻——先全部倒出来，再分类放回去
- [结尾] 回扣开头那个"盯着空白页面"的画面
-->

<!-- WC:EDITS
- 开头第三句"输入过载"这个词太学术，考虑换个更日常的说法
-->
```

---
name: web-search
description: 通用联网搜索工具，支持多平台、多场景的智能搜索和内容提取。触发场景：(1) 用户说"搜索"、"查找"、"找资料" (2) 用户需要收集网络素材、案例、数据 (3) 用户需要查找技术文档、代码示例 (4) 用户需要搜索社交媒体内容 (5) 用户提到"web-search"或"联网搜索"。
allowed-tools: Read, Write, Edit, Bash, AskUserQuestion, WebFetch, WebSearch
---

# Web Search V5.1

通用联网搜索工具。像人一样思考搜索策略，灵活调配 16 个通道资源，输出 10-15 条高质量结果。

## 搜索策略哲学

搜索的本质是"用最短路径找到用户需要的信息"。不同的搜索任务需要不同的策略——"查最新 AI 新闻"和"找某个 API 的配置案例"是完全不同的任务，不应该走同一条固定流水线。

### 四步思考循环

每次搜索任务，按这个框架思考：

**① 定义成功标准**：用户到底需要什么？要案例还是要评价？要最新动态还是要深度分析？什么样的结果算"搜到了"？这是后续所有判断的锚点。

**② 选择最可能直达的搜索策略**：根据成功标准和话题特征，判断哪些通道最可能产出高质量结果。不需要每次都搜全部 16 个通道——中文话题侧重知乎/小红书/微博/Bilibili，技术话题侧重 Reddit/Medium/V2EX，实时动态侧重 Twitter/微博。把资源集中在最可能命中的方向。

**③ 证据式过程校验**：每一步的搜索结果都是证据。结果偏离意图 → 调整关键词方向。某通道结果质量差 → 换通道或换策略。发现新的高频术语 → 补充搜索（雪球迭代）。

**④ 对照成功标准停止**：已有足够高质量结果就输出，不为凑数而搜。不过度操作。

### 通道选择逻辑

通道选择基于「话题-平台亲和矩阵」（详见 `references/topic-affinity.md`）：

1. 意图识别后，匹配最接近的话题领域（AI/技术前沿、编程/开发、写作/个人成长、金融/投资、生活方式、产品/工具评测、新闻/时事、学术/研究）
2. 按亲和度排序：**≥ 0.5 为主力通道，0.3-0.5 为辅助通道，< 0.3 跳过**
3. 搜索量按亲和度比例分配：`max_results × 亲和度`（最低 5 条）
4. 评分阶段加权：`base_score × (0.7 + 0.3 × 亲和度)`

**最低通道约束（不可违反）**：
- 每次搜索至少覆盖 **6 个通道**
- 其中中文通道 ≥ 2（知乎/小红书/微博/Bilibili/V2EX/雪球/微信/抖音）
- 其中英文通道 ≥ 2（Reddit/Twitter/Medium/YouTube/LinkedIn）
- 即使意图高度聚焦，也不得低于此下限。不足 6 个时从亲和度最高的已跳过通道中补回

主力通道多搜（25-30 条），辅助通道少搜（10-15 条）。总搜索量保持 100-160 条区间。

---

## 核心流程概览

**意图识别 → 关键词生成 → 并行搜索 → 雪球迭代 → 双重筛选 → 条目输出**

---

## 搜索通道能力边界

每个通道有不同的优势和局限，选择时要清楚它能给你什么：

| 通道 | 擅长 | 局限 | 流量指标 |
|------|------|------|---------|
| **Reddit** | 真实用户讨论、踩坑经验、产品对比 | 中文内容少 | score |
| **Twitter/X** | 实时性强、开发者一手动态 | 信息碎片化 | likes + retweets |
| **Medium** | 深度技术文章、最佳实践 | 付费墙、英文为主 | claps |
| **YouTube** | 教程演示、直观操作 | 无法快速浏览文字 | views |
| **知乎** | 中文深度讨论、专业回答 | 需 cookie、营销号多 | 赞同数 |
| **小红书** | 中文用户体验、生活化分享 | 技术深度有限 | 点赞 + 收藏 |
| **Bilibili** | 中文视频教程、科普解说 | 视频为主 | 播放量 |
| **微博** | 中文实时热点、社会讨论 | 碎片化、广告多 | 转发 + 点赞 |
| **V2EX** | 程序员社区、工具评测 | 无搜索 API | replies |
| **雪球** | 金融投资讨论 | 需 cookie、领域窄 | 回复 + 转发 |
| **LinkedIn** | 职场/专业内容 | 反爬严格 | 无 |
| **抖音** | 短视频、生活内容 | 文字信息少 | 无 |
| **RSS** | 自定义信息源、博客聚合 | 需配置、本地匹配 | 无 |
| **微信公众号** | 中文深度长文 | 依赖 wechat-extractor | 无 |
| **播客** | 对话/访谈内容 | 音频为主 | 无 |
| **通用网页** | 博客/文档/Gist/论坛长尾 | 质量参差 | 无 |

各通道的搜索实现、评分阈值、已知问题详见 `references/channels/{通道ID}.md`。

---

## 工作流程

### 前置检查 1: 用户 DNA

首次搜索时（`~/.web-search/user-dna.json` 不存在），通过 AskUserQuestion 采集用户基础信息：

1. **你的身份角色？** — 自媒体创作者 / 独立开发者 / 产品经理 / 研究者 / 学生 / 其他
2. **你搜索时最看重什么信息类型？** — 一手信息源(开发者推文/官方发布) / 深度分析(评测/教程) / 案例模板 / 趋势热点
3. **你的目标受众？** — 普通用户 / 技术人员 / 行业从业者 / 自己学习用

存为 `~/.web-search/user-dna.json`，结构分两层：

```json
{
  "stable": {
    "role": "AI自媒体创作者",
    "info_preference": "一手信息源",
    "target_audience": "普通用户",
    "created": "2026-03-24"
  },
  "domains": {}
}
```

**稳定层**（`stable`）：首次建档后基本不变，跨所有领域通用。决定"你是谁"——创作者视角、一手信息偏好、面向普通用户，这些在搜 AI、搜写作、搜生活方式时全部适用。

**动态层**（`domains`）：随搜索行为自动演化，不需要用户手动配置。每次搜索自动更新：

```json
{
  "domains": {
    "AI/技术前沿": {"weight": 0.55, "count": 12, "last": "2026-03-24"},
    "写作/个人成长": {"weight": 0.30, "count": 6, "last": "2026-03-23"},
    "生活方式": {"weight": 0.15, "count": 3, "last": "2026-03-20"}
  }
}
```

**动态层更新规则**：
- 每次搜索后，识别本次话题领域，对应 domain 的 `count += 1`，`last` 更新为今天
- `weight` = 该领域 count / 所有领域 count 总和（自动归一化）
- 新领域首次搜索时自动创建条目

**使用方式**：
- 稳定层 → 每次搜索都读取，影响意图解读、信息源偏好、关键词个性化
- 动态层 → 搜索时用**本次话题对应的 domain** 匹配亲和矩阵，不用全局单一 domain
- 稳定层 `role` 和动态层 `domains` 组合解读意图（如"AI自媒体创作者"搜"写作技巧" → 偏向"AI辅助写作"而非"传统文学创作"）

---

### 前置检查 2: 凭证验证

搜索前需要确认 API 凭证状态——没有有效凭证的通道无法使用 API 搜索（但可以用 WebSearch `site:` 兜底，质量会降低）。

1. 读取 `~/.web-search/config.json`
2. 检查以下凭证字段是否非空：
   - `exa_api_key`（Twitter/Reddit Tier 3 兜底）
   - `zhihu_z_c0` + `zhihu_d_c0`（知乎搜索必需）
   - `xueqiu_cookie`（雪球搜索必需）
3. 如果配置文件不存在或凭证为空，用 AskUserQuestion 告知用户：
   - 列出缺失的凭证及其影响
   - 询问用户：是否现在补充凭证，还是跳过这些通道继续搜索
4. 如果用户选择补充，引导获取并写入配置文件后再继续
5. 如果用户选择跳过，记录跳过的通道，在最终输出的筛选说明中标注

**不需要凭证的通道**：Reddit(Tier 1/2)、Twitter(Tier 1 Exa)、YouTube、Medium、Bilibili、小红书(MCP自管理)、V2EX、LinkedIn、抖音、RSS、播客、微信(跨skill)、通用网页

**轻量认证通道**：微博（访客 Cookie 可自动生成，无需用户操作）

---

### 步骤 0: 意图识别

意图识别是搜索的锚点——后续所有决策都基于这一步的结果。

#### 意图分类表

| 意图类型 | 特征词 | 用户真正想要 | 搜索方向 |
|---------|--------|-------------|---------|
| **实战案例** | "案例"、"例子"、"怎么用"、"实战"、"模板" | 别人写的使用示例、配置模板、经验分享 | 博客教程、社区分享、Gist |
| **技术原理** | "原理"、"源码"、"实现"、"架构"、"底层" | 技术实现细节、源代码分析 | 技术博客、官方文档 |
| **观点评价** | "评价"、"怎么样"、"值不值"、"对比" | 用户评价、产品对比、优缺点分析 | Reddit、知乎、Twitter 讨论 |
| **教程指南** | "教程"、"怎么做"、"步骤"、"入门" | 从零开始的操作指南 | Medium、YouTube、知乎专栏 |
| **资讯动态** | "最新"、"发布"、"更新"、"新闻" | 最近发生的事件和发布 | Twitter、微博、Reddit |

#### 歧义判断规则

歧义搜索会浪费大量资源。以下情况必须用 AskUserQuestion 向用户澄清：

1. **同一关键词可指向多种内容类型**
2. **搜索词过于宽泛**
3. **存在领域歧义**
4. **用户表述含糊**

意图明确时直接进入步骤 1，不需要询问用户。

#### 结合用户 DNA 解读意图

当 `~/.web-search/user-dna.json` 存在时，意图识别必须结合用户身份个性化解读：

| 用户搜索 | 无 DNA 时理解 | 有 DNA 时理解（示例：AI自媒体创作者） |
|---------|-------------|-------------------------------|
| "AI 资讯" | 通用 AI 新闻 | 一手 AI 新玩法、能影响普通人的更新 |
| "Claude 更新" | Anthropic 发布记录 | 创作者能用的新功能、实操亮点 |
| "提示词技巧" | 通用 prompt 教程 | 可直接教给受众的提示词方法 |
| "写作技巧" | 通用写作教程 | AI辅助写作方法（role=AI自媒体 → 偏向AI+写作交叉） |

**个性化规则**：
- `stable.info_preference = "一手信息源"` → 关键词加入 "release"/"changelog"/"announcement"，信息源层级三手降权加倍（从 0 变为 -10）
- `stable.target_audience = "普通用户"` → 关键词加入 "practical"/"for everyone"/"普通人能用"，过滤纯学术论文
- `stable.role` + `domains` 组合匹配话题亲和矩阵（用本次搜索对应的 domain 行，不是全局单一领域）
- 搜索完成后自动更新 `domains`：对应领域 count+1，weight 重算

---

### 步骤 1: 结构化关键词生成

基于步骤 0 的意图识别结果，生成三层关键词：

| 层级 | 用途 | 数量 |
|------|------|------|
| **核心词** | 直接描述用户需求 | 1-2 个 |
| **扩展词** | 同义词、相关概念、上下游词汇 | 2-4 个 |
| **通道定向词** | 针对特定通道优化的搜索词 | 每通道 1 个 |

#### 关键词生成规则

1. **从意图出发，而非从字面出发**
2. **中英文双语**：每个核心词同时生成中文和英文版本
3. **避免歧义词**：如果步骤 0 排除了某个方向，关键词中不应包含该方向的专属词汇
4. **加入场景限定词**：如 `实战`, `案例`, `tutorial`, `best practices`
5. **代表人物扩展**：确信识别出领域 KOL 时加入人名扩展词（不确定时不加）
6. **历史名称/别名覆盖**：用 WebSearch 确认搜索主体是否有曾用名/缩写/社区俗称
7. **Reddit 定向 subreddit**：识别 2-3 个最相关的 subreddit

---

### 步骤 2: 并行搜索

**搜索策略**：根据步骤 0 的意图和话题亲和矩阵，选择 **6-10** 个通道（最低 6 个，含中文≥2 英文≥2）。总量 100-160 条。

#### 并行执行（关键性能优化）

**所有通道搜索必须并行执行——在单次响应中同时发起多个 Bash 和 WebSearch 调用，不要顺序执行。**

**Group A: API 通道（并行 Bash 调用）**
Reddit(多级轮询), Twitter(Exa), YouTube, Bilibili, 知乎, 小红书, 微博, 雪球, 微信公众号, RSS

**Group B: WebSearch 通道（并行 WebSearch 调用）**
通用网页, LinkedIn, 抖音, V2EX, 播客

两组之间也并行——Group A 和 Group B 同时启动。

#### 搜索经验复用

搜索前检查 `references/search-patterns/` 目录下是否有该话题领域的经验文件。如果有，参考历史上哪些关键词组合和通道产出了高质量结果。

#### 通道搜索实现

各通道的具体搜索代码和调用方式见 `references/channels/{通道ID}.md`。

#### 搜索失败兜底

当某通道 API 搜索失败时，不直接跳过，按以下策略兜底：

| 失败通道 | 兜底方式 |
|---------|---------|
| 知乎（cookie 过期） | `WebSearch` `site:zhihu.com ${keyword}` |
| Reddit（Tier 1/2 失败） | Tier 3: Exa API `includeDomains: ["reddit.com"]` → Tier 4: `WebSearch` `site:reddit.com` |
| Twitter（Exa 失败） | `WebSearch` `site:twitter.com OR site:x.com ${keyword}` |
| YouTube（yt-dlp 失败） | `WebSearch` `site:youtube.com ${keyword}` |
| Medium（DuckDuckGo 失败） | `WebSearch` `site:medium.com ${keyword}` |
| 小红书（MCP 服务异常） | `WebSearch` `site:xiaohongshu.com ${keyword}` |
| Bilibili（API 异常） | `WebSearch` `site:bilibili.com ${keyword}` |
| 微博（访客 Cookie 失败） | `WebSearch` `site:weibo.com ${keyword}` |
| 雪球（cookie 过期） | `WebSearch` `site:xueqiu.com ${keyword}` |
| 微信（wechat-extractor 不可用） | `WebSearch` `site:mp.weixin.qq.com ${keyword}` |

**兜底规则**：
1. 兜底结果视为「无流量数据」，走动态权重中的无流量方案
2. 每个失败通道最多尝试 **1 次**兜底，兜底也失败则跳过
3. 兜底结果在最终输出的筛选说明中标注来源

---

#### 内容提取（Fetch 降级）

当需要抓取搜索结果的完整内容时，按多级降级策略执行。详见 `references/fetch-fallback.md`。

**Fetch 前检查**：如果 `references/site-patterns/{domain}.md` 存在，先读取该域名的已知提取模式（有效 UA、可用选择器、已知陷阱），按其指导执行 Fetch。

简要层级：

| 层级 | 方式 | 默认使用 |
|------|------|---------|
| Tier 1 | WebFetch（内置工具） | 是 |
| Tier 2 | r.jina.ai（Markdown 输出） | 是 |
| Tier 3 | curl + UA 轮换 | 仅高价值内容 |
| Tier 4 | Wayback Machine | 仅高价值内容 |

---

### 步骤 3: 双重筛选

对所有搜索结果进行评分，选出最好的 10-15 条。

#### 动态权重评分机制（总分 100）

| 维度 | 有流量数据 | 无流量数据 | 评判要点 |
|------|-----------|-----------|---------|
| **流量指标** | 30 分 | 0 分 | 各通道 engagement 数据 |
| **内容质量** | 35 分 | 50 分 | 相关度 + 深度 + 完整性 |
| **时效性** | 20 分 | 30 分 | 7天内(满分) → 1月内 → 3月内 → 更早 |
| **作者权威性** | 15 分 | 20 分 | 官方 → 活跃贡献者 → 普通用户 |

**核心原则**：没有数据就不评这个维度，权重转移到可评估的维度上，不惩罚 API 限制。

**重要**：相关度评分基于「意图匹配」而非「关键词字面匹配」。

#### 信息源层级加分（±15 分）

一手开发者推文和三手新闻转载价值天差地别。在四维基础分上叠加信息源层级修正：

| 层级 | 特征 | 加分 | 示例 |
|------|------|------|------|
| **一手源** | 原创者/官方直接发布 | +15 | 开发者推文、官方 changelog、原创博客、开源 repo release |
| **二手分析** | 基于一手源的深度加工 | +8 | 技术评测、Reddit/知乎深度讨论、YouTube 深度教程 |
| **三手转述** | 简单搬运/翻译/聚合 | 0 | 新闻资讯站、翻译搬运、AI 自动摘要 |
| **低质搬运** | 标题党/洗稿/无信息增量 | -10 | 标题党新闻、多层转载、SEO 垃圾 |

**判定方法**：
- URL 域名是官方域名（如 openai.com, anthropic.com, github.com/xxx） → 一手
- 作者是产品/项目直接相关人（开发者、创始人） → 一手
- 内容包含原创截图/代码/实验数据 → 一手或二手
- 内容仅引用/转述其他来源且无新分析 → 三手
- 多个来源报道同一事件 → 优先保留最接近原始源的那条
- 当 user-dna 中 `stable.info_preference = "一手信息源"` 时，三手降权加倍（从 0 变为 -10）

叠加后总分仍以 100 分封顶、0 分保底。

#### 话题亲和度加权

评分阶段额外乘以话题亲和度系数：`final_score = base_score × (0.7 + 0.3 × affinity)`。亲和度高的通道结果天然有分数优势，亲和度低的通道结果需要更高的基础分才能入选。

#### 用户画像加分（±10 分）

当 config 中配置了 `user_profile` 时叠加画像加分。封顶 100 分、保底 0 分。

#### 平台多样性约束

- 单一通道最多贡献最终结果的 **50%**
- 最终结果必须覆盖 **≥ 3 个不同通道**

完整评分细则和参考代码见 `references/scoring.md`。

---

### 步骤 4: 雪球迭代

从首轮结果中学习——结果本身就是线索。

#### 触发条件（满足任一即触发）

| 条件 | 说明 |
|------|------|
| **新关键词发现** | 首轮结果中出现了步骤 1 未覆盖的高频术语 |
| **意图偏移** | 首轮结果偏离用户意图 |
| **信息缺口** | 首轮结果不足 10 条高质量内容 |

#### 不触发条件

- 首轮已有 10+ 条高质量（评分 ≥ 70）匹配意图的内容

#### 限制

- **最多执行 1 轮**，每轮 ≤ 30 条（2-3 个通道）

---

### 步骤 5: 条目式输出

**输出规则**

1. **始终使用条目式输出，禁止自行消化整合**
2. **输出格式**：日期 + 一段话总结 + 按评分排序的条目列表
3. **每条包含**：标题、通道、评分、流量、摘要、链接、质量亮点
4. **方法类搜索**：输出完成后询问是否需要整合成指南
5. **搜索沉淀**：输出完成后询问用户是否需要保存到 `📚 30-积累/303-知识/3036-搜索沉淀/` 目录
6. **搜后评价**：沉淀询问后，用 AskUserQuestion 收集搜索质量反馈：
   - A) 很好，正是我要的
   - B) 还行，但部分结果无关
   - C) 不好，大部分不是我想要的
   - 选 B/C 时追问"哪些类型的结果你不需要？"
   - 将反馈追加到 `~/.web-search/feedback-log.json`（含日期、查询、评分、反馈内容、偏好/排斥的通道）
   - **反馈应用**（积累 3+ 条后生效）：多次否定某通道 → 该通道亲和度 -0.1；多次肯定 → +0.1；多次反映"新闻太多" → 三手降权从 0 改为 -5

#### 摘要质量约束

- ❌ **禁止空洞开头**：不得使用"本文介绍了…"等模板式开头
- ✅ **保留具体信息**：人名、数字、日期、版本号、工具名等具体数据点必须原样保留
- ✅ **字数限制**：50-150 字
- ✅ **信息密度**：每条摘要必须让读者无需点开链接就能判断"这条对我有没有用"

#### 输出模板

```markdown
📅 ${date}

🔍 搜索关键词：${keyword}
🎯 识别意图：${intent_type} — ${intent_description}
📊 原始结果：${total_count} 条 → 筛选后：${filtered_count} 条

[一段话总结]（2-3句话概括整体发现）

---

### 1. ${title}
**通道**: ${channel} | **评分**: ${score}/100
**流量**: ${traffic_metrics} | **发布**: ${date}
**摘要**: ${summary}
**链接**: ${url}
**质量亮点**: ${quality_highlights}

---

📌 筛选说明：
- 意图识别：${intent_type}
- 搜索通道：Reddit ${n}条, Twitter ${n}条, YouTube ${n}条, Bilibili ${n}条, Medium ${n}条, 知乎 ${n}条, 小红书 ${n}条, 微博 ${n}条, V2EX ${n}条, 雪球 ${n}条, LinkedIn ${n}条, 抖音 ${n}条, RSS ${n}条, 微信 ${n}条, 播客 ${n}条, 通用网页 ${n}条
- 雪球迭代：${snowball_status}
- 筛选标准：动态权重 + 画像加分 ±10
- 平台兜底：${fallback_status}
```

---

## 通道诊断 (Doctor)

当用户说"检查搜索通道"、"诊断搜索"或类似表达时，对所有 16 个通道执行健康检查。

### 检查流程

**API 通道**（测试实际 API 调用）：

| 通道 | 检查方式 |
|------|---------|
| Reddit | GET `reddit.com/search.json?q=test&limit=1` |
| Twitter | `npx @nicepkg/bird search "test" --limit 1` 或检查 Exa key |
| YouTube | `yt-dlp "ytsearch1:test" --dump-json` |
| Bilibili | GET `api.bilibili.com/x/web-interface/search/all/v2?keyword=test&pagesize=1` |
| 知乎 | GET `zhihu.com/api/v4/search_v3?q=test&limit=1` (with cookies) |
| 小红书 | POST `localhost:18060/mcp` search count=1 |
| 微博 | 访客 Cookie 生成 + test query |
| 雪球 | GET `xueqiu.com/query/v1/search/status.json?q=test&count=1` |
| 微信 | 检查 wechat-extractor skill 可用性 |
| RSS | `python3 -c "import feedparser"` + 检查 config 中 rss_feeds |

**WebSearch 通道**（直接用 WebSearch 测试）：
通用网页、LinkedIn、抖音、V2EX、播客

### 输出格式

```
🏥 搜索通道健康检查

| 通道 | 状态 | 备注 |
|------|------|------|
| Reddit | ✅ ready | |
| Twitter | ⚠️ degraded | bird cookies 过期, Exa 可用 |
| YouTube | ✅ ready | |
| Bilibili | ✅ ready | |
| 知乎 | ❌ unavailable | z_c0 cookie 过期 |
| 小红书 | ✅ ready | |
| 微博 | ✅ ready | 访客 Cookie 自动生成 |
| V2EX | ✅ ready | WebSearch 模式 |
| 雪球 | ❌ unavailable | 未配置 xueqiu_cookie |
| LinkedIn | ✅ ready | WebSearch 模式 |
| 抖音 | ✅ ready | WebSearch 模式 |
| RSS | ⚠️ degraded | feedparser 已安装, 未配置 rss_feeds |
| 微信 | ❌ unavailable | wechat-extractor 未运行 |
| 播客 | ✅ ready | WebSearch 模式 |
| 通用网页 | ✅ ready | |

状态：12/16 通道可用
```

---

## 站点经验库

`references/site-patterns/` 目录存储特定域名的内容提取经验，在 Fetch 时参考。

### 文件格式

```markdown
---
domain: example.com
aliases: [alias1, alias2]
updated: 2026-03-24
---

## 平台特征
架构、反爬措施、登录需求

## 有效模式
验证过的 URL 规律、提取策略、有效的 CSS 选择器

## 已知陷阱
什么方法行不通以及原因
```

### 使用规则

- Fetch 前自动匹配域名 → 读取对应经验文件
- 搜索过程中发现新的域名提取模式时，自动追加到经验文件
- 只记录验证过的事实，不写未确认的猜测

---

## 搜索经验沉淀

按话题领域积累搜索策略经验。存储位置：`references/search-patterns/`。

当一次搜索产出了高质量结果，在输出结果后记录：

```markdown
---
domain: ai-agent
updated: 2026-03-24
---

## 有效策略
- 关键词组合：`Claude Code skill` + `SOUL.md template` 在 Reddit 产出最佳
- 通道侧重：此话题 Reddit > Medium > 知乎

## 已知陷阱
- 知乎搜 "AI Agent" 营销号为主
```

---

## 配置管理

### 配置文件位置

`~/.web-search/config.json`

### 配置项

```json
{
  "default_channels": [
    "reddit", "twitter", "medium", "youtube", "zhihu", "xiaohongshu",
    "bilibili", "weibo", "v2ex", "xueqiu", "linkedin", "douyin",
    "rss", "wechat", "podcast", "general_web"
  ],
  "max_results_per_channel": {
    "reddit": 30, "twitter": 30, "medium": 20, "youtube": 20,
    "zhihu": 20, "xiaohongshu": 20, "bilibili": 20, "weibo": 20,
    "v2ex": 15, "xueqiu": 15, "linkedin": 10, "douyin": 10,
    "rss": 15, "wechat": 10, "podcast": 10, "general_web": 20
  },
  "output_count": 15,
  "snowball_max_rounds": 1,
  "rss_feeds": [],
  "user_profile": {
    "identity": "",
    "focus": [],
    "low_priority": []
  },
  "credentials": {
    "twitter_auth_token": "",
    "twitter_ct0": "",
    "exa_api_key": "",
    "zhihu_z_c0": "",
    "zhihu_d_c0": "",
    "xueqiu_cookie": ""
  }
}
```

### 凭证管理

| 通道 | 凭证字段 | 获取方式 | 有效期 |
|------|---------|---------|--------|
| Twitter (bird) | `twitter_auth_token`, `twitter_ct0` | Cookie-Editor 浏览器扩展 | 不固定 |
| Twitter (Exa) | `exa_api_key` | https://exa.ai 注册 | 长期 |
| 知乎 | `zhihu_z_c0`, `zhihu_d_c0` | 浏览器复制 Cookie | ~3 个月 |
| 雪球 | `xueqiu_cookie` | 浏览器复制 Cookie | ~1 个月 |
| 小红书 | MCP 自管理 | 运行 login 工具扫码 | ~3 个月 |
| 微博 | 自动生成 | 访客 Cookie 自动获取 | 单次会话 |
| 微信 | 跨 skill | 依赖 wechat-extractor 配置 | - |
| Reddit | 不需要 | 公开 API | - |
| YouTube | 不需要 | yt-dlp | - |
| Bilibili | 不需要 | 公开 API | - |
| Medium | 不需要 | DuckDuckGo | - |
| V2EX | 不需要 | 公开 API + WebSearch | - |
| LinkedIn | 不需要 | WebSearch | - |
| 抖音 | 不需要 | WebSearch | - |
| RSS | 不需要 | feedparser (需 pip install) | - |
| 播客 | 不需要 | WebSearch | - |

---

## 执行规则

### 搜索流程（6 步 + 前置检查）

0. **凭证验证**：读取配置文件，检查凭证有效性；缺失时询问用户补充或跳过
1. **意图识别**：分析用户输入，判断意图类型；存在歧义时用 AskUserQuestion 澄清
2. **关键词生成**：基于意图生成核心词 + 扩展词 + 通道定向词
3. **并行搜索**：根据意图选择通道，**并行执行所有通道搜索**（100-160 条）
4. **雪球迭代**：从首轮结果中学习，最多 1 轮
5. **双重筛选**：动态权重评分 + 画像加分 → 10-15 条
6. **条目输出**：按模板输出，询问是否沉淀保存

### 底线规则

- ❌ 不把搜索结果消化成"指南"——用户需要原始信息源
- ❌ 不跳过意图识别——歧义搜索浪费所有后续通道额度
- ❌ 不在意图有歧义时自行假设——猜错方向的结果对用户毫无价值
- ❌ 不对低价值内容（评分 < 80）使用 Tier 3/4 Fetch
- ❌ 不在凭证缺失时静默跳过通道——用户不知道通道被跳过

---

## 版本历史

### V5.1（2026-03-24）
- **用户 DNA 建档**：首次使用采集身份/领域/偏好/受众，个性化解读搜索意图
- **信息源层级评分**：一手源+15 / 二手分析+8 / 三手转述0 / 低质搬运-10，新闻转述不再淹没原创内容
- **话题-平台亲和矩阵**：8 话题领域 × 16 通道的量化亲和度（0-1），替代旧的二元选/不选逻辑
- **最低通道约束**：至少 6 通道，中文≥2 英文≥2，防止搜太少
- **搜后评价反馈**：A/B/C 三级评价 + 反馈积累校准亲和度
- **亲和度加权评分**：`base_score × (0.7 + 0.3 × affinity)`，高亲和通道结果有分数优势

### V5.0（2026-03-24）
- **16 通道架构**：新增 Bilibili、微博、V2EX、雪球、LinkedIn、抖音、RSS、微信公众号、播客 9 个通道
- **模块化通道文件**：每通道独立 `references/channels/{id}.md`，含搜索实现+评分阈值+已知问题
- **并行搜索**：所有通道搜索并行执行（Group A: API Bash 并行 + Group B: WebSearch 并行）
- **通道诊断 (Doctor)**：一键检测 16 通道健康状态，输出状态表格
- **bird CLI 替代 Exa**：Twitter 搜索主方式改为 bird CLI（零费用+engagement 指标），Exa 降为备选
- **XHS 结果精简**：小红书 MCP 响应仅保留 7 个核心字段，大幅节省 token
- **站点经验库**：`references/site-patterns/` 按域名积累 Fetch 提取经验
- **scoring.md 重构**：平台阈值迁入 channel 文件，scoring.md 精简为纯框架
- 保留 V4.0 的搜索策略哲学、意图识别、雪球迭代、摘要质量约束、画像加分等成熟机制

### V4.0（2026-03-24）
- 搜索策略哲学、平台选择灵活化、搜索经验沉淀、摘要质量约束、用户画像加分

### V3.x（2026-03-09 ~ 2026-03-10）
- 意图识别、结构化关键词、通用网页、雪球迭代、Fetch 降级、动态权重、凭证验证

### V2.0（2026-03-06）
- 广搜+精筛策略、双重筛选、条目式输出

### V1.0（2026-03-05）
- 初始版本

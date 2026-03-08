---
name: style-writing
description: >
  风格学习 + 内容创作一站式技能。从参考文章深度分析结构档案，或基于结构档案+素材进行内容创作。
  触发场景：(1) 用户说"风格学习"、"学习风格"、"提取风格"、"分析结构" (2) 用户说"风格写作"、"仿写"、"风格创作"、"写文章"
  (3) 用户提供参考文章并要求分析写作结构 (4) 用户提供选题/观点/干货方法要求创作内容。
  支持多风格档案、个人IP知识库迭代积累。
---

# Style Writing

风格结构学习 + 素材驱动创作一站式技能。

## 模式路由

使用 AskUserQuestion 询问用户选择模式：

| 模式 | 触发词 | 说明 |
|------|--------|------|
| **风格学习** | 学习风格、提取风格、分析结构 | 从参考文章深度分析结构，生成结构档案 |
| **内容创作** | 风格写作、仿写、创作、写文章 | 基于结构档案+素材（选题/观点/干货方法）创作 |

---

## Mode 1: 风格学习（结构深度分析）

### 步骤 1: 路径确认（首次使用必须执行）

读取 `references/personal-kb.md`，检查是否已记录结构档案保存路径。

- **已有路径**：直接使用，无需询问
- **无路径（首次）**：使用 AskUserQuestion 询问保存位置，记录到 `references/personal-kb.md`

### 步骤 2: 接收参考文章

1. 接收用户提供的参考文章（文件夹路径 / 单篇文件 / 文章文本）
2. 全量读取所有文件，不遗漏
3. 告知用户共读取了几篇，开始分析

### 步骤 3: 结构深度分析

**唯一分析目标：结构。除结构以外的一切元素（词汇风格、情绪调性、主题内容、价值观等）一律忽略，不分析、不记录。**

以下九个维度是**基础框架**，必须全部分析。在此基础上，通读参考文章后，**主动判断是否存在额外的结构特征**——如果发现文章中有某种显著的、可复用的结构规律，但不属于九个基础维度，则作为**扩展维度**追加分析。

扩展维度判断标准（满足任意一条即追加）：
- 该结构在多篇参考文章中重复出现
- 该结构对文章的整体组织方式有显著影响
- 该结构是这个作者/账号的明显个人习惯

扩展维度示例（不限于此，根据实际文章发现）：
- 对话结构（作者与读者的虚拟问答节奏）
- 悬念节点结构（在哪些位置制造信息缺口，如何布置和释放）
- 视觉节奏结构（换行、空行、符号的视觉布局规律）
- 数字/列表结构（编号列表的使用时机、格式、深度）
- 引用/援引结构（如何引入他人说法，前后如何处理）
- 自我披露结构（作者以何种形式出现在文章中，频率和位置）
- 层层剥笋结构（信息递进揭示的节奏，每一层在哪里）

每个维度（包括扩展维度）必须给出具体模式描述，不得泛泛而谈。

---

#### 维度一：文章整体结构

- 全文骨架类型（总-分-总 / 递进式 / 并列式 / 问题-分析-方案 / 故事弧线型 / 其他）
- 各模块的比例关系（开头占比 / 正文主体占比 / 结尾占比，估算字数比）
- 模块之间的连接方式（硬切 / 过渡句 / 小标题分割 / 留白跳转）
- 信息密度分布（哪个模块信息最密集，哪个最稀疏）

#### 维度二：开头结构

- 开头的进入方式（场景切入 / 问题抛出 / 结论先行 / 数据开场 / 反常识切入 / 故事引入 / 金句起笔 / 其他）
- 从第一句到正式进入主题，经历几步、每步做什么
- 开头与主体内容的衔接方式（直接硬接 / 过渡句连接 / 悬念延伸）
- 开头的长度模式（极短型≤3句 / 短型4-6句 / 中型7-10句 / 长型>10句）

#### 维度三：开头黄金三句结构

**单独拆解第一、二、三句各自的句法功能：**

- 第一句：句法角色（钩子 / 画面 / 断言 / 问题 / 数据 / 其他）+ 句子结构（主谓宾 / 倒装 / 问句 / 感叹句）
- 第二句：与第一句的关系（补充说明 / 转折 / 递进 / 具体化 / 情绪升温）
- 第三句：完成何种功能（建立共鸣 / 引发好奇 / 抛出矛盾 / 定锚主题 / 其他）
- 三句合力形成的整体结构模式，用一句话总结（如：「画面→共鸣→问题」型）

#### 维度四：结尾结构

- 结尾的收束方式（金句收尾 / 行动号召 / 情绪余韵 / 反问留白 / 回扣开头 / 升华总结 / 其他）
- 结尾从主体内容退出的节奏（急刹车型 / 渐缓型 / 突然反转型）
- 结尾长度模式（1句内 / 2-3句 / 1段 / 多段）
- 最后一句的句法特征（陈述 / 反问 / 祈使 / 感叹）

#### 维度五：正文主体结构

- 内容组织逻辑（时间线 / 逻辑递进 / 问题拆解 / 案例堆叠 / 对比并置 / 其他）
- 小节/模块的数量规律（固定几节 / 灵活变化）
- 各节内部的微结构（观点句 + 论据 / 场景 + 分析 / 问题 + 回答 / 其他）
- 节与节之间如何推进（逻辑递进 / 情绪递进 / 平行展开 / 反转跳跃）

#### 维度六：段落结构

- 段落长度分布（全文段落的字数范围，最短段 / 最长段 / 平均段）
- 段落长短的排列规律（长-短交替 / 先长后短 / 密集短段聚集区 / 其他）
- 单段内部的句子组织方式（单句一段 / 首句主题+展开 / 中心句在末尾 / 无中心句散漫型）
- 段落之间是否有视觉分隔（空行 / 小标题 / 无分隔直接连续）

#### 维度七：句子结构

- 句子长短分布（短句为主≤15字 / 长短混合 / 长句为主≥25字）
- 常用句型（疑问句 / 感叹句 / 排比句 / 祈使句 / 陈述句）各自的出现频率和位置规律
- 句子内部的节奏切分方式（逗号多 / 顿号多 / 破折号 / 省略号 / 其他标点）
- 特殊句式的使用规律（倒装 / 无主句 / 插入语 / 其他）

#### 维度八：表达结构

- 论证的结构模型（先论后据 / 先据后论 / 夹叙夹议 / 只叙不论 / 其他）
- 举例的结构方式（单例深挖 / 多例并列 / 例后拆解 / 例后留白不解释）
- 转折与递进的结构惯用法（如何制造转折、如何层层推进）
- 抽象与具体的切换节奏（先抽象后具体 / 先具体后抽象 / 交替出现）

#### 维度九：遣词造句结构

**注意：此维度只分析词语在句子中的结构位置和搭配规律，不分析词汇的风格/情绪/调性。**

- 修饰语的位置习惯（定语前置 / 定语后置 / 状语位置规律）
- 动词的结构使用（动词短语 / 动宾结构 / 连动句）
- 数字/量词的结构惯用（如何嵌入数据，前置还是后置，是否单独成句）
- 重复结构的使用规律（同一句式的重复出现频率和位置，如排比的间距）

---

### 步骤 4: 生成结构档案文件

1. 读取 `references/personal-kb.md` 获取保存路径
2. 检查目标文件夹现有文件，确定档案编号（查看已有最高编号，自动递增）
3. 询问用户此档案命名（账号名/风格名）
4. 文件命名：`{编号}-{账号名或风格名}-结构档案.md`
5. 写入内容：九个维度的完整分析结果，每个维度用二级标题分隔

文件结构示例：
```markdown
# {账号名} 结构档案

分析文章数：X篇
分析日期：YYYY-MM-DD

## 一、文章整体结构
...

## 二、开头结构
...

## 三、开头黄金三句结构
...

## 四、结尾结构
...

## 五、正文主体结构
...

## 六、段落结构
...

## 七、句子结构
...

## 八、表达结构
...

## 九、遣词造句结构
...
```

6. 保存文件，告知用户路径，风格学习完成

---

## Mode 2: 内容创作

### 步骤 1: 素材接收与初始确认

接收用户提供的素材，识别类型：

| 类型 | 判断标准 | 后续处理 |
|------|----------|----------|
| **A 爆款选题** | 一个话题/问题/现象，无附加立场 | → 选题评估分析 |
| **B 观点** | 一个主张/判断/结论（无明确选题范围） | → 找论据和案例 |
| **C 干货方法** | 一套方法/步骤/技巧（无明确选题范围） | → 逆向分析问题和人群 |
| **D 选题+用户立场** | 一个话题 + 用户附加的看法/观点/方法/干货 | → 拆层定锚 + 围绕用户立场深化 |

**D 类型识别规则**：当用户同时提供了一个选题方向，并且附加了自己的看法、观点、方法或干货内容时，归为 D 类型。关键判断标志：用户的输入中既有「话题/现象」，又有「我觉得…」「我的方法是…」「我认为…」或类似的个人立场表达。

类型识别后，立即完成两项确认（通过 AskUserQuestion）：

**① 结构档案选择**
- 扫描 personal-kb.md 记录的结构档案保存路径，读取所有可用档案
- 使用 AskUserQuestion 提供两个选项：
  - 「所有风格（默认）」——每个风格档案各创作一篇独立文章
  - 「仅使用01号风格」——只用编号01的档案创作一篇
- 用户可通过 Other 自定义输入（如指定某几个档案、排除某个等）

**创作数量规则**：选了几个档案就出几篇独立文章。素材分析（步骤2）和网络搜集（步骤3）只做一次，共享给所有文章；标题设计（步骤4）只做一次，所有文章共用同一组标题；创作（步骤6）按每个档案分别执行，每篇文章使用不同的结构组合

**② 目标字数**
- 读取 personal-kb.md 中的默认字数设置
- 选项：「1200字左右（默认）」/「800字左右」/「1500字左右」/「1800字左右」/ Other 自定义

确认完成后，读取所选结构档案 + 结构使用清单（了解上次使用过的结构，本次优先选用低频结构），全程复用。

---

### 步骤 2: 素材深度分析

根据类型执行对应分析：

#### 类型A：爆款选题分析

按以下四步完成，每步都必须输出具体结论：

**① 时效性判断**
- 常青选题 or 时效性选题？
- 如果是时效性选题：事件发生时间是什么时候？现在还在热度期内吗？是否已过时？
- 结论：可写 / 需转化为常青角度 / 已过时不建议写

**② 人群广度评估**
- 小众话题 or 大众话题？
- 从人群趋势分析：哪些年龄层、职业群体、生活状态的人会关心这个？
- 从圈层趋势分析：这件事是个例，还是在某个圈层里具有代表性？是哪个圈层？
- 结论：预估潜在读者人群描述

**③ 深度挖掘**
- 基于选题本身，还能提出哪些问题？（至少3个延伸问题）
- 这些问题中，哪些有数据支撑？哪些有研究资料？
- 找到新的信息层：有没有比表面现象更深一层的解释或规律？
- 结论：列出2-3个可写的深度素材点

**④ 一句话框架**
- 能否用一句话说清楚：切口（从哪里进）+ 延展（能展开多大）+ 逻辑（怎么论证）+ 落点（读者带走什么）？
- 输出这句话，格式：「从【切口】出发，延展到【延展方向】，通过【逻辑方式】，落点在【读者收获】」

---

#### 类型B：观点分析

**① 观点澄清**
- 这个观点的核心主张是什么？（用一句话重新表述，去掉模糊性）
- 这个观点有没有隐含的前提条件？

**② 论据搜寻**
- 有哪些现实案例可以支撑这个观点？（找2-4个，来源：社会现象/身边故事/公开事件）
- 有没有数据/研究可以佐证？
- 有没有反例？反例如何反转或融入论证？

**③ 论证结构**
- 这个观点用什么论证逻辑最有说服力？（归纳法/演绎法/对比法/因果链）
- 结论：给出论证框架草图

---

#### 类型C：干货方法分析

**① 逆向溯源**
- 这个方法解决的是什么具体问题？
- 这个问题属于哪个层面？（效率问题/认知问题/情绪问题/关系问题/其他）

**② 人群定位**
- 什么人群最需要这个方法？
- 这个人群的日常状态是什么？（具体描述，不要泛化）
- 他们已经尝试过哪些其他方式但没有解决？

**③ 痛点挖掘**
- 这个人群真正的痛点是什么？（表层痛点 vs 深层痛点）
- 他们最怕什么？最想要什么？
- 结论：写出核心读者痛点一句话描述

---

#### 类型D：选题 + 用户立场分析

**核心原则：用户的输入 = 文章灵魂。创作任务不是「从零探索角度」，而是「深化和构建用户已给出的方向」。**

**① 拆层**
- 明确分离两个层次：
  - **选题范围**：用户提到的话题/现象/领域是什么？（这决定了研究和素材搜集的边界）
  - **用户立场**：用户附加的看法/观点/方法/干货是什么？（这决定了文章的核心论点和独特角度）
- 输出格式：
  - 选题范围：一句话描述
  - 用户立场：一句话提炼（将用户原始表述提炼为更锋利、更明确的核心论点）

**② 立场锐化**
- 用户的原始表述可能比较粗糙/片面/口语化，需要提炼但不能偏离
- 将用户立场提炼为一句清晰的核心论点，遵守以下规则：
  - 保留用户的核心意思，不得反转或替换
  - 去掉模糊性，让立场更明确
  - 如果用户给了多个碎片观点，找到它们之间的逻辑线，串成一个连贯主张
- 输出锐化后的核心论点，供用户确认（如果与原意差异较大，标注出来）

**③ 选题维度分析**（借用 A 类型的框架，但方向已锁定）
- 时效性判断：同 A 类型①
- 人群广度评估：同 A 类型②，但重点评估「对用户立场有共鸣的人群」而非泛泛的话题人群
- 深度挖掘：围绕用户立场展开，不是开放式探索
  - 用户立场的深层逻辑是什么？（为什么这个看法成立？）
  - 有哪些维度可以支撑这个立场？（数据/案例/逻辑推演/反面论证）
  - 最可能的反对意见是什么？如何在文章中预先回应？

**④ 一句话框架**
- 格式同 A 类型，但切口和落点必须与用户立场一致：
- 「从【切口】出发，延展到【延展方向】，通过【逻辑方式】，落点在【读者收获】」
- 切口 = 用户立场的最佳进入点；落点 = 读者认同用户立场后带走的东西

---

分析完成后，输出完整的素材分析报告，进入网络素材搜集阶段。

---

### 步骤 3: 网络素材搜集

基于素材分析报告确定的核心方向和延伸问题，在多个平台搜集真实素材，丰富创作原料。

#### 搜索渠道说明

各平台方案汇总：

| 平台 | 工具/方式 | 安装 | 是否需要登录 | 关键词语言 |
|------|---------|------|------------|-----------|
| **微博** | requests 移动端 API | 系统自带 | 浏览器复制一次 Cookie | 中文 |
| **Reddit** | requests 公开 JSON API | 系统自带 | 不需要，零配置 | **英文**（选题自动翻译） |
| **知乎** | requests 脚本 | 系统自带 | 浏览器复制一次 Cookie | 中文 |
| **小红书** | xiaohongshu-mcp（按需启停） | 一次性下载二进制+扫码登录 | Cookie 由工具持久化管理 | 中文 |
| **Twitter/X** | Exa 语义搜索 + Jina Reader | Exa 需 API key | 不需要登录，不触碰 Twitter | **英文**（选题自动翻译） |
| **YouTube/B站** | yt-dlp 字幕提取 | `brew install yt-dlp` | 不需要，零配置 | **英文**(YT) / 中文(B站) |
| **任意网页** | Jina Reader API | 系统自带 | 不需要，零配置 | — |

**英文关键词说明（Reddit / Twitter / YouTube）**：搜索前将中文选题核心词翻译为英文，目的是获取国际视角的观点、案例和数据，作为补充素材维度。

---

#### 各平台搜索方式

**微博 — requests 调用移动端 API（需一次性配置 Cookie）**

Cookie 获取方式：登录 weibo.com → 开发者工具（F12）→ Network → 找任意请求 → Request Headers → 复制 `Cookie` 字段中 `SUB=` 后面的值，存入 `references/personal-kb.md` 的「搜索凭证」区块。

```python
import requests, re
from urllib.parse import quote

def search_weibo(keyword, cookie_sub, page=1, start_time=None, end_time=None):
    """
    start_time / end_time 格式：'2024-01-01'，不填则不限时间
    """
    url = "https://m.weibo.cn/api/container/getIndex"
    containerid = f"100103type=1&q={quote(keyword)}"
    if start_time and end_time:
        containerid += f"&xsort=hot&suball=1&timescope=custom:{start_time}-0:{end_time}-0"
    headers = {
        "Cookie": f"SUB={cookie_sub}",
        "Referer": "https://m.weibo.cn/",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15",
        "MWeibo-Pwa": "1",
        "X-Requested-With": "XMLHttpRequest",
    }
    params = {"containerid": containerid, "page_type": "searchall", "page": page}
    r = requests.get(url, headers=headers, params=params, timeout=10)
    cards = r.json().get("data", {}).get("cards", [])
    results = []
    for card in cards:
        if card.get("card_type") == 9:
            mb = card.get("mblog", {})
            text = re.sub(r"<[^>]+>", "", mb.get("text", ""))  # 去除 HTML 标签
            results.append({
                "text": text,
                "user": mb.get("user", {}).get("name", ""),
                "reposts": mb.get("reposts_count", 0),
                "comments": mb.get("comments_count", 0),
                "likes": mb.get("attitudes_count", 0),
                "created_at": mb.get("created_at", ""),
            })
    return results
```

**Reddit — requests 公开 JSON API（零配置，直接执行）**

```python
import requests

def search_reddit(keyword, limit=25):
    url = "https://www.reddit.com/search.json"
    headers = {"User-Agent": "ContentResearch/1.0"}
    params = {"q": keyword, "sort": "top", "t": "year", "limit": limit}
    r = requests.get(url, headers=headers, params=params, timeout=10)
    posts = r.json()["data"]["children"]
    return [{"title": p["data"]["title"],
             "text": p["data"]["selftext"][:500],
             "score": p["data"]["score"]} for p in posts]
```

**知乎 — requests 脚本（需浏览器复制一次 Cookie 存入 personal-kb.md）**

```python
import requests

def search_zhihu(keyword, z_c0, d_c0, offset=0, limit=20):
    url = "https://www.zhihu.com/api/v4/search_v3"
    params = {"q": keyword, "offset": offset, "limit": limit,
              "sort": "default", "vertical": "general"}
    headers = {
        "Cookie": f"z_c0={z_c0}; d_c0={d_c0}",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Referer": "https://www.zhihu.com/",
        "x-zse-93": "101_3_3.0",
    }
    r = requests.get(url, headers=headers, params=params, timeout=10)
    items = r.json().get("data", [])
    results = []
    for item in items:
        obj = item.get("object", {})
        results.append({
            "type": obj.get("type", ""),
            "title": obj.get("question", {}).get("title", "") or obj.get("title", ""),
            "content": obj.get("content", obj.get("excerpt", ""))[:500],
            "author": obj.get("author", {}).get("name", ""),
            "votes": obj.get("voteup_count", 0),
        })
    return results
```

Cookie 存入 `references/personal-kb.md` 的「搜索凭证」区块，失效时重新从浏览器复制。
关键字段：`z_c0`（登录态）和 `d_c0`（设备码），登录 zhihu.com 后从开发者工具复制。

**小红书 — xiaohongshu-mcp（按需启停，无需常驻后台）**

二进制已安装于 `~/Library/Application Support/xiaohongshu-mcp/`，Cookie 已持久化，可直接使用。

每次搜索时执行（skill 自动调用）：

```bash
# 启动服务（后台，记录 PID）
/path/to/xiaohongshu-mcp-darwin-arm64 &
XHS_PID=$!
sleep 2  # 等待服务就绪

# 调用搜索（MCP HTTP 接口）
curl -s -X POST http://localhost:18060/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"search_feeds","arguments":{"keyword":"关键词"}},"id":1}'

# 关闭服务
kill $XHS_PID
```

Cookie 失效时重新运行 login 工具扫码即可，无需其他操作。

**Twitter/X — Exa 语义搜索 + Jina Reader（零风险，不触碰 Twitter 账号）**

⚠️ **禁止直接访问 Twitter API 或使用 Cookie 模拟登录**，会导致封号。本方案通过第三方索引搜索推文内容，完全不接触 Twitter。

**搜推文 — Exa 语义搜索**

Exa 有专用的推文索引（`category: "tweet"`），直接搜索推文内容，比 `includeDomains` 过滤更精准。支持语义理解，不只是关键词匹配。

```python
import requests

def search_twitter_via_exa(keyword, exa_api_key, num_results=10):
    """通过 Exa 推文索引搜索推文，不触碰 Twitter"""
    url = "https://api.exa.ai/search"
    headers = {
        "x-api-key": exa_api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "query": keyword,
        "numResults": num_results,
        "category": "tweet",
        "type": "auto",
        "contents": {
            "text": {"maxCharacters": 500}
        }
    }
    r = requests.post(url, headers=headers, json=payload, timeout=15)
    data = r.json()
    results = []
    for item in data.get("results", []):
        results.append({
            "title": item.get("title", ""),
            "text": item.get("text", ""),
            "url": item.get("url", ""),
            "author": item.get("author", ""),
            "published_date": item.get("publishedDate", ""),
        })
    return results
```

**读单条推文 — Jina Reader（免费，无需认证）**

当需要读取某条推文的完整内容时，通过 Jina Reader 渲染，不直接访问 Twitter：

```python
import requests

def read_tweet_via_jina(tweet_url):
    """通过 Jina Reader 读取单条推文内容，零风险"""
    jina_url = f"https://r.jina.ai/{tweet_url}"
    headers = {"Accept": "text/markdown"}
    r = requests.get(jina_url, headers=headers, timeout=15)
    return r.text
```

**YouTube/B站 — yt-dlp 字幕提取（零配置）**

视频创作者的口播内容 = 文字素材金矿。通过提取视频字幕获取文本内容，不需要看视频。

安装（一次性）：`brew install yt-dlp`

```python
import subprocess, json, re

def search_youtube(keyword, max_results=5):
    """搜索 YouTube 视频并提取字幕"""
    # 第一步：搜索视频
    cmd = [
        "yt-dlp", f"ytsearch{max_results}:{keyword}",
        "--dump-json", "--no-download", "--flat-playlist"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    videos = []
    for line in result.stdout.strip().split("\n"):
        if line:
            data = json.loads(line)
            videos.append({
                "title": data.get("title", ""),
                "url": data.get("url", data.get("webpage_url", "")),
                "channel": data.get("channel", data.get("uploader", "")),
                "view_count": data.get("view_count", 0),
                "duration": data.get("duration", 0),
            })
    return videos

def extract_subtitles(video_url, lang="en"):
    """提取视频字幕为纯文本（YouTube 用 en，B站用 zh）"""
    cmd = [
        "yt-dlp", video_url,
        "--write-auto-sub", "--sub-lang", lang,
        "--skip-download", "--sub-format", "json3",
        "-o", "/tmp/yt_sub_%(id)s"
    ]
    subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    # 查找生成的字幕文件
    import glob
    sub_files = glob.glob("/tmp/yt_sub_*.json3")
    if not sub_files:
        return ""
    with open(sub_files[-1], "r") as f:
        sub_data = json.load(f)
    # 提取纯文本
    texts = []
    for event in sub_data.get("events", []):
        segs = event.get("segs", [])
        text = "".join(s.get("utf8", "") for s in segs).strip()
        if text and text != "\n":
            texts.append(text)
    return " ".join(texts)

def search_bilibili(keyword, max_results=5):
    """搜索B站视频"""
    cmd = [
        "yt-dlp", f"bilisearch{max_results}:{keyword}",
        "--dump-json", "--no-download", "--flat-playlist"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    videos = []
    for line in result.stdout.strip().split("\n"):
        if line:
            data = json.loads(line)
            videos.append({
                "title": data.get("title", ""),
                "url": data.get("url", data.get("webpage_url", "")),
                "channel": data.get("channel", data.get("uploader", "")),
                "view_count": data.get("view_count", 0),
            })
    return videos
```

**使用策略**：
- 先搜索找到相关视频 → 选择播放量高、标题相关的 → 提取字幕获取口播文本
- YouTube 字幕语言用 `en`，B站用 `zh`
- 提取的字幕文本作为「观点模块」或「案例模块」的素材来源

**任意网页 — Jina Reader（免费万能阅读器）**

当搜索结果中发现有价值的文章链接，需要读取全文内容时使用：

```python
import requests

def read_webpage(url):
    """将任意网页转为干净的 Markdown 文本"""
    jina_url = f"https://r.jina.ai/{url}"
    headers = {"Accept": "text/markdown"}
    r = requests.get(jina_url, headers=headers, timeout=15)
    return r.text
```

**使用场景**：微博/知乎/Reddit 搜索结果中提到了某篇报告或文章链接 → 用 Jina Reader 读取全文 → 提取数据或案例

---

#### Cookie / API Key 更新说明

Cookie 过期时，从浏览器开发者工具（F12 → Application → Cookies）复制对应字段，更新 `references/personal-kb.md` 中「搜索凭证」区块即可。

**各平台关键凭证字段：**
- 微博：`SUB`（登录 m.weibo.cn 后复制）
- 知乎：`z_c0` + `d_c0`（登录 zhihu.com 后复制）
- 小红书：运行 `xiaohongshu-login` 工具重新扫码
- Exa：API key 从 https://exa.ai 注册获取（免费额度），存入 personal-kb.md「搜索凭证」区块
- YouTube/B站、Jina Reader：无需凭证

#### 搜集规则

**按模块收集，不混在一起：**

- **数据模块**：统计数据、调查报告、研究结论、具体数字
  - 记录数据来源、发布机构、发布时间
  - 优先近两年内的数据

- **观点模块**：不同人的看法、专家意见、大众反应、争议声音
  - 每个观点记录来源账号/身份
  - 至少收集 2-3 个不同立场或视角的观点，**不能全部来自同一个人**
  - 包括支持性观点和反对性观点（反例同样有价值）

- **案例模块**：真实故事、具体事件、用户经历、典型案例
  - 记录案例的基本要素（人物背景/事件经过/结果）
  - 优先有细节的真实案例，不要泛泛的"有人说"

**搜索策略：**
- 优先搜索核心话题词，再搜索延伸关键词
- 每个平台不必面面俱到，根据话题特性选择最匹配的平台：
  - 职场话题 → 优先知乎
  - 生活方式 → 优先小红书
  - 社会议题 → 优先微博
  - 国际视角/英文观点 → 优先 Reddit、Twitter（Exa）
  - 深度讲解/方法论 → 优先 YouTube/B站（字幕提取）
  - 搜索中发现的优质文章链接 → 用 Jina Reader 读取全文
- 搜集量不设上限，但每个模块至少找到 2-3 条有效素材
- **D 类型专项**：搜集方向围绕用户立场展开，重点找三类素材：① 支撑用户立场的案例/数据 ② 用户立场的反面观点（用于文章中预先回应） ③ 能让用户立场更具体/更生动的细节素材。不要搜集与用户立场无关的泛泛素材

#### 输出格式

搜集完成后，按模块整理输出：

```
【素材库】

▌数据模块
- [数据1] 来源：xxx，时间：xxx
- [数据2] 来源：xxx，时间：xxx

▌观点模块
- [观点1] 来源账号/身份：xxx，平台：xxx
- [观点2] 来源账号/身份：xxx，平台：xxx
- [反向观点] 来源：xxx

▌案例模块
- [案例1] 人物/背景：xxx，核心细节：xxx，来源：xxx
- [案例2] ...
```

---

### 步骤 4: 标题设计

读取 `references/title-creation-guide.md`（**仅用于查阅6种微调手法的定义和示例**）和 `references/personal-kb.md`（标题偏好）。

**⚠️ 重要：title-creation-guide.md 中的"微调版5个+重写版5个"分配方式不适用于本流程。本流程的标题数量和格式以下方规则为准，guide 仅作为微调手法的参考工具书。**

**根据素材类型，执行不同标题策略：**

#### A 爆款选题 / D 选题+用户立场（有明确选题标题时） → 1+9 微调格式

**严格执行，不得变通：**

- **第1个（原题保留）**：直接使用用户提供的选题原文，一字不改
- **第2-10个（9个微调版）**：在原题骨架不变的基础上微调，遵守以下规则：
  - 每个标题只用1-2种微调手法（从 title-creation-guide.md 的6种手法中选取）
  - **原题的核心词、核心句式必须保留**，只做局部微调
  - **禁止重写**：不得改变原题的整体句式结构，不得换成完全不同的表述
  - 9个微调版之间尽量覆盖不同的手法组合，避免9个都用同一种手法

**6种微调手法速查（详见 title-creation-guide.md）：**
1. 词汇升级（普通词→高级感词）
2. 增加极端词（真正/所有/只有/终身/根本）
3. 数字具象化（"几个"→"三个"）
4. 调整节奏（添加标点改呼吸感）
5. 括号补充（添加价值锚点或反转）
6. 句式微调（疑问↔陈述、肯定↔否定）

#### B 观点 / C 干货方法 / D 选题+用户立场（无明确选题标题时） → 10个全新标题

- **全新设计（10个）**：基于素材分析报告中的核心话题词，从零设计
- 覆盖至少5种不同结构模式（参考 title-creation-guide.md 的8种结构模式）
- 标题中的核心话题词必须保持一致，不可偏移
- D 类型的标题需体现用户立场的独特切角

**不询问确认**：所有标题随初稿一起交付，放在文章最前面。

---

### 步骤 5: 创作准备

读取 `references/personal-kb.md`（个人IP档案、偏好、路径配置）。

结构档案、字数、结构使用清单已在步骤1完成确认和读取，此处直接复用，无需重复询问。

---

### 步骤 6: 文章创作

**严格按照以下规则执行，不得添加额外流程：**

**多风格多篇创作规则**：
- 如果步骤1选择了多个单独档案 → 按每个档案各创作一篇独立文章
- 每篇文章必须使用不同的结构组合（不同的开头方式、整体骨架、论证模型等）
- 按档案顺序依次创作，每篇完成后再创作下一篇
- 每篇文章前标注使用的档案名称

**必须读取并使用：**
- 结构档案（已在步骤1读取）
- personal-kb.md 中的个人IP档案部分

**明确禁止：**
- 不做审校流程
- 不读取 Case 参考文章
- 不做反AI特征检查
- 不做风格还原度评估
- 不做任何形式的质量自检

**素材筛选原则（写作前必须执行）：**

从步骤 3 的素材库中，筛选进入文章的素材，遵守以下规则：
- **强关联优先**：只选与文章核心论点直接相关的素材，弱关联素材宁可不用
- **来源多样**：同一模块（数据/观点/案例）中，不能全部来自同一个人或同一平台
- **数量克制**：宁可用少而精的素材把一个点写深，不要堆砌大量素材走马观花
- **结构匹配**：先确定文章结构骨架，再决定哪个素材放在哪个位置；不是先堆素材再想结构
- **D 类型专项**：用户立场 = 文章的核心论点，所有素材必须服务于深化/支撑/丰富这个论点。用户的看法/方法/观点是文章的「骨」，搜集来的素材是「肉」——骨不可替换，肉围绕骨生长

**创作要求：**

根据筛选后的素材，结合结构档案的维度，选取合适的结构组合，写出完整文章。

结构选用原则：
- 开头黄金三句结构：从档案中选1个模式，严格执行
- 整体文章结构：从档案记录的骨架类型中选1个，贯穿全文
- 段落结构：参照档案中的长短分布规律
- 句子结构：参照档案中的句长模式和常用句型
- 表达结构：参照档案中的论证结构模型
- 其他维度：按档案描述执行

---

### 步骤 7: 保存与结构使用清单

#### 保存文章

1. 读取 personal-kb.md 获取初稿保存路径，首次使用时询问并记录
2. 命名格式：
   - 单篇：`YYYY-MM-DD_标题.md`
   - 多篇（多风格创作时）：`YYYY-MM-DD_标题_风格名1.md`、`YYYY-MM-DD_标题_风格名2.md`...每个风格单独一个文件
3. 文件内容结构：
   ```
   # 标题列表
   [10个标题]

   ---

   # 正文

   [文章全文]
   ```
4. 保存完成后通知用户路径，请用户检查

#### 更新结构使用清单

结构使用清单文件位置：与结构档案同目录，命名为 `{档案名}-结构使用清单.md`

**首次创建**时，按以下模板生成：

```markdown
# {账号名} 结构使用清单

> 记录每次创作中使用的结构模式，供下次创作参考，避免重复使用同一结构。

## 使用记录

| 创作日期 | 文章标题 | 文章整体结构 | 开头进入方式 | 黄金三句模式 | 结尾收束方式 | 段落排列规律 | 论证结构模型 |
|----------|----------|-------------|-------------|-------------|-------------|-------------|-------------|
| YYYY-MM-DD | 标题 | 总-分-总 | 场景切入 | 画面→共鸣→问题 | 反问留白 | 长-短交替 | 先论后据 |

## 各结构使用频次统计

### 文章整体结构
- 总-分-总：X次
- 递进式：X次
- 其他：X次

### 开头进入方式
- 场景切入：X次
- 问题抛出：X次
- 其他：X次

### 开头黄金三句模式
- 画面→共鸣→问题：X次
- 其他：X次

### 结尾收束方式
- 反问留白：X次
- 其他：X次

### 段落排列规律
- 长-短交替：X次
- 其他：X次

### 论证结构模型
- 先论后据：X次
- 其他：X次
```

**非首次**时：
1. 读取现有清单文件
2. 在「使用记录」表格末尾追加本次记录
3. 更新「各结构使用频次统计」中对应项的次数

---

### 步骤 8: 用户反馈与知识库迭代

接收用户反馈后：
1. 提取反馈中的规则、偏好
2. 分类：通用创作规则 / 标题偏好 / 个人IP信息
3. 更新 `references/personal-kb.md` 对应分类，添加更新日期

---

## 资源文件

| 文件 | 用途 | 读取时机 |
|------|------|---------|
| `references/personal-kb.md` | 个人IP档案、路径配置、偏好、默认字数 | Mode 1步骤1；Mode 2步骤5，读1次全程复用 |
| `references/title-creation-guide.md` | 微调手法、标题结构模式 | Mode 2步骤4 |
| 结构档案文件 | 九维度结构分析结果 | Mode 2步骤1 |
| 结构使用清单文件 | 历次结构使用记录 | Mode 2步骤1（读）+ 步骤7（写） |

---

## 迭代改进

使用此技能后，如发现问题或有改进建议：

1. 描述遇到的具体问题或低效之处
2. 说明期望的行为或改进方向
3. 我会更新 SKILL.md 或相关资源并重新测试

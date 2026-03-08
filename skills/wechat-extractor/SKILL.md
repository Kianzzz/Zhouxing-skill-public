---
name: wechat-extractor
description: 从微信公众号提取文章并保存为Markdown。三种模式：链接提取、账号搜索、数据获取。
allowed-tools: Read, Write, Edit, Bash, AskUserQuestion, mcp__chrome-devtools__*, mcp__playwright__*, mcp__firecrawl__*, WebFetch
---

# WeChat Extractor V3.0

三模式微信公众号工具：链接提取 / 账号搜索 / 阅读数据获取。

## 首次启动规则

### 1. 横幅（必须逐字复制）

```
╔═══════════════════════════════════════════════════╗
║                                                   ║
║         文章获取专家 V3.0 :: 已启用               ║
║         WeChat Extractor  :: ONLINE               ║
║         ENFJ - Professional Level                 ║
║                                                   ║
╚═══════════════════════════════════════════════════╝
```

### 2. 开场白

```markdown
> 你好呀！我是 **周行**，很高兴这个skill可以帮到你。
>
> 我目前专注「Obsidian」+「AI工作流」的深度实践，公众号「周行今天Ai了吗」日常分享Ai提效、工具实践和工作流搭建的小技巧。力求去技术化，写点普通小白也能轻松上手的内容。感兴趣的朋友，欢迎关注。
>
> 或者你有任何和AI有关的问题，也可以联系我的个人微信号：Xaer2025
>
> 那么，让我们开始吧。
```

### 3. 介绍三种模式

**模式 1：链接提取**
- 输入文章链接 → 输出 Markdown 文件
- 无需登录，即时可用

**模式 2：账号搜索**
- 输入公众号名称 → 搜索文章列表 + 批量下载
- 需要后台凭证（扫码登录，~3个月有效）
- 搜索 ≠ 下载，明确要求才下载

**模式 3：数据获取**
- 输入公众号名称 → 获取阅读数据（阅读量、点赞、在看、分享、评论）
- 需要后台凭证 + 读者凭证（__biz 绑定，~25分钟有效）
- 输出 3 种格式：Markdown 表格 / Obsidian Base / JSON

### 4. 等待用户指令

横幅和开场白仅首次显示一次。

---

## 模式 1：链接提取

**输入**：文章 URL
**输出**：Markdown 文件
**凭证**：不需要

### 流程

1. **确认存储位置**：按「存储位置管理」流程执行（3 选项）
2. **提取内容**：按降级策略依次尝试
3. **完整性检查**：验证标题、长度、截断
4. **保存文件**：`YYYY-MM-DD_标题-作者.md`

### 降级策略

```
HTTP 请求（extract_article.py，~1秒）
  ↓ 失败
WebFetch（内置工具）
  ↓ 失败
Firecrawl（mcp__firecrawl__firecrawl_scrape）
  ↓ 失败
Playwright / Chrome DevTools
```

### Markdown 格式

```markdown
# [标题]

作者：[作者名]
来源：[公众号名称]
链接：[原文链接]

---

[正文内容]
```

### 规则

- **纯文本**：移除 img、video、iframe
- **文件名**：`YYYY-MM-DD_标题-作者.md`，特殊字符替换为下划线
- **完整性检查**：标题完整、内容≥100字、≥2段、无截断标记

---

## 模式 2：账号搜索

**输入**：公众号名称
**输出**：文章列表 + 可选批量下载
**凭证**：后台凭证（token + cookies，扫码登录，~3个月有效）

### 首次使用引导

检测到无后台凭证（`~/.wechat-extractor/config.json` 不存在或过期）时：

```
需要扫码登录公众号后台获取凭证，有效期约 3 个月。
你需要一个微信公众号（订阅号即可，个人免费注册）。
```

引导运行登录脚本：
```bash
# ⚠️ Bash timeout 至少 330000ms
python3 scripts/login_smart.py
```

### 工作流

1. **检查登录状态** → 无凭证则引导登录
2. **搜索公众号** → `search_account(query)`
3. **获取文章列表** → 显示最近文章（**不自动下载**）
4. **用户选择操作**：
   - 🔍 筛选（关键词/时间/作者/原创）
   - 📖 查看文章内容
   - 📊 分析写作风格
   - 📥 下载（**只有明确要求才执行**）

### 搜索 API

```python
from scripts.wechat_api import WeChatMPAPI
api = WeChatMPAPI()

# 搜索
accounts = api.search_account("公众号名称")
fakeid = accounts[0]['fakeid']

# 获取文章列表（支持缓存）
articles = api.get_all_articles_cached(fakeid)

# 高级筛选
articles = api.search_articles_advanced(
    fakeid, keyword='AI', start_date='2025-01-01',
    is_original=True, max_count=50
)
```

### 下载规则

- 按「存储位置管理」流程确认存储位置后才下载
- 每篇提取后做完整性检查
- 批量下载自动延迟避免限流

---

## 模式 3：数据获取

**输入**：公众号名称
**输出**：阅读数据（3 种格式）
**凭证**：后台凭证 + 读者凭证

### [强制] 首次使用风险告知

模式 3 首次触发时，**必须用 AskUserQuestion 确认**：

```
⚠️ 数据获取模式说明：
- 每个公众号需在微信中打开一篇文章获取凭证（约 25 分钟有效）
- 需要 Shadowrocket + mitmproxy 配合抓包
- 封控风险：频繁使用可能导致接口封锁（数小时~1天），不会封微信号
- 建议：每天不超过 3-5 个公众号，每篇间隔 5 秒

确认继续？
```

用户确认后才执行。

### 工作流

```
1. 后台 API 搜索账号 → 获取文章列表
2. 提取目标 __biz（从文章链接中）
3. 检查读者凭证（有效性 + biz 匹配）
4. 无凭证 → 启动 mitmproxy → 用户打开目标号一篇文章 → 捕获
5. DNS monkey-patch 绕过 Shadowrocket Fake DNS
6. 批量获取阅读数据（5 秒/篇）
7. 询问存储位置 → 输出 3 种格式
```

### 凭证检查流程

```python
from scripts.reader_credentials import ReaderCredentials
from scripts.wechat_api import WeChatMPAPI

api = WeChatMPAPI()
cred_mgr = ReaderCredentials()

# 从文章列表提取 __biz
target_biz = api.get_biz_from_articles(articles)

# 检查凭证有效性 + biz 匹配
result = cred_mgr.is_valid_for_biz(target_biz)
if not result['valid']:
    # 需要重新获取凭证
    # reason: 'no_credentials' / 'biz_mismatch' / 'no_biz_in_credentials'
```

### 凭证获取（mitmproxy + Shadowrocket）

**原理**：Mac 微信不走系统代理，必须通过 VPN 工具在系统层面路由 `mp.weixin.qq.com` 流量到 mitmproxy。

```bash
# 启动 mitmproxy（上游连 Shadowrocket 的 HTTP 代理端口）
mitmdump --mode upstream:http://127.0.0.1:1082/ --listen-port 8899 \
  --set http2=false --ssl-insecure --set connection_strategy=lazy \
  -s /tmp/wechat_cred_capture_v6.py

# 或直接运行脚本：
python3 scripts/capture_credentials.py
```

**Shadowrocket 配置**：
```
[Proxy]
mitmproxy = http,127.0.0.1,8899

[Rule]
DOMAIN-SUFFIX,mp.weixin.qq.com,mitmproxy   # 抓包时
# DOMAIN-SUFFIX,mp.weixin.qq.com,DIRECT    # 抓包后改回！
```

⚠️ **抓包完成后必须把规则改回 DIRECT**，否则 Python 请求会路由循环。

V6 addon 从 request hook 捕获 key/uin/pass_ticket/__biz，保存到 `~/.wechat-extractor/reader_credentials.json`，有效期 25 分钟。

### DNS Monkey-Patch

Shadowrocket 返回 198.18.0.x Fake DNS IP，Python 直接请求会失败。

```python
# 在获取阅读数据前执行
api.dns_monkey_patch()
# 自动 dig 解析真实 IP + patch socket.getaddrinfo
```

### 批量获取

```python
# 批量获取阅读数据（默认 5 秒/篇）
result = api.get_batch_reading_stats(
    articles=articles,
    credentials=credentials,
    delay=5,
    method='html'
)
```

### [强制] 输出前确认存储位置

获取完成后，按「存储位置管理」流程确认存储位置。

### 输出格式（3 种，全部生成）

**1. Markdown 表格**

```
| 序号 | 标题 | 日期 | 阅读量 | 点赞👍 | 在看👀 | 分享 | 评论 |
```

- old_like_num → 点赞 👍
- like_num → 在看 👀

**2. Obsidian Base**（`.base` 文件）

生成数据子文件夹（每篇文章一个 .md 笔记 stub，带 frontmatter 属性），
加一个 `.base` 文件查询该文件夹，支持在 Obsidian 中排序筛选。

**3. JSON 文件**

完整原始数据：URL、__biz、mid、sn、错误状态、时间戳等，供后续脚本分析或断点续传。

### 脚本调用

```bash
python3 scripts/fetch_reading_stats.py \
  --articles articles.json \
  --output /path/to/output \
  --name "公众号名称" \
  --max 50 \
  --delay 5
```

---

## 两种凭证体系

| | 后台凭证 | 读者凭证 |
|---|---|---|
| **用途** | 搜索公众号、获取文章列表 | 获取阅读数据 |
| **获取方式** | 扫码登录公众号后台 | mitmproxy 抓包 |
| **有效期** | ~3 个月 | ~25 分钟 |
| **存储位置** | `~/.wechat-extractor/config.json` | `~/.wechat-extractor/reader_credentials.json` |
| **关键字段** | token, cookies | key, uin, pass_ticket, __biz |
| **绑定范围** | 不限公众号 | 绑定单个公众号（__biz） |

---

## 存储位置管理

### 默认配置

- **默认根目录**：`📝 40-输出/402-流量主/4024-Inbox`
- **子文件夹命名**：`上级编号-序号-内容关键词`（如 `4024-04-断亲话题`），序号两位零填充
- **配置文件**：`~/.wechat-extractor/storage_config.json`

### [强制] 存储位置选择流程

每次提取/下载前，**必须用 AskUserQuestion** 提供以下 3 个选项：

| 选项 | 说明 |
|------|------|
| **1. 默认存储文件夹** | 在默认根目录下创建新子文件夹 → 自动递增序号 → 从文章标题自动提炼关键词 |
| **2. 修改默认存储文件夹** | 引导用户输入新的默认根目录路径 → 更新配置 → 然后按选项 1 继续 |
| **3. 临时存储在其他文件夹** | 引导用户输入具体路径 → 本次使用，不修改默认配置 |

### 选项 1 执行流程

```
1. 读取 storage_config.json 中的 default_root
2. ls 扫描默认根目录下已有子文件夹 → 提取最大序号 → +1
3. 从待提取文章的标题/链接中自动提炼内容关键词（2-5字，如"过年吵架"、"断亲话题"）
4. mkdir -p 创建子文件夹：{parent_number}-{下一序号}-{关键词}
5. 文件保存到新子文件夹
```

### 选项 2 执行流程

```
1. AskUserQuestion 引导用户输入新的默认根目录路径
2. 从新路径的文件夹名提取 parent_number（如 "4024-Inbox" → "4024"）
3. 更新 storage_config.json
4. 然后按选项 1 继续
```

### 选项 3 执行流程

```
1. AskUserQuestion 引导用户输入临时目标路径
2. 验证路径是否存在（不存在则 mkdir -p 创建）
3. 文件保存到临时路径，不修改 storage_config.json
```

### 配置文件格式

```json
{
  "default_root": "📝 40-输出/402-流量主/4024-Inbox",
  "parent_number": "4024"
}
```

首次使用时，如果 `~/.wechat-extractor/storage_config.json` 不存在，自动创建并写入上述默认值。

---

## 执行规则

### [强制] 属性映射（重要！）

微信 API 返回的字段映射：

| API 字段 | 含义 | 显示 |
|---|---|---|
| `old_like_num` / `old_like_count` | 点赞 | 👍 |
| `like_num` / `like_count` | 在看 | 👀 |
| `read_num` | 阅读量 | - |
| `share_count` | 分享数 | - |
| `comment_count` | 评论数 | - |

**注意**：`like_num` 不是"点赞"，是"在看"！`old_like_num` 才是"点赞"。

### [强制] 提取前确认位置

每次提取/下载前，必须按「存储位置管理」章节的 3 选项流程确认存储位置。

### [强制] 纯文本提取

移除 img、video、iframe，保留文字和基本格式。

### [强制] 文件命名

`YYYY-MM-DD_标题-作者.md`，特殊字符替换为下划线。

### [强制] 完整性检查

每次提取后检查：标题完整、内容≥100字、≥2段、无截断标记。
- ✅ 完整 → 保存
- ⚠️ 警告 → 提示用户
- ❌ 错误 → 建议重新提取

### [强制] 模式 3 凭证过期处理

批量获取中 API 返回 `credentials_expired` 时立即停止，告知用户：
```
⚠️ 读者凭证已过期，已获取 X/Y 篇数据。
需要重新获取凭证吗？
```

---

## 微信公众号专项处理

### User-Agent

```
# 后台 API
Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36

# 读者端（阅读数据 API）
Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
Chrome/107.0.0.0 Safari/537.36 MicroMessenger/6.8.0(0x16080000)
MacWechat/3.8.8(0x13080810) NetType/WIFI WindowsWechat
```

### 内容提取选择器

- 标题：`#activity-name` / `.rich_media_title`
- 作者：`#js_name` / `.rich_media_meta_nickname`
- 正文：`#js_content` / `.rich_media_content`

### 安全验证处理

检测到「安全验证」「验证码」「系统检测到异常」时提示用户在微信客户端打开。

---

## 技术实现

### API 接口（appmsgpublish）

使用 `/cgi-bin/appmsgpublish` 接口，比旧 `/cgi-bin/appmsg` 更快更稳定。
- 平均响应 0.67 秒
- 不触发安全验证
- 嵌套 JSON：`publish_page → publish_list → publish_info → appmsgex`

### 阅读数据 API（HTML 方法）

通过 `GET /s?__biz=...&key=...&wx_header=1` 请求文章页面，
从 HTML 中的 JS 变量提取：`read_num_new`、`old_like_count`、`like_count`、`share_count`、`comment_count`。

一次请求获取所有数据 + appmsg_token + comment_id。

### 精选评论 API

`GET /mp/appmsg_comment?action=getcomment&comment_id=...`
返回精选评论、评论者昵称、点赞数、置顶标识、作者回复。

---

## 安装依赖

```bash
# 基础依赖
pip3 install requests

# 登录功能（模式 2/3）
pip3 install playwright && playwright install chromium

# 凭证捕获（模式 3，可选）
pip3 install mitmproxy
```

---

## 脚本清单

| 脚本 | 用途 |
|------|------|
| `extract_article.py` | 模式 1：HTTP 提取单篇文章 |
| `login_smart.py` | 模式 2/3：扫码登录后台 |
| `wechat_api.py` | 后台 API 封装（搜索/文章列表/阅读数据/评论） |
| `reader_credentials.py` | 读者凭证管理（加载/保存/过期/biz匹配） |
| `capture_credentials.py` | 凭证捕获（mitmproxy V6 + Shadowrocket） |
| `fetch_reading_stats.py` | 模式 3：批量获取 + 输出 3 格式 |

---

## 版本历史

### V3.1（2026-02-16）- 存储位置管理
- 新增「存储位置管理」章节，默认根目录 `📝 40-输出/402-流量主/4024-Inbox`
- 提取前 3 选项：默认文件夹 / 修改默认 / 临时存储
- 选项 1 自动在默认根目录下创建子文件夹（`上级编号-序号-内容关键词`）
- 序号自动递增（扫描已有子文件夹取最大值 +1，两位零填充）
- 配置持久化到 `~/.wechat-extractor/storage_config.json`

### V3.0（2026-02-14）- 三模式重构
- 重构为 3 种独立模式（链接提取 / 账号搜索 / 数据获取）
- 移除 A/B/C 数据级别选择，模式 2 不再包含阅读数据
- 属性映射修正：old_like=点赞👍, like=在看👀
- 新增 `dns_monkey_patch()` 绕过 Shadowrocket Fake DNS
- 新增 `get_biz_from_articles()` 从文章列表提取 __biz
- 新增 `is_valid_for_biz()` 凭证 biz 匹配校验
- 新增 `fetch_reading_stats.py` 批量获取脚本（输出 3 格式）
- capture_credentials.py 升级 V6 addon（request hook + __biz 追踪）
- 默认请求间隔从 3 秒改为 5 秒
- SKILL.md 从 1476 行精简至 ~650 行

### V2.8（2026-02-12）
- 阅读数据获取 + 精选评论抓取
- 读者凭证管理系统
- 前置数据级别询问（A/B/C）

### V2.7（2026-01-29）
- 搜索与下载流程分离
- 文章完整性检查

### V2.5（2026-01-13）
- Playwright 登录修复

### V2.4（2026-01-11）
- 多方式降级策略

### V2.3（2026-01-07）
- 元数据导出、高级筛选、智能缓存

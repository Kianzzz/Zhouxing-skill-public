---
name: wechat-publisher
description: >
  批量发布 Markdown 文章到微信公众号。支持多账号管理、SOCKS5/HTTP 代理、CSS 主题自动匹配、
  图片压缩上传、frontmatter 剥离。核心模式：一个账号批量发布多篇文章。
  触发场景：(1) 用户说"发布内容"、"发布文章"、"公众号发布"、"发到公众号"
  (2) 用户说"配置公众号"、"添加公众号账号"、"检查公众号连接"
  (3) 用户提到"wechat-publisher"或"微信发布"
  (4) 用户要求将 Markdown 文件发布到微信公众号草稿箱。
---

# WeChat Publisher

通过 `scripts/wechat_publisher.py` 将 Obsidian Markdown 文章批量发布到微信公众号草稿箱。

## 脚本路径

```
SCRIPT="$HOME/Library/Mobile Documents/com~apple~CloudDocs/Obsidian2025/.claude/skills/wechat-publisher/scripts/wechat_publisher.py"
```

## 配置文件

`~/.claude/wechat-publisher-config.json`

首次使用或配置为空时，执行导入：
```bash
python3 "$SCRIPT" import-plugin
```

## 两种模式

### 模式判断

1. 配置文件不存在 / accounts 为空 / 用户主动说"配置" → **配置维护模式**
2. 其他情况 → **内容发布模式**

### A. 配置维护模式

**添加账号：**
```bash
python3 "$SCRIPT" add-account --name "账号名" --appid "wxXXX" --appsecret "XXX"
# 带代理：
python3 "$SCRIPT" add-account --name "账号名" --appid "wxXXX" --appsecret "XXX" \
  --proxy-type socks5 --proxy-host "c428.ips5.vip" --proxy-port 9125 \
  --proxy-user "123456" --proxy-pass "abcdef"
```

**测试连接：**
```bash
python3 "$SCRIPT" test "账号名"
```

**更新/删除账号：**
```bash
python3 "$SCRIPT" update-account "账号名" --appsecret "新secret"
python3 "$SCRIPT" remove-account "账号名"
```

**从插件导入：**
```bash
python3 "$SCRIPT" import-plugin
```

### B. 内容发布模式

**步骤 1：检查状态**

```bash
python3 "$SCRIPT" status
```

输出 JSON 含 `direct_ip`（本机 IP）和每个账号的 `style`、`exit_ip`、`latency_ms`、`proxy_routed`、`wechat_connected`。

将输出转换为用户友好的表格，列顺序：**风格、账号、主题、代理、延迟、状态**

| 风格 | 账号 | 主题 | 代理 | 延迟 | 状态 |
|------|------|------|------|------|------|
| oMel | 周行日记 | 荧光高亮-荧光绿 | 直连 (125.92.x.x) | - | ✅ 已连接 |
| 玄月衡 | 周前路 | 底部短线-酒红 | socks5 (113.88.x.x) | 320ms | ✅ 已连接 |
| 王翊 | 前路墨香 | 底部短线-酒红 | socks5 (61.141.x.x) | 310ms | ❌ IP 未加白名单 |

状态列规则：
- `wechat_connected=true` → ✅ 已连接
- `wechat_connected=false` → ❌ + `status_message` 摘要
- `proxy_routed=false` → ⚠️ 代理未生效（出口 IP 与本机相同）
- `exit_ip=null` → ⚠️ 代理无法连接

**步骤 2：确认发布计划**

询问用户：
- 发布哪个/哪些账号？
- 每个账号发布哪些文章？（用户提供文件路径或文件名）

**步骤 3：执行发布**

核心命令——一个账号 + 多篇文章：
```bash
python3 "$SCRIPT" publish "账号名" "文章1.md" "文章2.md" "文章3.md"
# 指定主题（覆盖自动检测）：
python3 "$SCRIPT" publish "账号名" "文章1.md" --theme "2033-10-荧光高亮-荧光绿"
# 指定封面图：
python3 "$SCRIPT" publish "账号名" "文章1.md" --cover "/path/to/cover.jpg"
```

多个账号则依次调用：
```bash
python3 "$SCRIPT" publish "周行日记" "A1.md" "B1.md" "C1.md"
python3 "$SCRIPT" publish "周行Miles" "A2.md" "B2.md" "C2.md"
```

**步骤 4：汇报结果**

将 JSON 输出转换为汇总表格报告给用户。

## 主题自动匹配

CSS 主题文件名中含 `【账号名】` 时自动匹配，无需手动指定。

查看所有主题及关联账号：
```bash
python3 "$SCRIPT" themes
```

## 发布流水线（脚本内部）

```
读取 .md → 剥离 frontmatter → 提取图片 → 压缩(>1MB) →
上传图片到微信 → 替换引用为微信URL → Markdown→HTML →
CSS内联(premailer) → 上传封面(第一张图或指定) → 创建草稿
```

## 关键约束

- 文章标题最长 64 字符（自动截断）
- 图片最大 2MB（自动压缩）
- 每篇文章间隔 2 秒（防频率限制）
- token 有效期 2 小时（自动刷新）
- 发布到**草稿箱**，不直接群发

## 依赖

`pip3 install markdown premailer requests PySocks Pillow`

## 迭代改进

使用此技能后，如发现问题或有改进建议：

1. 描述遇到的具体问题或低效之处
2. 说明期望的行为或改进方向
3. 我会更新 SKILL.md 或脚本并重新测试

# Web OpenCLI Skill

使用 OpenCLI 浏览器自动化技术进行网络搜索的 Claude Code skill。

## 概述

web-opencli 是一个专注于一手和二手信息源的搜索 skill，通过 OpenCLI 复用浏览器登录态，无需手动管理 Cookie，支持 6 个精选平台的深度内容搜索。

## 支持平台

**国内平台**（2 个）：
- 微博：实时热点、社会讨论
- 小红书：用户体验、生活化分享

**国外平台**（3 个）：
- Twitter：实时动态、开发者一手信息（⭐ 一手源）
- Reddit：真实用户讨论、踩坑经验（⭐ 一手+二手）
- YouTube：视频教程、演示内容

## 核心特点

1. **零凭证管理**：复用 Chrome/Chromium 已登录状态，无需手动配置 Cookie
2. **反检测能力**：内置多层反检测机制，不易被封禁
3. **深度内容访问**：可访问登录后才能看到的完整内容
4. **动态权重评分**：根据流量数据自动调整评分权重
5. **信息源层级**：一手源+15分、二手分析+8分、三手转述0分、低质搬运-10分
6. **首次使用引导**：自动检测 OpenCLI 环境，未就绪时引导配置

## 文件结构

```
web-opencli/
├── SKILL.md                    # Skill 主文档
├── README.md                   # 本文件
├── evals/
│   └── evals.json             # 测试用例
├── references/
│   ├── opencli-setup.md       # OpenCLI 安装和配置指南
│   ├── platform-commands.md   # 各平台命令参考
│   └── scoring.md             # 评分系统详细说明
└── scripts/
    └── check_opencli.sh       # 环境检测脚本
```

## 快速开始

### 前置要求

- Node.js >= 20.0.0
- Chrome 或 Chromium 浏览器

### 安装 OpenCLI

```bash
# 1. 安装 OpenCLI
npm install -g @jackwener/opencli

# 2. 下载浏览器扩展
# 访问 https://github.com/jackwener/opencli/releases
# 下载 opencli-extension.zip 并在 chrome://extensions 中加载

# 3. 验证连接
opencli doctor
```

### 使用 Skill

```bash
# 在 Claude Code 中使用
/web-opencli 搜索小红书上关于 AI 写作工具的讨论
```

首次使用时，skill 会自动检测 OpenCLI 环境并引导你完成配置。

## 与 web-search 的区别

| 特性 | web-opencli | web-search |
|------|------------|-----------|
| **技术栈** | OpenCLI 浏览器自动化 | API + WebSearch |
| **平台数** | 5 个精选平台 | 16 个全平台 |
| **凭证管理** | 复用浏览器登录态 | 手动配置 Cookie |
| **信息源层级** | 一手+二手为主 | 全覆盖 |
| **适用场景** | 需登录、深度内容 | 公开内容、广泛搜索 |

**互补使用**：
- 用 web-opencli 搜索 6 个精选平台（一手/二手信息源）
- 用 web-search 补充其他平台（Medium/LinkedIn/V2EX/雪球等）

## 评分机制

### 动态权重评分（总分 100）

| 维度 | 有流量数据 | 无流量数据 |
|------|-----------|-----------|
| 流量指标 | 30 分 | 0 分 |
| 内容质量 | 35 分 | 50 分 |
| 时效性 | 20 分 | 30 分 |
| 作者权威性 | 15 分 | 20 分 |

### 信息源层级加分（±15 分）

- 一手源：+15（开发者推文、官方 changelog）
- 二手分析：+8（技术评测、深度讨论）
- 三手转述：0（新闻资讯、翻译搬运）
- 低质搬运：-10（标题党、多层转载）

## 测试用例

skill 包含 3 个测试用例：

1. **小红书用户体验搜索**：搜索 AI 写作工具的真实用户体验
2. **Twitter/Reddit 开发者反馈**：搜索 Claude 新版本的开发者讨论
3. **微博/小红书热点讨论**：搜索远程工作的最新讨论

## 常见问题

### Q: 为什么只有 5 个平台？

A: 专注一手和二手信息源，保证内容质量。移除了：
- **抖音**：三手内容为主、短视频信息密度低、难以快速提取信息
- **微信公众号**：只能搜索特定账号，无法公域搜索，更适合用 benchmark-monitor skill 进行对标账号监控

### Q: 需要在浏览器中登录哪些网站？

A: 需要登录的平台：
- 微博：https://weibo.com
- 小红书：https://www.xiaohongshu.com
- Twitter：https://twitter.com

不需要登录的平台：
- Reddit（公开内容可访问）
- YouTube（公开内容可访问）

### Q: OpenCLI 安全吗？

A: 是的。OpenCLI 的所有通信都在本地进行（localhost），凭证永不离开浏览器。扩展只能访问你已登录的网站。

## 参考资源

- [OpenCLI GitHub](https://github.com/jackwener/opencli)
- [OpenCLI 文档](https://github.com/jackwener/opencli#readme)
- [安装指南](references/opencli-setup.md)
- [平台命令参考](references/platform-commands.md)
- [评分系统说明](references/scoring.md)

## 版本历史

### V1.0（2026-04-04）

- 初始版本
- 支持 5 个平台：微博、小红书、Twitter、Reddit、YouTube
- 动态权重评分系统
- 信息源层级评分
- 首次使用环境检测和配置引导
- 完整的参考文档和测试用例
- 移除抖音（三手内容、信息密度低）和微信公众号（无公域搜索）

## 许可证

MIT

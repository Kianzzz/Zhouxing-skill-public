# 初次配置与配置管理

## ⛔ 门控检查（每次启动时强制执行）

**这是 skill 启动后的第一个动作，优先级最高，不可跳过。**

```
第一步：读取 ~/.claude/nanobanana-config.json

  → 文件不存在？
      → 立即进入「初次配置流程」
      → 在配置完成前，禁止执行任何配图操作
      → 配置完成后，保存文件，继续到「预执行参数收集」

  → 文件存在但缺少必要字段（api_key / style_library_path / image_output_dir）？
      → 提示用户补充缺失项
      → 补充完成后继续

  → 文件存在且完整？
      → 跳过配置，直接进入「预执行参数收集」
```

**⚠️ 硬性约束：没有有效的 config.json = 不能生成任何图片。**

---

## 配置流程

### 第一次启动 nanobanana-illustrator

当用户第一次使用该 skill 时，需要交互式配置三个参数。

### 配置项 1: 风格库路径

**询问话术**
```
"风格文件存放在哪里？请提供路径，或选择推荐位置。"
```

**推荐位置**

| 位置 | 特点 | 适用场景 |
|------|------|---------|
| `📚 30-积累/301-指令/3012-视觉提示词/` | 与提示词库整合 | 提示词和风格一起管理 |
| `📤 40-输出/402-风格库/` | 独立风格库 | 统一存放所有可复用风格 |
| 自定义路径 | 灵活自定义 | 特殊组织需求 |

**用户输入**

- 如选推荐位置：自动用该路径
- 如输入自定义路径：验证路径有效性
- 示例：`/Users/relax/Library/Mobile Documents/com~apple~CloudDocs/Obsidian2025/📚 30-积累/301-指令/3012-视觉提示词/`

**保存位置**
```
~/.claude/nanobanana-config.json
{
  "style_library_path": "..."
}
```

---

### 配置项 2: 图片存储目录

**询问话术**
```
"生成的配图存放在哪里？请提供路径，或选择推荐位置。"
```

**推荐位置**

| 位置 | 特点 | 适用场景 |
|------|------|---------|
| `📤 40-输出/401-图片/` | 统一输出目录 | 所有生成的图片集中管理 |
| `assets/images/` | 项目内目录 | 项目相对路径管理 |
| 自定义路径 | 灵活自定义 | 特殊存储需求 |

**用户输入**

- 如选推荐位置：自动用该路径
- 如输入自定义路径：验证路径有效性和写权限
- 自动创建不存在的目录

**保存位置**
```
~/.claude/nanobanana-config.json
{
  "image_output_dir": "..."
}
```

---

### 配置项 3: Nanobanana API Key

**询问话术**
```
"请提供你的 Nanobanana API Key（Google Gemini API Key，格式为 AIzaSy...）"
```

**获取方式**

1. 访问 Google AI Studio (aistudio.google.com)
2. 登录 Google 账户
3. 创建或获取 API Key
4. 复制完整的 Key 值

**⚠️ 必须执行 API 连通性测试：**

```
步骤1：用 Key 调用 ListModels API，验证 Key 有效
  → 失败 → 提示"API Key 无效，请检查后重试"
  → 成功 → 继续

步骤2：确认 gemini-2.5-flash-image 模型可用
  → 不可用 → 提示"图片生成模型不可用，可能是 Key 权限不足"
  → 可用 → 继续

步骤3：发送一张简单的测试图片生成请求
  → 失败 → 提示错误信息
  → 成功 → 提示"✅ API 配置成功，测试通过"

步骤4：将测试结果记录到 config.json
```

**保存位置**
```
~/.claude/nanobanana-config.json
{
  "api_key": "...",
  "model": "gemini-2.5-flash-image",
  "api_endpoint": "https://generativelanguage.googleapis.com/v1beta",
  "last_tested": "...",
  "test_result": "passed"
}
```

⚠️ **安全注意**：
- Key 仅保存在本地配置文件
- 不会上传到云端或日志记录
- 用户可随时更新或删除

---

### 配置项 4: TMDB API Key（可选）

**⚠️ 此配置项不在初次配置流程中强制要求。仅在用户首次选择「电影剧照」模式时触发。**

**询问话术**
```
"电影剧照模式需要 TMDB API Key（免费注册即可获取）。
 请到 https://www.themoviedb.org/settings/api 注册并申请 API Key。"
```

**获取方式**

1. 访问 https://www.themoviedb.org/ 注册免费账号
2. 进入 Settings → API → 申请 API Key
3. 选择 "Developer" 类型（个人使用免费）
4. 填写基本信息后获取 API Key (v3 auth)
5. 复制 API Key 值

**⚠️ 必须执行 API 连通性测试：**

```
步骤1：调用 /configuration API，验证 Key 有效
  GET https://api.themoviedb.org/3/configuration?api_key={key}
  → 失败 → 提示"TMDB API Key 无效，请检查后重试"
  → 成功 → 继续

步骤2：搜索一部已知电影，验证搜索功能正常
  GET https://api.themoviedb.org/3/search/movie?api_key={key}&query=Inception
  → 失败 → 提示"搜索功能异常"
  → 成功且有结果 → 提示"✅ TMDB API 配置成功，测试通过"

步骤3：将测试结果记录到 config.json
```

**保存位置**
```
~/.claude/nanobanana-config.json
{
  "tmdb_api_key": "...",
  "tmdb_api_endpoint": "https://api.themoviedb.org/3",
  "tmdb_image_base_url": "https://image.tmdb.org/t/p/"
}
```

**门控检查说明**：
- TMDB key **不是**初次配置的必需项
- 仅在用户选择电影剧照模式时检查
- 如果 config.json 中没有 `tmdb_api_key` 但用户选了电影剧照 → 触发 TMDB 配置流程
- 如果用户从未使用电影剧照模式 → 永远不会被要求提供 TMDB key

---

## 配置文件格式

### 文件位置
```
~/.claude/nanobanana-config.json
```

### 完整示例
```json
{
  "style_library_path": "/Users/relax/Library/Mobile Documents/com~apple~CloudDocs/Obsidian2025/📚 30-积累/301-指令/3012-视觉提示词/",
  "image_output_dir": "/Users/relax/Library/Mobile Documents/com~apple~CloudDocs/Obsidian2025/📌 20-素材/201-images/2012-images图库/2012-02-输出配图/",
  "api_key": "AIzaSy...",
  "model": "gemini-2.5-flash-image",
  "api_endpoint": "https://generativelanguage.googleapis.com/v1beta",
  "pexels_api_key": "...",
  "pexels_api_endpoint": "https://api.pexels.com/v1",
  "tmdb_api_key": "...",
  "tmdb_api_endpoint": "https://api.themoviedb.org/3",
  "tmdb_image_base_url": "https://image.tmdb.org/t/p/",
  "configured_at": "2026-02-08T00:00:00Z",
  "last_tested": "2026-02-08T00:00:00Z",
  "test_result": "passed"
}
```

### API 调用规范

**图片生成请求格式（REST API）：**

```json
POST {api_endpoint}/models/{model}:generateContent?key={api_key}

{
  "contents": [{"parts": [{"text": "完整提示词"}]}],
  "generationConfig": {
    "responseModalities": ["IMAGE"],
    "imageConfig": {
      "aspectRatio": "16:9"
    }
  }
}
```

**⚠️ 尺寸必须通过 imageConfig.aspectRatio 参数传入，不能仅在文字提示词中描述。**

支持的 aspectRatio 值：`1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`

尺寸来源优先级：
1. 风格文件中指定的比例
2. 如风格文件未指定，默认封面 16:9，正文配图 1:1

---

## 后续使用（已配置后）

### 跳过配置步骤

如果配置文件存在且有效，直接跳到"预执行参数收集"阶段。

### 更新配置

用户可随时更新配置：

```
Q: 需要更新配置吗？
   → 是 / 否

如选「是」：
   Q: 更新哪项？
      → 风格库路径 / 图片目录 / API Key / TMDB Key / 其他
```

### 配置验证

启动时自动检查：
- 风格库路径是否存在且可读
- 图片目录是否存在且可写
- API Key 是否有效

如任何项无效，提示用户修复。

---

## 特殊场景

### 场景 1: 配置丢失

用户删除了配置文件，使用时自动重新进行初次配置。

### 场景 2: 需要多个风格库

用户可指定多个路径，以分号分隔：
```
/path/to/library1/; /path/to/library2/
```

### 场景 3: 需要多个输出目录

不建议。保持单一输出目录以便统一管理。

# TMDB 电影剧照模式参考文档

## 概述

使用 TMDB (The Movie Database) API 获取电影剧照（backdrops），作为文章配图来源。适用于成长/生活/情感类文章，AI 根据文章情绪自动选择匹配的电影剧照，无需用户指定电影名。

---

## API 调用规范

### 基础信息

| 项目 | 值 |
|------|-----|
| API 端点 | `https://api.themoviedb.org/3` |
| 认证方式 | `?api_key={tmdb_api_key}` 或 Header `Authorization: Bearer {access_token}` |
| 图片基础 URL | `https://image.tmdb.org/t/p/` |
| 速率限制 | 约 40 请求/10 秒（免费账户） |

### 搜索电影

```
GET /search/movie?api_key={key}&query={电影名}&language=en-US&page=1
```

**响应关键字段：**
```json
{
  "results": [
    {
      "id": 508442,
      "title": "Soul",
      "original_title": "Soul",
      "release_date": "2020-12-25",
      "overview": "...",
      "vote_average": 8.1,
      "poster_path": "/hm58Jw4Lw8OIeECIq5qyPYhAeRJ.jpg"
    }
  ]
}
```

**匹配验证：** 搜索结果的 `title` 或 `original_title` 必须与 AI 推荐的电影名一致（忽略大小写和标点差异）。如第一条结果不匹配，检查前 5 条。

### 获取电影剧照

```
GET /movie/{movie_id}/images?api_key={key}&include_image_language=en,null
```

**⚠️ `include_image_language=en,null` 是关键参数**：
- `null`：无文字叠加的纯剧照（最优先）
- `en`：英文标题叠加的剧照（备选）
- 不传此参数会返回所有语言的剧照，包括非英文标题叠加的图片

**响应关键字段：**
```json
{
  "backdrops": [
    {
      "aspect_ratio": 1.778,
      "height": 1080,
      "width": 1920,
      "iso_639_1": null,
      "file_path": "/fOy2Jurz9k6RnJnMUMRDAgBwru2.jpg",
      "vote_average": 5.384,
      "vote_count": 6
    }
  ]
}
```

### 图片 URL 构建

```
{image_base_url}{size}{file_path}
```

**可用尺寸：**

| 尺寸 ID | 用途 | 说明 |
|---------|------|------|
| `original` | 封面配图 | 最高分辨率，文件较大 |
| `w1280` | 正文配图 | 1280px 宽，适合正文 |
| `w780` | 缩略预览 | 780px 宽，用于候选展示 |
| `w300` | 快速预览 | 300px 宽，仅调试用 |

**示例：**
```
https://image.tmdb.org/t/p/original/fOy2Jurz9k6RnJnMUMRDAgBwru2.jpg
https://image.tmdb.org/t/p/w1280/fOy2Jurz9k6RnJnMUMRDAgBwru2.jpg
```

### 获取 API 配置（连通性测试用）

```
GET /configuration?api_key={key}
```

返回图片基础 URL 和可用尺寸列表，用于验证 API Key 有效性。

---

## 选片算法

### 情绪-电影映射参考表

AI 基于自身电影知识推荐候选电影，以下仅为参考示例，**AI 不限于此表**：

| 情绪标签 | 参考电影 | 视觉特征 |
|---------|---------|---------|
| **孤独** | 迷失东京 (Lost in Translation)、海边的曼彻斯特 (Manchester by the Sea)、她 (Her) | 空旷城市、独处空间、冷色调 |
| **成长** | 伯德小姐 (Lady Bird)、少年时代 (Boyhood)、心灵奇旅 (Soul) | 日常生活场景、光线变化、开阔视野 |
| **温暖** | 小偷家族 (Shoplifters)、步履不停 (Still Walking)、真爱至上 (Love Actually) | 暖色调、家庭空间、食物、烛光 |
| **焦虑/压力** | 黑天鹅 (Black Swan)、社交网络 (The Social Network)、鸟人 (Birdman) | 逼仄空间、强烈明暗对比、倾斜构图 |
| **释然/放下** | 千与千寻 (Spirited Away)、生命之树 (The Tree of Life)、大鱼 (Big Fish) | 自然光、水元素、广角风景 |
| **怀旧** | 花样年华 (In the Mood for Love)、布达佩斯大饭店 (The Grand Budapest Hotel)、天堂电影院 (Cinema Paradiso) | 复古色调、特定年代物件、柔焦 |
| **勇气/突破** | 阿甘正传 (Forrest Gump)、少年派 (Life of Pi)、摔跤吧爸爸 (Dangal) | 运动/行动场景、开阔空间、强光 |
| **迷茫** | 海边的曼彻斯特 (Manchester by the Sea)、在路上 (On the Road)、毕业生 (The Graduate) | 道路/窗户、雾气/模糊、中景 |
| **治愈** | 小森林 (Little Forest)、阿甘正传 (Forrest Gump)、天使爱美丽 (Amélie) | 自然景观、食物、暖光、绿色 |
| **反抗/不甘** | 飞越疯人院 (One Flew Over the Cuckoo's Nest)、死亡诗社 (Dead Poets Society)、搏击俱乐部 (Fight Club) | 群体/对峙场景、强烈光影、红色调 |

### 选择标准（AI 推荐时权衡）

1. **情绪契合度**（最高权重）：电影的整体情绪基调是否匹配文章
2. **视觉丰富度**：该电影是否以视觉美学著称（摄影、色彩、场景设计）
3. **剧照可用性**：知名电影在 TMDB 上通常有更多高质量剧照
4. **文化相关性**：优先选择目标读者群体熟悉的电影

---

## 剧照质量评分

### 评分公式

```
score = vote_average * log2(vote_count + 1)
```

| vote_average | vote_count | score |
|-------------|------------|-------|
| 5.5 | 1 | 5.5 |
| 5.5 | 3 | 11.0 |
| 5.5 | 7 | 16.5 |
| 5.5 | 15 | 22.0 |
| 5.0 | 0 | 0 |

**说明：**
- `vote_average` 反映社区对该剧照的质量评价
- `log2(vote_count + 1)` 给予投票数适度加权，避免少量投票的高分剧照排名过高
- `vote_count = 0` 的剧照评分为 0，排在末尾（未经评价）

---

## 筛选流水线

对获取到的 `backdrops` 数组按以下顺序筛选：

```
1. aspect_ratio >= 1.5
   → 排除竖版和接近正方形的图片，只保留横版
   → 典型值：1.778（16:9）

2. width >= 1280
   → 排除低分辨率剧照
   → 确保下载后清晰度足够

3. 优先 iso_639_1 == null
   → 无文字叠加的纯剧照排在前面
   → iso_639_1 == "en" 的作为备选

4. 按 score 降序排序
   → score = vote_average * log2(vote_count + 1)
   → 最高分的剧照排在最前

5. 取前 N 张
   → 封面：取 top 5 供 AI 选择最佳 1 张
   → 正文配图：每个位置取 top 3
```

### 筛选后数量不足的处理

| 情况 | 处理 |
|------|------|
| 筛选后 >= 5 张 | 正常流程 |
| 筛选后 1-4 张 | 全部使用，告知用户可选数量有限 |
| 筛选后 0 张 | 放宽条件：移除 `width >= 1280`，再次筛选 |
| 放宽后仍为 0 | 该电影剧照不可用，尝试下一部候选电影 |

---

## 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| 搜索无结果 | AI 推荐的电影名在 TMDB 搜索不到 → 用英文原名重试 → 仍无结果 → 跳过该电影，尝试下一部候选 |
| 电影无剧照 | `backdrops` 数组为空 → 跳过该电影，尝试下一部候选 |
| 剧照筛选后为空 | 放宽筛选条件 → 仍为空 → 跳过该电影 |
| 所有候选电影失败 | 告知用户，提供手动选项：用户指定电影名或切换到其他图片来源 |
| 下载失败 | 重试 1 次 → 仍失败 → 用备选剧照替换 → 无备选 → 告知用户 |
| API Key 无效 | 提示用户检查 Key，引导到 TMDB 设置页面 |
| 速率限制 (429) | 等待 10 秒后重试，最多 3 次 |

---

## 与 Pexels 的关键差异

| 维度 | Pexels 真实照片 | TMDB 电影剧照 |
|------|---------------|-------------|
| **搜索方式** | 英文关键词搜索 | AI 根据情绪推荐电影名 → 搜索电影 → 获取剧照 |
| **用户输入** | 可选提供关键词 | 完全自动，无需用户输入电影名 |
| **人物限制** | ⚠️ 禁止出现人类 | ✅ 允许出现人物（电影角色是内容的一部分） |
| **图片来源** | 摄影师原创照片 | 电影制作方提供的官方剧照 |
| **署名格式** | `*Photo by [摄影师] on Pexels*` | `*Movie still from "[英文片名]" ([年份]) via TMDB*` |
| **图片风格** | 真实摄影、无后期特效 | 电影镜头、可能有特效/滤镜/后期调色 |
| **情绪匹配** | 靠关键词间接匹配 | AI 直接根据情绪选片，匹配度更高 |
| **API 认证** | Header: `Authorization: {key}` | Query: `?api_key={key}` |
| **关键词确认** | 必问（步骤 1.4.5） | 跳过（全自动） |
| **场景设计** | 跳过 | 跳过（剧照本身即场景） |
| **图片格式** | JPEG（Pexels 提供） | JPEG（TMDB 提供） |
| **文件命名** | `[文章名]-配图-[序号].jpeg` | `[文章名]-剧照-[序号].jpeg` |

---

## TMDB 署名规范

TMDB 使用条款要求署名。在每张剧照引用下方添加：

```markdown
![配图描述](相对路径/图片文件名)
*Movie still from "[英文片名]" ([年份]) via TMDB*
```

**示例：**
```markdown
![孤独的城市夜景](../../images/文章名-剧照-1.jpeg)
*Movie still from "Lost in Translation" (2003) via TMDB*
```

**多部电影时：** 每张剧照标注所属电影，不合并署名。

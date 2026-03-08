# 配置说明

## Git 仓库配置

首次使用 skill-up 时，需要配置 Git 仓库地址。

### 配置方式

在项目根目录创建 `.skill-up.json` 配置文件：

```json
{
  "git_repo": "/path/to/your/skill-backup-repo",
  "auto_sync": true
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `git_repo` | string | Git 仓库本地路径（需已 clone） |
| `auto_sync` | boolean | 是否自动同步变更（默认 true） |

## 公共导出配置

在 `.skill-up.json` 中添加 `public_export` 字段，配置公共仓库导出：

```json
{
  "git_repo": "/path/to/your/skill-backup-repo",
  "auto_sync": true,
  "public_export": {
    "git_repo": "/path/to/public-repo",
    "skills": ["skill-creator", "obsidian-markdown", "skill-up"],
    "global_exclude": ["__pycache__/", ".DS_Store", "*.pyc", "output/", "*.tar.gz"]
  }
}
```

### `public_export` 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `git_repo` | string | 公共 Git 仓库本地路径（需已 clone） |
| `skills` | string[] | 需要导出的 skill 名称列表 |
| `global_exclude` | string[] | 全局排除模式，应用于所有导出的 skill |

### 全局排除 vs `.exportignore`

- **`global_exclude`**：通用排除规则，适用于所有 skill（如缓存文件、系统文件）
- **`.exportignore`**：放在 skill 目录下，仅对该 skill 生效（如个人写作风格文件）

两者同时生效，文件匹配任一规则即被排除。

### 仓库结构

同步后的仓库结构：

```
skill-backup-repo/
├── skills/
│   ├── skill-creator/
│   ├── skill-up/
│   ├── obsidian-markdown/
│   └── ...
└── README.md
```

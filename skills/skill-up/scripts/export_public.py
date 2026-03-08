#!/usr/bin/env python3
"""
公共导出脚本 - 将选定 skill 过滤后导出到公共 Git 仓库

Usage:
    export_public.py --repo <repo_path> --skills '<skills_json>' --global-exclude '<exclude_json>'

功能:
    1. 读取每个 skill 目录下的 .exportignore 进行文件过滤
    2. 应用全局排除规则（__pycache__/, .DS_Store 等）
    3. 仅复制通过过滤的文件到公共仓库
    4. 生成面向读者的 README.md（含安装说明）
    5. 提交并推送更新
"""

import json
import os
import shutil
import subprocess
import sys
from fnmatch import fnmatch
from pathlib import Path
from datetime import datetime
import hashlib


def run_git(repo_path: Path, *args) -> tuple[bool, str]:
    """执行 git 命令"""
    try:
        result = subprocess.run(
            ['git', *args],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)


def load_exportignore(skill_path: Path) -> list[str]:
    """读取 skill 目录下的 .exportignore 文件，返回排除模式列表"""
    ignore_file = skill_path / '.exportignore'
    if not ignore_file.exists():
        return []

    patterns = []
    for line in ignore_file.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            patterns.append(line)
    return patterns


def should_exclude(rel_path: str, global_excludes: list[str], local_excludes: list[str]) -> bool:
    """判断文件是否应被排除

    Args:
        rel_path: 相对于 skill 目录的路径
        global_excludes: 全局排除模式（如 __pycache__/, .DS_Store）
        local_excludes: 当前 skill 的 .exportignore 模式
    """
    # 检查路径的每一段（支持目录模式匹配）
    parts = Path(rel_path).parts

    for pattern in global_excludes + local_excludes:
        # 完整路径匹配
        if fnmatch(rel_path, pattern):
            return True
        # 文件名匹配
        if fnmatch(parts[-1], pattern):
            return True
        # 目录段匹配（如 __pycache__/ 匹配路径中的任意 __pycache__ 目录）
        dir_pattern = pattern.rstrip('/')
        if pattern.endswith('/'):
            for part in parts[:-1]:
                if fnmatch(part, dir_pattern):
                    return True

    return False


def export_skill_filtered(source: Path, target: Path, global_excludes: list[str]) -> dict:
    """过滤复制 skill 目录到目标位置

    Returns:
        dict: {'copied': int, 'excluded': int, 'excluded_files': list}
    """
    local_excludes = load_exportignore(source)
    stats = {'copied': 0, 'excluded': 0, 'excluded_files': []}

    for root, dirs, files in os.walk(source):
        rel_root = Path(root).relative_to(source)

        for filename in files:
            rel_path = str(rel_root / filename) if str(rel_root) != '.' else filename

            if should_exclude(rel_path, global_excludes, local_excludes):
                stats['excluded'] += 1
                stats['excluded_files'].append(rel_path)
                continue

            # 创建目标目录并复制文件
            src_file = Path(root) / filename
            dst_file = target / rel_path
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dst_file)
            stats['copied'] += 1

    return stats


def get_filtered_hash(skill_path: Path, global_excludes: list[str]) -> str:
    """仅对导出文件（排除 .exportignore 和全局排除）计算哈希"""
    hasher = hashlib.md5()
    local_excludes = load_exportignore(skill_path)

    for root, dirs, files in os.walk(skill_path):
        dirs.sort()
        rel_root = Path(root).relative_to(skill_path)

        for filename in sorted(files):
            rel_path = str(rel_root / filename) if str(rel_root) != '.' else filename

            if should_exclude(rel_path, global_excludes, local_excludes):
                continue

            filepath = Path(root) / filename
            try:
                hasher.update(filepath.read_bytes())
            except:
                pass

    return hasher.hexdigest()


def generate_public_readme(repo_path: Path, skills: list[dict]) -> None:
    """生成面向读者的公共 README（含安装说明）"""
    # 构建 skill 表格行
    rows = []
    for i, skill in enumerate(sorted(skills, key=lambda s: s['name']), 1):
        name = skill['name']
        desc = skill.get('description', '')
        if len(desc) > 60:
            desc = desc[:60] + '...'
        rows.append(f"| {i} | [{name}](skills/{name}/) | {desc} |")

    table = '\n'.join(rows)

    # 读取已有的更新记录
    readme_path = repo_path / 'README.md'
    recent_updates = []
    if readme_path.exists():
        content = readme_path.read_text(encoding='utf-8')
        in_updates = False
        for line in content.split('\n'):
            if line.strip() == '## 更新记录':
                in_updates = True
                continue
            if in_updates and line.startswith('- **'):
                recent_updates.append(line)

    recent_updates = recent_updates[:10]
    updates_text = '\n'.join(recent_updates) if recent_updates else f'- **{datetime.now().strftime("%Y-%m-%d")}** — 首次导出'

    readme = f"""# Claude Code Skills

一组可复用的 Claude Code 技能（Skill），覆盖写作、Obsidian、图片生成、微信公众号等场景。

> 此仓库由 [skill-up](skills/skill-up/) 自动导出，已过滤个人配置和私有数据。

## 技能清单

| 序号 | 名称 | 描述 |
|------|------|------|
{table}

## 安装方式

### 方法一：手动复制

1. 将需要的 skill 文件夹复制到你的项目 `.claude/skills/` 目录下
2. 根据 skill 的 `SKILL.md` 说明进行个性化配置

### 方法二：克隆整个仓库

```bash
git clone <本仓库地址>
# 将需要的 skill 目录复制到你的项目中
cp -r skills/skill-name /path/to/your/project/.claude/skills/
```

## 注意事项

- 部分 skill 的 `references/` 目录下的个人文件已被过滤，你需要根据 SKILL.md 的说明创建自己的配置
- 每个 skill 的 SKILL.md 是核心入口文件，请先阅读了解用法
- 如果 skill 依赖外部 API（如 Gemini API），你需要自行配置 API Key

## 更新记录

{updates_text}
"""
    readme_path.write_text(readme, encoding='utf-8')


def add_update_record(repo_path: Path, synced_skills: list[str]) -> None:
    """在 README 的更新记录部分添加一条记录"""
    readme_path = repo_path / 'README.md'
    if not readme_path.exists():
        return

    timestamp = datetime.now().strftime('%Y-%m-%d')
    new_record = f"- **{timestamp}** — 导出 {', '.join(synced_skills)}"

    content = readme_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    new_lines = []
    inserted = False

    for line in lines:
        new_lines.append(line)
        if not inserted and line.strip() == '## 更新记录':
            new_lines.append('')
            new_lines.append(new_record)
            inserted = True

    readme_path.write_text('\n'.join(new_lines), encoding='utf-8')


def export_skills_to_repo(repo_path: Path, skills: list[dict], global_excludes: list[str]) -> dict:
    """导出 skills 到公共仓库（带过滤）"""
    results = {
        'exported': [],
        'unchanged': [],
        'errors': [],
        'filter_stats': {}
    }

    skills_dir = repo_path / 'skills'
    skills_dir.mkdir(exist_ok=True)

    for skill in skills:
        skill_name = skill['name']
        source_path = Path(skill['path'])
        target_path = skills_dir / skill_name

        try:
            # 检查是否需要导出
            if target_path.exists():
                source_hash = get_filtered_hash(source_path, global_excludes)
                target_hash = get_filtered_hash(target_path, global_excludes)

                if source_hash == target_hash:
                    results['unchanged'].append(skill_name)
                    continue

                # 删除旧版本
                shutil.rmtree(target_path)

            # 过滤复制
            stats = export_skill_filtered(source_path, target_path, global_excludes)
            results['exported'].append(skill_name)
            results['filter_stats'][skill_name] = stats

        except Exception as e:
            results['errors'].append(f"{skill_name}: {str(e)}")

    # 清理仓库中不再导出的 skill
    if skills_dir.exists():
        exported_names = {s['name'] for s in skills}
        for existing in skills_dir.iterdir():
            if existing.is_dir() and existing.name not in exported_names:
                shutil.rmtree(existing)
                results.setdefault('removed', []).append(existing.name)

    return results


def commit_and_push(repo_path: Path, exported_skills: list[str]) -> tuple[bool, str]:
    """提交并推送更新"""
    if not exported_skills:
        return True, "无需提交"

    success, msg = run_git(repo_path, 'add', '-A')
    if not success:
        return False, f"git add 失败: {msg}"

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    commit_msg = f"skill-up(public): 导出 {', '.join(exported_skills)} ({timestamp})"
    success, msg = run_git(repo_path, 'commit', '-m', commit_msg)
    if not success and 'nothing to commit' not in msg:
        return False, f"git commit 失败: {msg}"

    success, msg = run_git(repo_path, 'push')
    if not success:
        return False, f"git push 失败: {msg}"

    return True, "导出完成"


def main():
    if '--repo' not in sys.argv or '--skills' not in sys.argv:
        print("Usage: export_public.py --repo <repo_path> --skills '<skills_json>' --global-exclude '<exclude_json>'")
        sys.exit(1)

    repo_idx = sys.argv.index('--repo')
    skills_idx = sys.argv.index('--skills')

    repo_path = Path(sys.argv[repo_idx + 1])
    skills = json.loads(sys.argv[skills_idx + 1])

    # 全局排除规则（可选参数）
    global_excludes = []
    if '--global-exclude' in sys.argv:
        ge_idx = sys.argv.index('--global-exclude')
        global_excludes = json.loads(sys.argv[ge_idx + 1])

    # 检查仓库
    if not (repo_path / '.git').exists():
        print(json.dumps({'error': f'不是有效的 Git 仓库: {repo_path}'}, ensure_ascii=False))
        sys.exit(1)

    # 导出
    results = export_skills_to_repo(repo_path, skills, global_excludes)

    # 更新 README
    if results['exported']:
        generate_public_readme(repo_path, skills)
        add_update_record(repo_path, results['exported'])

    # 提交推送
    if results['exported']:
        success, msg = commit_and_push(repo_path, results['exported'])
        results['push_status'] = msg if success else f"错误: {msg}"

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

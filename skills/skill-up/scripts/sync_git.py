#!/usr/bin/env python3
"""
Git 同步脚本 - 将本地 skill 同步到 Git 仓库

Usage:
    sync_git.py --repo <repo_path> --skills <skills_json>

功能:
    1. 检测本地 skill 与仓库的差异
    2. 自动同步变更到仓库
    3. 提交并推送更新
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime


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


def get_skill_hash(skill_path: Path) -> str:
    """获取 skill 目录的内容哈希（用于检测变更）"""
    import hashlib
    hasher = hashlib.md5()

    for root, dirs, files in os.walk(skill_path):
        dirs.sort()
        for filename in sorted(files):
            filepath = Path(root) / filename
            try:
                hasher.update(filepath.read_bytes())
            except:
                pass

    return hasher.hexdigest()


def sync_skills_to_repo(repo_path: Path, skills: list) -> dict:
    """同步 skills 到仓库"""
    results = {
        'synced': [],
        'unchanged': [],
        'errors': []
    }

    skills_dir = repo_path / 'skills'
    skills_dir.mkdir(exist_ok=True)

    for skill in skills:
        skill_name = skill['name']
        source_path = Path(skill['path'])
        target_path = skills_dir / skill_name

        try:
            # 检查是否需要同步
            if target_path.exists():
                source_hash = get_skill_hash(source_path)
                target_hash = get_skill_hash(target_path)

                if source_hash == target_hash:
                    results['unchanged'].append(skill_name)
                    continue

                # 删除旧版本
                shutil.rmtree(target_path)

            # 复制新版本
            shutil.copytree(source_path, target_path)
            results['synced'].append(skill_name)

        except Exception as e:
            results['errors'].append(f"{skill_name}: {str(e)}")

    return results


def generate_readme(repo_path: Path, skills: list) -> None:
    """根据当前 skill 列表生成 README.md"""
    # 功能简称映射
    func_map = {
        'obsidian-markdown': 'Obsidian Markdown 编辑',
        'nanobanana-illustrator': '文章自动配图',
        'skill-creator': '创建/更新 Skill',
        'obsidian-bases': 'Obsidian 数据库视图',
        'file-organizer': '文件整理归档',
        'nanobanana-extractor': '图片风格提取',
        'skill-up': '技能管理',
        'wechat-extractor': '公众号文章提取',
        'json-canvas': 'Canvas 画布编辑',
        'web-artifacts-builder': 'Web 组件构建',
    }

    # 读取现有 README 中的"最近更新"部分
    readme_path = repo_path / 'README.md'
    recent_updates = []
    if readme_path.exists():
        content = readme_path.read_text(encoding='utf-8')
        in_updates = False
        for line in content.split('\n'):
            if line.strip() == '## 最近更新':
                in_updates = True
                continue
            if in_updates and line.startswith('- **'):
                recent_updates.append(line)

    # 构建 skill 表格行
    rows = []
    for i, skill in enumerate(sorted(skills, key=lambda s: s['name']), 1):
        name = skill['name']
        func = func_map.get(name, name)
        desc = skill.get('description', '')
        # 截取描述前40字
        if len(desc) > 40:
            desc = desc[:40] + '...'
        rows.append(f"| {i} | [{name}](skills/{name}/) | {func} | {desc} |")

    table = '\n'.join(rows)

    # 保留最近10条更新记录
    recent_updates = recent_updates[:10]
    updates_text = '\n'.join(recent_updates) if recent_updates else '- **' + datetime.now().strftime('%Y-%m-%d') + '** — 首次同步'

    readme = f"""# Zhouxing Skill

Claude Code 技能备份仓库，由 [skill-up](skills/skill-up/SKILL.md) 自动管理和同步。

## 仓库说明

这个仓库用于备份和版本管理我在 Claude Code 中使用的所有 Skill（技能）。每次 skill 有变更时，会自动同步到此仓库。

## Skill 清单

| 序号 | 名称 | 功能 | 描述 |
|------|------|------|------|
{table}

## 最近更新

{updates_text}
"""
    readme_path.write_text(readme, encoding='utf-8')


def add_update_record(repo_path: Path, synced_skills: list) -> None:
    """在 README 的最近更新部分添加一条记录"""
    readme_path = repo_path / 'README.md'
    if not readme_path.exists():
        return

    timestamp = datetime.now().strftime('%Y-%m-%d')
    new_record = f"- **{timestamp}** — 更新 {', '.join(synced_skills)}"

    content = readme_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    new_lines = []
    inserted = False

    for line in lines:
        new_lines.append(line)
        if not inserted and line.strip() == '## 最近更新':
            new_lines.append('')
            new_lines.append(new_record)
            inserted = True

    readme_path.write_text('\n'.join(new_lines), encoding='utf-8')


def commit_and_push(repo_path: Path, synced_skills: list) -> tuple[bool, str]:
    """提交并推送更新"""
    if not synced_skills:
        return True, "无需提交"

    # git add
    success, msg = run_git(repo_path, 'add', '-A')
    if not success:
        return False, f"git add 失败: {msg}"

    # git commit
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    commit_msg = f"skill-up: 同步 {', '.join(synced_skills)} ({timestamp})"
    success, msg = run_git(repo_path, 'commit', '-m', commit_msg)
    if not success and 'nothing to commit' not in msg:
        return False, f"git commit 失败: {msg}"

    # git push
    success, msg = run_git(repo_path, 'push')
    if not success:
        return False, f"git push 失败: {msg}"

    return True, "同步完成"


def main():
    # 解析参数
    if '--repo' not in sys.argv or '--skills' not in sys.argv:
        print("Usage: sync_git.py --repo <repo_path> --skills <skills_json>")
        sys.exit(1)

    repo_idx = sys.argv.index('--repo')
    skills_idx = sys.argv.index('--skills')

    repo_path = Path(sys.argv[repo_idx + 1])
    skills_json = sys.argv[skills_idx + 1]

    # 解析 skills
    skills = json.loads(skills_json)

    # 检查仓库
    if not (repo_path / '.git').exists():
        print(json.dumps({'error': f'不是有效的 Git 仓库: {repo_path}'}, ensure_ascii=False))
        sys.exit(1)

    # 同步
    results = sync_skills_to_repo(repo_path, skills)

    # 更新 README
    if results['synced']:
        generate_readme(repo_path, skills)
        add_update_record(repo_path, results['synced'])

    # 提交推送
    if results['synced']:
        success, msg = commit_and_push(repo_path, results['synced'])
        results['push_status'] = msg if success else f"错误: {msg}"

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

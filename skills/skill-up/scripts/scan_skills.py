#!/usr/bin/env python3
"""
扫描本地和全局 skill 目录，输出 JSON 格式的 skill 列表

Usage:
    scan_skills.py [--project-path <path>]

Output:
    JSON 格式的 skill 信息列表
"""

import json
import os
import sys
import re
from pathlib import Path


def extract_frontmatter(skill_md_path: Path) -> dict:
    """从 SKILL.md 提取 frontmatter 信息"""
    try:
        content = skill_md_path.read_text(encoding='utf-8')
        # 匹配 YAML frontmatter
        match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return {}

        frontmatter = {}
        for line in match.group(1).split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()
        return frontmatter
    except Exception:
        return {}


def scan_skill_directory(skills_dir: Path, scope: str) -> list:
    """扫描指定目录下的所有 skill"""
    skills = []

    if not skills_dir.exists():
        return skills

    for item in skills_dir.iterdir():
        if not item.is_dir():
            continue

        skill_md = item / 'SKILL.md'
        if not skill_md.exists():
            continue

        frontmatter = extract_frontmatter(skill_md)

        skills.append({
            'name': frontmatter.get('name', item.name),
            'description': frontmatter.get('description', '(无描述)'),
            'path': str(item),
            'scope': scope,
            'has_scripts': (item / 'scripts').exists(),
            'has_references': (item / 'references').exists(),
            'has_assets': (item / 'assets').exists(),
        })

    return skills


def main():
    # 解析参数
    project_path = None
    if '--project-path' in sys.argv:
        idx = sys.argv.index('--project-path')
        if idx + 1 < len(sys.argv):
            project_path = sys.argv[idx + 1]

    all_skills = []

    # 1. 扫描全局 skill 目录
    global_skills_dir = Path.home() / '.claude' / 'skills'
    all_skills.extend(scan_skill_directory(global_skills_dir, 'global'))

    # 2. 扫描项目级 skill 目录
    if project_path:
        project_skills_dir = Path(project_path) / '.claude' / 'skills'
        all_skills.extend(scan_skill_directory(project_skills_dir, 'project'))

    # 输出 JSON
    print(json.dumps(all_skills, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

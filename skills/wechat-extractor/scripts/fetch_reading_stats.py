#!/usr/bin/env python3
"""
批量获取微信公众号文章阅读数据（Mode 3 脚本）

工作流：
  1. 加载文章列表（从 JSON 文件或缓存）
  2. DNS monkey-patch 绕过 Shadowrocket Fake DNS
  3. 调用 get_batch_reading_stats 批量获取
  4. 输出 3 种格式：Markdown 表格、Obsidian Base、JSON

使用方式：
  python3 scripts/fetch_reading_stats.py --articles articles.json --output /path/to/output
  python3 scripts/fetch_reading_stats.py --articles articles.json --output /path/to/output --max 20
"""
import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

# 添加脚本目录到 path
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from wechat_api import WeChatMPAPI
from reader_credentials import ReaderCredentials


def load_articles(articles_path):
    """从 JSON 文件加载文章列表"""
    with open(articles_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 支持两种格式：直接数组 或 {articles: [...]}
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and 'articles' in data:
        return data['articles']
    else:
        print(f"❌ 无法解析文章列表文件格式")
        return []


def generate_markdown_table(articles, account_name=''):
    """生成 Markdown 表格

    属性映射（正确）：
    - old_like_num / old_like_count → 点赞 👍
    - like_num / like_count → 在看 👀
    """
    lines = []
    lines.append(f"# {account_name} 阅读数据\n")
    lines.append(f"> 获取时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    lines.append("")
    lines.append("| 序号 | 标题 | 日期 | 阅读量 | 点赞👍 | 在看👀 | 分享 | 评论 |")
    lines.append("|------|------|------|--------|--------|--------|------|------|")

    for i, article in enumerate(articles, 1):
        stats = article.get('reading_stats', {})
        create_time = article.get('create_time', 0)
        date_str = datetime.fromtimestamp(create_time).strftime('%Y-%m-%d') if create_time else '-'

        title = article.get('title', '未知标题')
        # 截断过长标题
        if len(title) > 40:
            title = title[:37] + '...'

        read_num = stats.get('read_num', '-')
        old_like = stats.get('old_like_num', stats.get('old_like_count', '-'))
        like = stats.get('like_num', stats.get('like_count', '-'))
        share = stats.get('share_count', '-')
        comment = stats.get('comment_count', '-')

        # 如果有错误，标记
        if stats.get('error'):
            lines.append(f"| {i} | {title} | {date_str} | ❌ | - | - | - | - |")
        else:
            lines.append(f"| {i} | {title} | {date_str} | {read_num} | {old_like} | {like} | {share} | {comment} |")

    # 统计摘要
    success_articles = [a for a in articles if a.get('reading_stats', {}).get('error') is None]
    if success_articles:
        total_read = sum(a['reading_stats'].get('read_num', 0) for a in success_articles)
        avg_read = total_read // len(success_articles) if success_articles else 0
        lines.append("")
        lines.append(f"**统计**：共 {len(articles)} 篇，成功获取 {len(success_articles)} 篇")
        lines.append(f"**总阅读量**：{total_read:,}  |  **平均阅读量**：{avg_read:,}")

    return '\n'.join(lines)


def generate_obsidian_base(articles, account_name, output_dir):
    """生成 Obsidian Base 文件 + 数据笔记

    创建：
    1. 数据子文件夹（含每篇文章的 .md 笔记 stub，带 frontmatter 属性）
    2. .base 文件（查询该文件夹，支持排序筛选）
    """
    data_folder_name = f"{account_name}_data"
    data_folder = output_dir / data_folder_name
    data_folder.mkdir(parents=True, exist_ok=True)

    # 生成数据笔记（每篇文章一个 .md 文件）
    for i, article in enumerate(articles, 1):
        stats = article.get('reading_stats', {})
        create_time = article.get('create_time', 0)
        date_str = datetime.fromtimestamp(create_time).strftime('%Y-%m-%d') if create_time else ''

        title = article.get('title', f'文章{i}')
        # 文件名安全处理
        safe_title = title.replace('/', '_').replace('\\', '_').replace(':', '_')
        safe_title = safe_title.replace('|', '_').replace('"', '_').replace('?', '_')
        safe_title = safe_title.replace('*', '_').replace('<', '_').replace('>', '_')
        if len(safe_title) > 60:
            safe_title = safe_title[:57] + '...'

        has_error = stats.get('error') is not None

        note_content = f"""---
title: "{title.replace('"', '\\"')}"
date: {date_str}
read_num: {stats.get('read_num', 0) if not has_error else 0}
like_thumb: {stats.get('old_like_num', 0) if not has_error else 0}
like_wow: {stats.get('like_num', 0) if not has_error else 0}
share_count: {stats.get('share_count', 0) if not has_error else 0}
comment_count: {stats.get('comment_count', 0) if not has_error else 0}
status: {"error" if has_error else "ok"}
---
"""
        note_path = data_folder / f"{date_str}_{safe_title}.md"
        with open(note_path, 'w', encoding='utf-8') as f:
            f.write(note_content)

    # 生成 .base 文件
    # 使用相对路径（相对于 .base 文件所在目录）
    base_content = f"""views:
  - type: table
    name: 阅读数据
    filters:
      and:
        - file.folder == "{data_folder_name}"
    sort:
      - property: date
        direction: DESC
"""

    return base_content, len(articles)


def generate_json_output(articles, account_name, target_biz=''):
    """生成完整 JSON 数据"""
    output = {
        'account_name': account_name,
        '__biz': target_biz,
        'fetch_time': datetime.now().isoformat(),
        'fetch_timestamp': time.time(),
        'total': len(articles),
        'success': sum(1 for a in articles if a.get('reading_stats', {}).get('error') is None),
        'articles': []
    }

    for article in articles:
        stats = article.get('reading_stats', {})
        create_time = article.get('create_time', 0)

        item = {
            'title': article.get('title', ''),
            'link': article.get('link', ''),
            'date': datetime.fromtimestamp(create_time).strftime('%Y-%m-%d') if create_time else '',
            'create_time': create_time,
            '__biz': target_biz,
            'mid': article.get('aid', ''),
            'sn': '',
            'reading_stats': {
                'read_num': stats.get('read_num', 0),
                'old_like_num': stats.get('old_like_num', 0),
                'like_num': stats.get('like_num', 0),
                'share_count': stats.get('share_count', 0),
                'comment_count': stats.get('comment_count', 0),
                'error': stats.get('error'),
            }
        }

        # 从 link 中提取 mid/sn
        link = article.get('link', '')
        if link:
            params = WeChatMPAPI.parse_article_url(link)
            item['mid'] = params.get('mid', '')
            item['sn'] = params.get('sn', '')

        output['articles'].append(item)

    return output


def main():
    import argparse

    parser = argparse.ArgumentParser(description='批量获取公众号文章阅读数据')
    parser.add_argument('--articles', required=True, help='文章列表 JSON 文件路径')
    parser.add_argument('--output', required=True, help='输出目录路径')
    parser.add_argument('--name', default='', help='公众号名称（用于文件命名）')
    parser.add_argument('--max', type=int, default=None, help='最大获取数量')
    parser.add_argument('--delay', type=int, default=5, help='请求间隔（秒），默认 5')
    parser.add_argument('--no-dns-patch', action='store_true', help='跳过 DNS monkey-patch')

    args = parser.parse_args()

    # 1. 加载文章列表
    print(f"📂 加载文章列表: {args.articles}")
    articles = load_articles(args.articles)
    if not articles:
        print("❌ 文章列表为空")
        sys.exit(1)
    print(f"   共 {len(articles)} 篇文章")

    # 2. 提取 __biz
    api = WeChatMPAPI()
    target_biz = api.get_biz_from_articles(articles) or ''
    if target_biz:
        print(f"   __biz: {target_biz[:12]}...")

    # 3. 加载读者凭证
    cred_mgr = ReaderCredentials()
    credentials = cred_mgr.load()
    if not credentials:
        print("❌ 无有效的读者凭证，请先获取凭证")
        sys.exit(1)

    age_info = cred_mgr.get_age_info()
    print(f"🔐 读者凭证: {age_info}")

    # 检查 biz 匹配
    if target_biz:
        biz_check = cred_mgr.is_valid_for_biz(target_biz)
        if not biz_check['valid']:
            if biz_check['reason'] == 'biz_mismatch':
                print(f"⚠️ 凭证 __biz 不匹配目标公众号，需要重新获取凭证")
                sys.exit(1)
            elif biz_check['reason'] == 'no_biz_in_credentials':
                print(f"⚠️ 凭证无 __biz 字段（旧格式），继续尝试...")

    # 4. DNS monkey-patch
    if not args.no_dns_patch:
        print("\n🔧 DNS monkey-patch...")
        real_ip = api.dns_monkey_patch()
        if not real_ip:
            print("⚠️ DNS patch 失败，继续尝试（可能不影响）")

    # 5. 批量获取阅读数据
    print(f"\n📊 开始批量获取...")
    result = api.get_batch_reading_stats(
        articles=articles,
        credentials=credentials,
        delay=args.delay,
        max_count=args.max,
        show_progress=True,
        method='html'
    )

    # 6. 输出结果
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    account_name = args.name or '公众号'

    # 6a. Markdown 表格
    md_content = generate_markdown_table(result, account_name)
    md_path = output_dir / f"{account_name}_阅读数据.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"\n✅ Markdown 表格: {md_path}")

    # 6b. Obsidian Base
    base_content, note_count = generate_obsidian_base(result, account_name, output_dir)
    base_path = output_dir / f"{account_name}_阅读数据.base"
    with open(base_path, 'w', encoding='utf-8') as f:
        f.write(base_content)
    print(f"✅ Obsidian Base: {base_path} ({note_count} 笔记)")

    # 6c. JSON
    json_data = generate_json_output(result, account_name, target_biz)
    json_path = output_dir / f"{account_name}_阅读数据.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    print(f"✅ JSON 数据: {json_path}")

    # 7. 摘要
    success = json_data['success']
    total = json_data['total']
    print(f"\n🎉 完成！成功获取 {success}/{total} 篇文章的阅读数据")


if __name__ == '__main__':
    main()

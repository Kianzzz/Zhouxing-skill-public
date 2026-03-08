#!/usr/bin/env python3
"""
搜索公众号并获取所有文章用于分析
"""
import sys
import json
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from wechat_api_browser import WeChatMPAPIBrowser


def main():
    query = "四月槐汐"

    print(f"🔍 开始搜索公众号: {query}")

    # 初始化API
    api = WeChatMPAPIBrowser()

    if not api.is_logged_in():
        print("❌ 未登录，请先运行 login_smart.py 登录")
        return

    # 搜索公众号
    print(f"\n📡 正在搜索公众号...")
    accounts = api.search_account(query, count=10)

    if not accounts:
        print(f"❌ 未找到公众号: {query}")
        return

    print(f"\n✅ 找到 {len(accounts)} 个公众号:")
    for i, acc in enumerate(accounts, 1):
        print(f"   {i}. {acc.get('nickname', '未知')}")
        print(f"      微信号: {acc.get('alias', '无')}")
        print(f"      fakeid: {acc.get('fakeid', 'N/A')}")

    # 使用第一个结果
    target_account = accounts[0]
    fakeid = target_account.get('fakeid')
    nickname = target_account.get('nickname', '未知')

    print(f"\n📊 开始获取「{nickname}」的文章列表...")

    # 获取所有文章
    from analyze_account_browser import get_all_articles_browser
    articles = get_all_articles_browser(api, fakeid)

    if not articles:
        print("❌ 未获取到文章")
        return

    # 保存数据
    output_file = Path(__file__).parent.parent / f"data_{nickname}.json"
    output_data = {
        'account': {
            'nickname': nickname,
            'alias': target_account.get('alias', ''),
            'fakeid': fakeid,
            'signature': target_account.get('signature', ''),
        },
        'total_articles': len(articles),
        'articles': articles
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ 数据已保存到: {output_file}")
    print(f"   公众号: {nickname}")
    print(f"   文章总数: {len(articles)}")

    # 显示最近10篇文章
    print(f"\n📋 最近10篇文章:")
    for i, article in enumerate(articles[:10], 1):
        title = article.get('title', '无标题')
        create_time = article.get('create_time', 0)
        from datetime import datetime
        date_str = datetime.fromtimestamp(create_time).strftime('%Y-%m-%d')
        print(f"   {i}. {title} ({date_str})")

    # 关闭浏览器
    if api.browser:
        api.browser.close()

    return output_file


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""测试新的appmsgpublish接口"""
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.wechat_api import WeChatMPAPI

def main():
    print("=" * 60)
    print("🧪 测试新的appmsgpublish接口")
    print("=" * 60)
    print()

    api = WeChatMPAPI()

    # 检查登录状态
    if not api.is_logged_in():
        print("❌ 未登录，请先登录")
        print("运行: python3 scripts/login_smart.py")
        return

    print("✅ 已登录")
    print()

    # 测试搜索公众号
    print("🔍 步骤1: 搜索公众号 '反向的猫'")
    print("-" * 60)
    accounts = api.search_account('反向的猫', count=3)

    if not accounts:
        print("❌ 搜索失败或无结果")
        return

    print(f"✅ 找到 {len(accounts)} 个公众号")
    for i, account in enumerate(accounts, 1):
        print(f"{i}. {account.get('nickname', '未知')}")
        print(f"   微信号: {account.get('alias', '无')}")
        print(f"   fakeid: {account.get('fakeid', '无')[:30]}...")
        print()

    # 选择第一个公众号
    target_account = accounts[0]
    fakeid = target_account.get('fakeid')
    nickname = target_account.get('nickname')

    print("=" * 60)
    print(f"🔍 步骤2: 获取 '{nickname}' 的文章列表")
    print("-" * 60)

    # 使用新接口获取文章
    result = api.get_articles(fakeid, begin=0, count=5)

    articles = result.get('articles', [])
    total = result.get('total', 0)

    if articles:
        print(f"✅ 成功获取文章！")
        print(f"   本次获取: {len(articles)} 篇")
        print(f"   总共: {total} 篇")
        print()
        print("📋 文章列表：")
        print("-" * 60)
        for i, article in enumerate(articles[:5], 1):
            title = article.get('title', '未知标题')
            link = article.get('link', '')
            create_time = article.get('create_time', 0)

            # 转换时间戳
            import time
            if create_time:
                date_str = time.strftime('%Y-%m-%d %H:%M', time.localtime(create_time))
            else:
                date_str = '未知日期'

            print(f"{i}. {title}")
            print(f"   日期: {date_str}")
            print(f"   链接: {link[:60]}...")
            print()

        print("=" * 60)
        print("🎉 新接口测试成功！")
        print("=" * 60)
    else:
        print("❌ 未获取到文章")
        print(f"   可能原因：接口返回格式不符合预期")

if __name__ == '__main__':
    main()

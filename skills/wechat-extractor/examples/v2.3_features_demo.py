#!/usr/bin/env python3
"""
V2.3 新功能演示脚本
展示元数据导出、高级筛选、缓存功能的使用方法
"""

import sys
from pathlib import Path

# 添加父目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from scripts.wechat_api import WeChatMPAPI


def demo_metadata_export():
    """演示 1: 元数据导出功能"""
    print("\n" + "="*60)
    print("演示 1: 获取文章元数据（阅读量、点赞数等）")
    print("="*60)

    api = WeChatMPAPI()

    # 注意：这需要真实的 credentials
    # 获取方法：参考 https://docs.mptext.top/advanced/wxdown-service.html
    credentials = {
        'appmsg_token': 'your_appmsg_token_here',
        'cookie': 'your_cookie_here'
    }

    article_url = 'https://mp.weixin.qq.com/s/xxxxx'

    print(f"\n📊 正在获取文章元数据...")
    print(f"   文章链接: {article_url}")

    metadata = api.get_article_metadata(article_url, credentials)

    if metadata:
        print(f"\n✅ 元数据获取成功：")
        print(f"   阅读量: {metadata['read_num']:,}")
        print(f"   点赞数: {metadata['like_num']:,}")
        print(f"   评论数: {metadata['comment_count']:,}")
        print(f"   分享数: {metadata['share_count']:,}")
        print(f"   是否原创: {'是' if metadata['is_original'] else '否'}")
    else:
        print("\n⚠️ 元数据获取失败（需要提供有效的 credentials）")


def demo_advanced_search():
    """演示 2: 高级筛选功能"""
    print("\n" + "="*60)
    print("演示 2: 高级筛选功能（多条件组合）")
    print("="*60)

    api = WeChatMPAPI()

    if not api.is_logged_in():
        print("\n⚠️ 未登录，跳过演示")
        print("   请先运行 api.login() 登录")
        return

    # 搜索公众号
    accounts = api.search_account("婷在路上的日子")
    if not accounts:
        print("\n⚠️ 未找到公众号，跳过演示")
        return

    fakeid = accounts[0]['fakeid']

    # 高级搜索：最近30天、阅读量>10000、仅原创
    print(f"\n🔍 搜索条件：")
    print(f"   时间范围: 最近 30 天")
    print(f"   最小阅读量: 10,000")
    print(f"   文章类型: 仅原创")

    from datetime import datetime, timedelta
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    articles = api.search_articles_advanced(
        fakeid=fakeid,
        start_date=start_date.strftime('%Y-%m-%d'),
        min_read_num=10000,
        is_original=True,
        max_count=10
    )

    print(f"\n✅ 找到 {len(articles)} 篇符合条件的文章")
    for i, article in enumerate(articles[:5], 1):
        print(f"   {i}. {article['title']}")
        if 'read_num' in article:
            print(f"      阅读 {article['read_num']:,} | 点赞 {article.get('like_num', 0):,}")


def demo_cache_system():
    """演示 3: 智能缓存系统"""
    print("\n" + "="*60)
    print("演示 3: 智能缓存系统")
    print("="*60)

    api = WeChatMPAPI()

    if not api.is_logged_in():
        print("\n⚠️ 未登录，跳过演示")
        return

    # 搜索公众号
    accounts = api.search_account("洞见")
    if not accounts:
        print("\n⚠️ 未找到公众号，跳过演示")
        return

    fakeid = accounts[0]['fakeid']

    # 第一次获取：会从服务器加载并缓存
    print(f"\n📥 第一次获取文章列表（会从服务器加载）...")
    articles1 = api.get_all_articles_cached(
        fakeid=fakeid,
        max_count=10,
        use_cache=True,
        cache_hours=24
    )
    print(f"   获取到 {len(articles1)} 篇文章")

    # 第二次获取：会使用缓存
    print(f"\n⚡ 第二次获取文章列表（会使用缓存）...")
    articles2 = api.get_all_articles_cached(
        fakeid=fakeid,
        max_count=10,
        use_cache=True,
        cache_hours=24
    )
    print(f"   获取到 {len(articles2)} 篇文章")

    # 手动清除缓存
    print(f"\n🗑️ 清除缓存...")
    api.clear_cache(fakeid=fakeid)

    print(f"\n💡 缓存说明：")
    print(f"   - 默认有效期: 24 小时")
    print(f"   - 缓存位置: ~/.wechat-extractor/cache/")
    print(f"   - 命名格式: articles_{{fakeid}}.json")


def demo_combined_features():
    """演示 4: 组合使用多个新功能"""
    print("\n" + "="*60)
    print("演示 4: 组合使用（缓存 + 高级筛选 + 元数据）")
    print("="*60)

    api = WeChatMPAPI()

    if not api.is_logged_in():
        print("\n⚠️ 未登录，跳过演示")
        return

    # 搜索公众号
    accounts = api.search_account("洞见")
    if not accounts:
        print("\n⚠️ 未找到公众号，跳过演示")
        return

    fakeid = accounts[0]['fakeid']

    # 步骤1: 使用缓存快速获取文章列表
    print(f"\n步骤 1: 使用缓存获取文章列表...")
    all_articles = api.get_all_articles_cached(
        fakeid=fakeid,
        use_cache=True,
        cache_hours=24
    )
    print(f"   ✅ 获取到 {len(all_articles)} 篇文章")

    # 步骤2: 使用高级筛选过滤文章
    print(f"\n步骤 2: 使用高级筛选（仅合集文章）...")
    filtered_articles = api.search_articles_advanced(
        fakeid=fakeid,
        has_collection=True,  # 仅合集文章
        max_count=10
    )
    print(f"   ✅ 筛选后剩余 {len(filtered_articles)} 篇文章")

    # 步骤3: 为筛选后的文章获取元数据（需要 credentials）
    print(f"\n步骤 3: 获取文章元数据...")
    print(f"   ⚠️ 需要提供 credentials（此处仅演示流程）")

    # credentials = {
    #     'appmsg_token': 'xxx',
    #     'cookie': 'xxx'
    # }
    #
    # for article in filtered_articles[:3]:
    #     metadata = api.get_article_metadata(
    #         article_url=article['link'],
    #         credentials=credentials
    #     )
    #     if metadata:
    #         article.update(metadata)

    print(f"\n✅ 组合使用演示完成！")
    print(f"   实际使用中可以根据需求灵活组合这些功能")


def main():
    """主函数"""
    print("\n" + "🚀"*30)
    print("  V2.3 新功能演示")
    print("🚀"*30)

    print("\n📝 本演示将展示以下功能：")
    print("   1. 元数据导出（阅读量、点赞数等）")
    print("   2. 高级筛选（作者、阅读量、合集等）")
    print("   3. 智能缓存系统")
    print("   4. 组合使用多个功能")

    # 运行各个演示
    demo_metadata_export()
    demo_advanced_search()
    demo_cache_system()
    demo_combined_features()

    print("\n" + "="*60)
    print("演示完成！")
    print("="*60)
    print("\n💡 提示：")
    print("   - 元数据功能需要提供 credentials（通过抓包获取）")
    print("   - 高级筛选和缓存功能可直接使用")
    print("   - 详细文档请查看 SKILL.md")
    print()


if __name__ == '__main__':
    main()

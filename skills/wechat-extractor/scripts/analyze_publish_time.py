#!/usr/bin/env python3
"""
分析公众号发布时间规律
"""
import sys
import json
from datetime import datetime, timedelta
from collections import defaultdict
from wechat_api import WeChatMPAPI

def analyze_publish_pattern(articles, account_name):
    """分析发布时间规律"""
    if not articles:
        print(f"\n❌ {account_name}: 没有找到文章")
        return None

    # 统计数据
    by_weekday = defaultdict(int)  # 星期几
    by_hour = defaultdict(int)     # 几点钟
    by_month = defaultdict(int)    # 每月文章数

    weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

    for article in articles:
        create_time = article.get('create_time', 0)
        dt = datetime.fromtimestamp(create_time)

        # 统计星期几
        weekday = dt.weekday()
        by_weekday[weekday] += 1

        # 统计发布时间
        by_hour[dt.hour] += 1

        # 统计每月
        month_key = dt.strftime('%Y-%m')
        by_month[month_key] += 1

    # 打印分析结果
    print(f"\n{'='*60}")
    print(f"📊 {account_name} - 发布规律分析")
    print(f"{'='*60}")
    print(f"总文章数：{len(articles)}")
    print(f"时间范围：{datetime.fromtimestamp(articles[-1]['create_time']).strftime('%Y-%m-%d')} ~ {datetime.fromtimestamp(articles[0]['create_time']).strftime('%Y-%m-%d')}")

    # 星期分布
    print(f"\n📅 星期分布：")
    for i in range(7):
        count = by_weekday[i]
        percentage = count / len(articles) * 100
        bar = '█' * int(percentage / 2)
        print(f"  {weekday_names[i]}: {count:3d} 篇 ({percentage:5.1f}%) {bar}")

    # 时间分布
    print(f"\n⏰ 发布时间分布（前5个高峰时段）：")
    sorted_hours = sorted(by_hour.items(), key=lambda x: x[1], reverse=True)[:5]
    for hour, count in sorted_hours:
        percentage = count / len(articles) * 100
        print(f"  {hour:02d}:00 - {hour+1:02d}:00: {count:3d} 篇 ({percentage:5.1f}%)")

    # 每月分布
    print(f"\n📈 每月发布数（近12个月）：")
    sorted_months = sorted(by_month.items(), reverse=True)[:12]
    for month, count in sorted_months:
        avg_per_week = count / 4.3
        bar = '▓' * int(count / 2)
        print(f"  {month}: {count:3d} 篇 (平均 {avg_per_week:.1f} 篇/周) {bar}")

    return {
        'total': len(articles),
        'by_weekday': dict(by_weekday),
        'by_hour': dict(by_hour),
        'by_month': dict(by_month),
        'most_frequent_weekday': weekday_names[max(by_weekday.items(), key=lambda x: x[1])[0]],
        'most_frequent_hour': max(by_hour.items(), key=lambda x: x[1])[0]
    }

def main():
    if len(sys.argv) < 2:
        print("用法: python3 analyze_publish_time.py <公众号名称1> [公众号名称2] ...")
        sys.exit(1)

    account_names = sys.argv[1:]

    api = WeChatMPAPI()

    # 检查登录状态
    if not api.is_logged_in():
        print("❌ 未登录，请先登录")
        print("\n请运行以下命令登录：")
        print("python3 -c \"from wechat_api import WeChatMPAPI; api = WeChatMPAPI(); api.login()\"")
        sys.exit(1)

    # 计算一年前的日期
    one_year_ago = datetime.now() - timedelta(days=365)
    start_date = one_year_ago.strftime('%Y-%m-%d')

    results = {}

    for account_name in account_names:
        print(f"\n🔍 正在搜索公众号: {account_name}")

        # 搜索公众号
        search_results = api.search_account(account_name, count=5)

        if not search_results:
            print(f"❌ 未找到公众号: {account_name}")
            continue

        # 取第一个结果
        account = search_results[0]
        fakeid = account['fakeid']
        nickname = account['nickname']

        print(f"✅ 找到: {nickname}")
        print(f"   正在获取近一年的文章列表...")

        # 获取文章列表（使用缓存）
        articles = api.get_all_articles_cached(
            fakeid=fakeid,
            use_cache=True,
            cache_hours=24
        )

        if not articles:
            print(f"❌ 未获取到文章")
            continue

        # 筛选近一年的文章
        filtered_articles = []
        for article in articles:
            create_time = article.get('create_time', 0)
            dt = datetime.fromtimestamp(create_time)
            if dt >= one_year_ago:
                filtered_articles.append(article)

        print(f"   共 {len(articles)} 篇文章，近一年 {len(filtered_articles)} 篇")

        # 分析发布规律
        pattern = analyze_publish_pattern(filtered_articles, nickname)
        results[nickname] = pattern

    # 打印对比总结
    if len(results) > 1:
        print(f"\n\n{'='*60}")
        print("📋 对比总结")
        print(f"{'='*60}")

        for name, pattern in results.items():
            if pattern:
                print(f"\n{name}:")
                print(f"  • 总发布: {pattern['total']} 篇")
                print(f"  • 最常发布日: {pattern['most_frequent_weekday']}")
                print(f"  • 最常发布时间: {pattern['most_frequent_hour']}:00")

if __name__ == '__main__':
    main()

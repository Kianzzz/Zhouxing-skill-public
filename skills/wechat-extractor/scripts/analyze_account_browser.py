#!/usr/bin/env python3
"""
分析公众号文章统计数据（完全基于浏览器API）
"""

import sys
import json
import time
import re
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# 添加当前目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from wechat_api_browser import WeChatMPAPIBrowser


def get_all_articles_browser(api, fakeid, max_count=None):
    """使用浏览器API获取所有文章"""
    all_articles = []
    begin = 0
    page_size = 5

    print(f"📥 开始获取文章列表...")

    while True:
        # 构建URL
        token = api.config.get('token', '')
        url = f'https://mp.weixin.qq.com/cgi-bin/appmsg?action=list_ex&fakeid={fakeid}&begin={begin}&count={page_size}&type=9&query=&token={token}&lang=zh_CN&f=json&ajax=1'

        try:
            api.page.goto(url, wait_until='domcontentloaded', timeout=10000)
            time.sleep(0.5)

            # 获取响应
            content = api.page.content()
            json_match = re.search(r'<pre[^>]*>(.*?)</pre>', content, re.DOTALL)

            if json_match:
                data = json.loads(json_match.group(1))

                # 调试：打印错误信息
                if data.get('base_resp', {}).get('ret') != 0:
                    error_msg = data.get('base_resp', {}).get('err_msg', '未知错误')
                    error_ret = data.get('base_resp', {}).get('ret', -1)
                    print(f"⚠️  API返回错误 (ret={error_ret}): {error_msg}")
                    print(f"   Token: {token[:20] if token else 'None'}...")
                    print(f"   Fakeid: {fakeid}")

                if data.get('base_resp', {}).get('ret') == 0:
                    articles = data.get('app_msg_list', [])
                    total = data.get('app_msg_cnt', 0)

                    if not articles:
                        break

                    all_articles.extend(articles)

                    # 显示进度
                    if total > 0:
                        progress = min(100, int(len(all_articles) / total * 100))
                        print(f"   进度: {len(all_articles)}/{total} ({progress}%)")

                    # 检查是否达到最大数量
                    if max_count and len(all_articles) >= max_count:
                        all_articles = all_articles[:max_count]
                        break

                    # 检查是否还有更多
                    if begin + len(articles) >= total:
                        break

                    begin += page_size
                else:
                    error_msg = data.get('base_resp', {}).get('err_msg', '未知错误')
                    print(f"❌ 获取文章列表失败: {error_msg}")
                    break
            else:
                print("❌ 无法解析响应")
                break

        except Exception as e:
            print(f"❌ 获取文章失败: {e}")
            break

    print(f"✅ 共获取 {len(all_articles)} 篇文章")
    return all_articles


def analyze_publishing_pattern(articles, months=6):
    """分析文章发布规律"""
    # 计算时间范围
    now = datetime.now()
    start_date = now - timedelta(days=months * 30)
    start_ts = int(start_date.timestamp())

    # 按月份统计
    monthly_count = defaultdict(int)
    # 按星期统计
    weekly_count = defaultdict(int)
    # 按小时统计
    hourly_count = defaultdict(int)

    # 筛选近期文章
    recent_articles = []
    for article in articles:
        # 使用 update_time（发布时间）而不是 create_time（创建时间）
        publish_time = article.get('update_time', article.get('create_time', 0))
        if publish_time >= start_ts:
            # 保存发布时间到文章对象中
            article['publish_time'] = publish_time
            recent_articles.append(article)

            dt = datetime.fromtimestamp(publish_time)

            # 月份统计
            month_key = dt.strftime('%Y-%m')
            monthly_count[month_key] += 1

            # 星期统计
            weekday = dt.strftime('%A')
            weekday_cn = {
                'Monday': '周一',
                'Tuesday': '周二',
                'Wednesday': '周三',
                'Thursday': '周四',
                'Friday': '周五',
                'Saturday': '周六',
                'Sunday': '周日'
            }
            weekly_count[weekday_cn.get(weekday, weekday)] += 1

            # 小时统计
            hour_key = dt.strftime('%H:00')
            hourly_count[hour_key] += 1

    return {
        'total': len(recent_articles),
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': now.strftime('%Y-%m-%d'),
        'monthly': dict(sorted(monthly_count.items())),
        'weekly': dict(sorted(weekly_count.items(),
                             key=lambda x: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'].index(x[0]) if x[0] in ['周一', '周二', '周三', '周四', '周五', '周六', '周日'] else 999)),
        'hourly': dict(sorted(hourly_count.items())),
        'articles': recent_articles
    }


def print_statistics(stats):
    """打印统计结果"""
    print(f"\n📊 统计数据（{stats['start_date']} ~ {stats['end_date']}）")
    print(f"总计：{stats['total']} 篇文章\n")

    if stats['total'] == 0:
        print("⚠️  近期没有发布文章")
        return

    # 月度统计
    print("📅 月度发布统计：")
    max_count = max(stats['monthly'].values()) if stats['monthly'] else 1
    for month, count in stats['monthly'].items():
        bar_length = int(count / max_count * 30)
        bar = '█' * bar_length
        print(f"   {month}: {bar} ({count} 篇)")

    # 平均发布频率
    months_count = len(stats['monthly'])
    if months_count > 0:
        avg_per_month = stats['total'] / months_count
        print(f"\n   平均每月：{avg_per_month:.1f} 篇")

    # 星期统计
    print("\n📆 星期发布统计：")
    max_count = max(stats['weekly'].values()) if stats['weekly'] else 1
    for weekday, count in stats['weekly'].items():
        bar_length = int(count / max_count * 20)
        bar = '█' * bar_length
        print(f"   {weekday}: {bar} ({count} 篇)")

    # 找出最常发布的星期
    if stats['weekly']:
        max_weekday = max(stats['weekly'].items(), key=lambda x: x[1])
        print(f"\n   最常发布：{max_weekday[0]} ({max_weekday[1]} 篇)")

    # 时段统计（只显示有文章的时段）
    if stats['hourly']:
        print("\n🕐 时段发布统计：")
        max_count = max(stats['hourly'].values()) if stats['hourly'] else 1
        for hour, count in stats['hourly'].items():
            if count > 0:
                bar_length = int(count / max_count * 20)
                bar = '█' * bar_length
                print(f"   {hour}: {bar} ({count} 篇)")

        # 找出最常发布的时段
        max_hour = max(stats['hourly'].items(), key=lambda x: x[1])
        print(f"\n   最常发布时段：{max_hour[0]} ({max_hour[1]} 篇)")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 analyze_account_browser.py <公众号名称> [月数]")
        print("示例: python3 analyze_account_browser.py 肥猫说财 6")
        sys.exit(1)

    account_name = sys.argv[1]
    months = int(sys.argv[2]) if len(sys.argv) > 2 else 6

    print(f"🔍 正在搜索公众号：{account_name}")

    # 初始化 API（使用浏览器版本）
    api = WeChatMPAPIBrowser()

    if not api.is_logged_in():
        print("❌ 未登录，请先运行登录脚本")
        print("   python3 scripts/login_smart.py")
        sys.exit(1)

    try:
        # 搜索公众号
        accounts = api.search_account(account_name, count=5)

        if not accounts:
            print(f"❌ 未找到公众号：{account_name}")
            sys.exit(1)

        # 选择第一个结果
        account = accounts[0]
        print(f"\n✅ 找到公众号：{account['nickname']}")
        print(f"   微信号：{account.get('alias', '未设置')}")
        print(f"   fakeid：{account['fakeid']}")

        # 获取所有文章（使用浏览器API）
        fakeid = account['fakeid']
        all_articles = get_all_articles_browser(api, fakeid)

        if not all_articles:
            print("\n❌ 未能获取文章列表，可能需要重新登录")
            sys.exit(1)

        # 分析统计数据
        print(f"\n🔬 分析近 {months} 个月的发布规律...")
        stats = analyze_publishing_pattern(all_articles, months)

        # 打印统计结果
        print_statistics(stats)

        # 显示最近 5 篇文章
        if stats['articles']:
            print(f"\n📝 最近 5 篇文章：")
            for i, article in enumerate(stats['articles'][:5], 1):
                # 使用 publish_time（已在 analyze_publishing_pattern 中添加）
                publish_time = article.get('publish_time', article.get('update_time', article.get('create_time', 0)))
                dt = datetime.fromtimestamp(publish_time)
                date_str = dt.strftime('%Y-%m-%d %H:%M')
                print(f"   {i}. {article['title']}")
                print(f"      发布时间：{date_str}")
                print()

    finally:
        # 关闭浏览器
        api.close()


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
搜索公众号并获取所有文章（温和模式）
"""
import sys
import json
import time
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from wechat_api_browser import WeChatMPAPIBrowser


def main():
    query = "四月槐汐"

    print(f"🔍 开始搜索公众号: {query}")
    print(f"⏰ 等待30秒以避免频率限制...")
    time.sleep(30)

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
    print(f"⏰ 使用温和模式，每页等待5秒...")

    # 手动获取文章，增加延迟
    all_articles = []
    begin = 0
    page_size = 5
    max_retries = 3

    api._ensure_browser()

    while True:
        retry_count = 0
        success = False

        while retry_count < max_retries and not success:
            try:
                # 构建URL
                token = api.config.get('token', '')
                url = f'https://mp.weixin.qq.com/cgi-bin/appmsg?action=list_ex&fakeid={fakeid}&begin={begin}&count={page_size}&type=9&query=&token={token}&lang=zh_CN&f=json&ajax=1'

                print(f"\n请求第 {begin // page_size + 1} 页...")
                api.page.goto(url, wait_until='domcontentloaded', timeout=15000)
                time.sleep(5)  # 增加等待时间

                # 获取响应
                content = api.page.content()
                import re
                json_match = re.search(r'<pre[^>]*>(.*?)</pre>', content, re.DOTALL)

                if json_match:
                    data = json.loads(json_match.group(1))

                    if data.get('base_resp', {}).get('ret') == 0:
                        articles = data.get('app_msg_list', [])
                        total = data.get('app_msg_cnt', 0)

                        if not articles:
                            print("✅ 已获取所有文章")
                            success = True
                            break

                        all_articles.extend(articles)

                        # 显示进度
                        if total > 0:
                            progress = min(100, int(len(all_articles) / total * 100))
                            print(f"   进度: {len(all_articles)}/{total} ({progress}%)")

                        # 检查是否还有更多
                        if begin + len(articles) >= total:
                            print("✅ 已获取所有文章")
                            success = True
                            break

                        begin += page_size
                        success = True

                    elif data.get('base_resp', {}).get('ret') == 200013:
                        print(f"⚠️  频率限制，等待60秒后重试...")
                        time.sleep(60)
                        retry_count += 1
                    else:
                        error_msg = data.get('base_resp', {}).get('err_msg', '未知错误')
                        print(f"❌ API错误: {error_msg}")
                        break
                else:
                    print("❌ 无法解析响应")
                    break

            except Exception as e:
                print(f"❌ 请求失败: {e}")
                retry_count += 1
                if retry_count < max_retries:
                    print(f"等待30秒后重试...")
                    time.sleep(30)

        if not success:
            print(f"❌ 达到最大重试次数，停止获取")
            break

    print(f"\n✅ 共获取 {len(all_articles)} 篇文章")

    if not all_articles:
        print("❌ 未获取到文章")
        api.browser.close()
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
        'total_articles': len(all_articles),
        'articles': articles
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ 数据已保存到: {output_file}")
    print(f"   公众号: {nickname}")
    print(f"   文章总数: {len(all_articles)}")

    # 显示最近10篇文章
    print(f"\n📋 最近10篇文章:")
    for i, article in enumerate(all_articles[:10], 1):
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

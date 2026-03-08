#!/usr/bin/env python3
"""
调试时间显示问题
"""

import sys
import json
import time
import re
from pathlib import Path
from datetime import datetime

# 添加当前目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from wechat_api_browser import WeChatMPAPIBrowser


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 debug_time.py <公众号名称>")
        sys.exit(1)

    account_name = sys.argv[1]

    print(f"🔍 正在搜索公众号：{account_name}")

    # 初始化 API
    api = WeChatMPAPIBrowser()

    if not api.is_logged_in():
        print("❌ 未登录")
        sys.exit(1)

    try:
        # 搜索公众号
        accounts = api.search_account(account_name, count=5)

        if not accounts:
            print(f"❌ 未找到公众号")
            sys.exit(1)

        account = accounts[0]
        fakeid = account['fakeid']

        print(f"\n✅ 找到公众号：{account['nickname']}")

        # 获取最近5篇文章
        token = api.config.get('token', '')
        url = f'https://mp.weixin.qq.com/cgi-bin/appmsg?action=list_ex&fakeid={fakeid}&begin=0&count=5&type=9&query=&token={token}&lang=zh_CN&f=json&ajax=1'

        api.page.goto(url, wait_until='domcontentloaded', timeout=10000)
        time.sleep(0.5)

        content = api.page.content()
        json_match = re.search(r'<pre[^>]*>(.*?)</pre>', content, re.DOTALL)

        if json_match:
            data = json.loads(json_match.group(1))

            if data.get('base_resp', {}).get('ret') == 0:
                articles = data.get('app_msg_list', [])

                print(f"\n📝 最近 {len(articles)} 篇文章的时间调试：\n")

                for i, article in enumerate(articles, 1):
                    create_time = article.get('create_time', 0)
                    update_time = article.get('update_time', 0)

                    print(f"{i}. {article['title']}")
                    print(f"   原始 create_time: {create_time}")
                    print(f"   原始 update_time: {update_time}")

                    # 方法1: 直接转换（本地时区）
                    dt1 = datetime.fromtimestamp(create_time)
                    print(f"   转换1 (本地时区): {dt1.strftime('%Y-%m-%d %H:%M:%S')}")

                    # 方法2: UTC时区
                    from datetime import timezone
                    dt2 = datetime.fromtimestamp(create_time, tz=timezone.utc)
                    print(f"   转换2 (UTC): {dt2.strftime('%Y-%m-%d %H:%M:%S %Z')}")

                    # 方法3: 北京时间 (UTC+8)
                    from datetime import timedelta
                    dt3 = datetime.fromtimestamp(create_time, tz=timezone.utc) + timedelta(hours=8)
                    print(f"   转换3 (UTC+8/北京): {dt3.strftime('%Y-%m-%d %H:%M:%S')}")

                    # 当前系统时区
                    import time as time_module
                    print(f"   系统时区偏移: {time_module.timezone / 3600} 小时")

                    print()

    finally:
        api.close()


if __name__ == '__main__':
    main()

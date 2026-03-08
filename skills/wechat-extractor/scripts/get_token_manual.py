#!/usr/bin/env python3
"""手动在浏览器中获取token"""
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

config_file = Path.home() / ".wechat-extractor" / "config.json"

with open(config_file, 'r') as f:
    config = json.load(f)

print("正在打开浏览器，尝试获取token...")
print()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=1000)
    context = browser.new_context()
    context.add_cookies(config['cookies'])

    page = context.new_page()

    # 访问后台首页
    print("1. 访问后台首页...")
    page.goto('https://mp.weixin.qq.com/', wait_until='load')
    time.sleep(3)

    print(f"   URL: {page.url}")

    # 尝试点击任意功能菜单
    print("\n2. 尝试导航到不同页面获取token...")

    pages_to_try = [
        ('https://mp.weixin.qq.com/cgi-bin/home', '首页'),
        ('https://mp.weixin.qq.com/cgi-bin/masssendpage', '群发'),
        ('https://mp.weixin.qq.com/cgi-bin/appmsg', '素材管理'),
        ('https://mp.weixin.qq.com/cgi-bin/message', '消息管理'),
        ('https://mp.weixin.qq.com/cgi-bin/settingpage', '设置'),
    ]

    token = None
    for url, name in pages_to_try:
        print(f"\n  尝试 {name}: {url}")
        try:
            page.goto(url, wait_until='load', timeout=10000)
            time.sleep(2)
            current_url = page.url
            print(f"    实际URL: {current_url}")

            if 'token=' in current_url:
                import re
                match = re.search(r'token=([^&]+)', current_url)
                if match:
                    token = match[1]
                    print(f"    ✅ 找到token: {token[:30]}...")
                    break
        except Exception as e:
            print(f"    ❌ 访问失败: {e}")

    if token:
        print(f"\n\n🎉 成功获取token！")
        print(f"Token: {token}")

        # 保存到配置
        config['token'] = token
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Token已保存到配置文件")
    else:
        print("\n\n❌ 未能获取token")
        print("\n可能原因：")
        print("  1. Cookies已过期，需要重新登录")
        print("  2. 微信后台UI改版，不再在URL中显示token")
        print("  3. 账号权限不足")

    print("\n按Enter关闭浏览器...")
    input()
    browser.close()

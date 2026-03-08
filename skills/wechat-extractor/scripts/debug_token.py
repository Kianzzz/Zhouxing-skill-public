#!/usr/bin/env python3
"""调试token获取问题"""
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

config_file = Path.home() / ".wechat-extractor" / "config.json"

with open(config_file, 'r') as f:
    config = json.load(f)

print(f"📋 加载了 {len(config['cookies'])} 个cookies")
print(f"📋 保存的token: {config.get('token', 'None')}")
print()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # 可见模式
    context = browser.new_context()

    # 加载cookies
    context.add_cookies(config['cookies'])
    print("✅ Cookies已加载")

    page = context.new_page()

    print("\n🔍 测试1: 访问后台首页")
    page.goto('https://mp.weixin.qq.com/cgi-bin/home', wait_until='domcontentloaded')
    time.sleep(3)

    print(f"   当前URL: {page.url}")
    print(f"   页面标题: {page.title()}")

    # 尝试从页面提取token
    try:
        token_from_js = page.evaluate("""
            () => {
                if (window.wx && window.wx.data && window.wx.data.token) {
                    return window.wx.data.token;
                }
                return null;
            }
        """)
        print(f"   window.wx.data.token: {token_from_js}")
    except:
        print("   window.wx.data.token: 无法访问")

    print("\n🔍 测试2: 访问素材管理页面")
    page.goto('https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit&action=edit&type=10&lang=zh_CN',
             wait_until='domcontentloaded')
    time.sleep(3)

    print(f"   当前URL: {page.url}")

    print("\n按Enter查看页面后关闭...")
    input()

    browser.close()

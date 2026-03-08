#!/usr/bin/env python3
"""
在Playwright浏览器上下文中测试搜索API
这样可以确保cookies完全有效
"""
import sys
import json
import re
from pathlib import Path

def test_search_in_browser():
    """在浏览器上下文中测试搜索"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ 未安装 Playwright")
        return False

    config_file = Path.home() / ".wechat-extractor" / "config.json"

    if not config_file.exists():
        print("❌ 未找到登录配置，请先登录")
        return False

    # 加载配置
    with open(config_file, 'r') as f:
        config = json.load(f)

    print("\n🔍 在浏览器上下文中测试搜索API")
    print("="*60)
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        # 恢复cookies
        cookies = config.get('cookies', [])
        context.add_cookies(cookies)
        print(f"✅ 已加载 {len(cookies)} 个cookies")

        page = context.new_page()

        try:
            # 访问后台首页确保session有效
            print("📄 访问后台首页...")

            # 使用 wait_until='load' 确保页面完全加载
            page.goto('https://mp.weixin.qq.com/cgi-bin/home', wait_until='load', timeout=15000)

            import time
            time.sleep(5)  # 等待可能的重定向完成

            # 提取token
            current_url = page.url
            print(f"   当前URL: {current_url}")

            # 安全地获取页面标题
            try:
                page_title = page.title()
                print(f"   页面标题: {page_title}")
            except Exception as e:
                print(f"   ⚠️  无法获取页面标题: {e}")
                page_title = "未知"

            token = None
            if 'token=' in current_url:
                match = re.search(r'token=([^&]+)', current_url)
                if match:
                    token = match.group(1)
                    print(f"✅ 提取到token: {token[:30]}...")
            else:
                print("⚠️  URL中没有token参数")
                print()
                print("   分析：")

                # 检查是否在登录页
                if current_url == 'https://mp.weixin.qq.com/' or current_url == 'https://mp.weixin.qq.com':
                    print("   ❌ 被重定向到登录页 - cookies已过期")
                    print()
                    print("   解决方案：")
                    print("   1. 关闭所有打开的浏览器窗口")
                    print("   2. 运行重新登录: python3 scripts/login_debug.py")
                    print("   3. 登录成功后再次测试")
                elif 'token=' not in current_url and '/cgi-bin/home' in current_url:
                    print("   ⚠️  在后台页面但URL中没有token")
                    print("   这是正常的 - 微信公众号登录后URL不一定包含token")
                    print()
                    print("   尝试从cookies中获取token...")
                    # 尝试从cookies中找token
                    for cookie_name in ['token', 'wxtoken']:
                        try:
                            cookies = page.context.cookies()
                            for c in cookies:
                                if c['name'] == cookie_name:
                                    token = c['value']
                                    print(f"   ✅ 从cookie找到token: {token[:30]}...")
                                    break
                            if token:
                                break
                        except:
                            pass

                print("\n   请查看浏览器窗口，观察当前页面...")
                print("   （浏览器将保持打开30秒）\n")

                # 保持浏览器打开30秒让用户观察
                time.sleep(30)

            if not token:
                print("\n❌ 未能提取token，无法继续测试")
                print("   请重新登录后再试")
                browser.close()
                return False

            # 构建搜索URL
            search_url = f'https://mp.weixin.qq.com/cgi-bin/searchbiz?action=search_biz&query=人民日报&count=3&token={token}&lang=zh_CN&f=json&ajax=1'

            print(f"\n🔍 发送搜索请求...")
            print(f"   查询: 人民日报")

            # 使用浏览器直接访问API
            response = page.goto(search_url, wait_until='domcontentloaded', timeout=10000)

            # 获取响应内容
            content = page.content()

            # 提取JSON（通常在<pre>标签中）
            import re
            json_match = re.search(r'<pre[^>]*>(.*?)</pre>', content, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)
                data = json.loads(json_text)

                print()
                if data.get('base_resp', {}).get('ret') == 0:
                    accounts = data.get('list', [])
                    print(f'✅ 搜索成功！找到 {len(accounts)} 个结果：')
                    print()
                    for i, account in enumerate(accounts, 1):
                        nickname = account.get('nickname', '未知')
                        alias = account.get('alias', '无')
                        print(f'{i}. 公众号: {nickname}')
                        print(f'   微信号: {alias}')
                        print()

                    print("🎉 搜索功能在浏览器上下文中正常工作！")
                    print()
                    print("📝 这说明问题在于：")
                    print("   cookies在requests库中无法正确传递")
                    print("   需要使用浏览器上下文或找到正确的session管理方式")
                else:
                    error_msg = data.get('base_resp', {}).get('err_msg', '未知错误')
                    print(f'❌ 搜索失败: {error_msg}')
                    print(f'   完整响应: {json.dumps(data, indent=2, ensure_ascii=False)}')
            else:
                print("❌ 无法解析响应")
                print(f"   响应内容: {content[:500]}")

            input("\n按Enter键关闭浏览器...")
            browser.close()
            return True

        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            browser.close()
            return False

if __name__ == '__main__':
    test_search_in_browser()

#!/usr/bin/env python3
"""
使用已保存的token在浏览器中测试搜索
"""
import sys
import json
import re
from pathlib import Path

def test_with_saved_token():
    """使用已保存的token测试搜索"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ 未安装 Playwright")
        return False

    config_file = Path.home() / ".wechat-extractor" / "config.json"

    if not config_file.exists():
        print("❌ 未找到登录配置")
        return False

    # 加载配置
    with open(config_file, 'r') as f:
        config = json.load(f)

    token = config.get('token')
    if not token:
        print("❌ 配置中没有token")
        return False

    print("\n🔍 使用已保存的token测试搜索")
    print("="*60)
    print(f"✅ Token: {token}")
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
            # 直接构建搜索URL（使用已保存的token）
            search_url = f'https://mp.weixin.qq.com/cgi-bin/searchbiz?action=search_biz&query=人民日报&count=3&token={token}&lang=zh_CN&f=json&ajax=1'

            print(f"🔍 发送搜索请求...")
            print(f"   查询: 人民日报")
            print(f"   Token: {token}")
            print()

            # 使用浏览器直接访问API
            page.goto(search_url, wait_until='domcontentloaded', timeout=10000)

            import time
            time.sleep(2)

            # 获取响应内容
            content = page.content()

            # 提取JSON（通常在<pre>标签中）
            json_match = re.search(r'<pre[^>]*>(.*?)</pre>', content, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)
                data = json.loads(json_text)

                print("📊 响应结果:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                print()

                if data.get('base_resp', {}).get('ret') == 0:
                    accounts = data.get('list', [])
                    print(f'✅ 搜索成功！找到 {len(accounts)} 个结果：')
                    print()
                    for i, account in enumerate(accounts, 1):
                        nickname = account.get('nickname', '未知')
                        alias = account.get('alias', '无')
                        fakeid = account.get('fakeid', '无')
                        print(f'{i}. 公众号: {nickname}')
                        print(f'   微信号: {alias}')
                        print(f'   fakeid: {fakeid[:30]}...')
                        print()

                    print("🎉 搜索功能在浏览器上下文中正常工作！")
                    print()
                    print("✅ 结论：")
                    print("   - Cookies有效")
                    print("   - Token有效")
                    print("   - 搜索API可以正常调用")
                    print()
                    print("❌ 问题在于：")
                    print("   - requests库无法正确使用这些cookies")
                    print("   - 需要改用Playwright进行所有API调用")
                else:
                    error_ret = data.get('base_resp', {}).get('ret', -1)
                    error_msg = data.get('base_resp', {}).get('err_msg', '未知错误')
                    print(f'❌ 搜索失败:')
                    print(f'   错误码: {error_ret}')
                    print(f'   错误信息: {error_msg}')

                    if error_ret == 200003:
                        print()
                        print("   分析: invalid session")
                        print("   - Token可能已过期")
                        print("   - 需要重新登录获取新token")
            else:
                print("❌ 无法解析响应")
                print(f"   响应内容: {content[:500]}")

            print("\n按Enter键关闭浏览器...")
            input()
            browser.close()
            return True

        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            browser.close()
            return False

if __name__ == '__main__':
    test_with_saved_token()

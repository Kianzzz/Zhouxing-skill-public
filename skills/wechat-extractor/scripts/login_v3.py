#!/usr/bin/env python3
"""
使用Playwright实现微信公众号后台登录 - V3版本
通过页面内容变化检测登录成功（而不是URL变化）
"""
import sys
import os
import json
import time
import re
from pathlib import Path

def login_with_playwright():
    """使用Playwright打开登录页面并等待扫码"""
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    except ImportError:
        print("❌ 未安装 Playwright")
        print("请运行: pip install playwright && playwright install chromium")
        return False

    config_dir = Path.home() / ".wechat-extractor"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "config.json"

    print("\n" + "="*60)
    print("🔐 微信公众号后台登录 V3")
    print("="*60)
    print("\n📱 即将打开浏览器...")
    print("   扫码登录后，页面会自动刷新显示后台")
    print("="*60 + "\n")

    with sync_playwright() as p:
        print("🌐 正在启动浏览器...")
        browser = p.chromium.launch(
            headless=False,
            args=['--window-size=900,1000']
        )

        context = browser.new_context(
            viewport={'width': 900, 'height': 1000},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        page = context.new_page()

        try:
            print("📄 正在打开登录页面...")
            page.goto('https://mp.weixin.qq.com/', wait_until='domcontentloaded', timeout=30000)

            print("\n" + "="*60)
            print("📱 请在浏览器窗口中用微信扫描二维码")
            print("="*60)
            print("步骤：")
            print("  1. 用微信「扫一扫」扫描浏览器中的二维码")
            print("  2. 在手机上选择你的公众号")
            print("  3. 点击「确认登录」")
            print("\n⏳ 等待扫码中（最长5分钟）...")
            print("   脚本会自动检测页面内容变化...\n")

            login_detected = False
            max_wait_time = 300  # 5分钟
            start_time = time.time()
            check_count = 0

            while time.time() - start_time < max_wait_time:
                try:
                    elapsed = int(time.time() - start_time)
                    check_count += 1

                    # 每2秒检查一次
                    if check_count % 2 == 0:
                        # 检测页面内容，判断是否登录成功
                        # 方法1: 检查是否存在二维码（登录前有，登录后消失）
                        qrcode_exists = page.locator('img.qrcode, .login_qrcode, #wx_login_qrcode').count() > 0

                        # 方法2: 检查是否出现后台特征元素
                        # 登录成功后会出现导航菜单、账号信息等
                        backend_elements = page.locator('.menu, .account_info, .weui-desktop-account').count()

                        # 方法3: 检查页面标题
                        page_title = page.title()

                        # 每10秒输出一次状态
                        if check_count % 10 == 0:
                            print(f"[{elapsed}s] 🔍 检测状态:")
                            print(f"       二维码存在: {qrcode_exists}")
                            print(f"       后台元素数: {backend_elements}")
                            print(f"       页面标题: {page_title[:50]}")

                        # 判断登录成功的条件：
                        # 1. 二维码消失 或
                        # 2. 出现后台元素 或
                        # 3. 标题包含"公众号" "后台"等关键词
                        if (not qrcode_exists and backend_elements > 0) or \
                           '公众平台' in page_title or '首页' in page_title:
                            print(f"\n[{elapsed}s] ✅ 检测到登录成功！")
                            print(f"       二维码已消失: {not qrcode_exists}")
                            print(f"       后台元素数量: {backend_elements}")
                            print(f"       页面标题: {page_title}")
                            login_detected = True
                            break

                    # 每秒检查一次
                    time.sleep(1)

                except Exception as e:
                    error_msg = str(e).lower()
                    if "closed" in error_msg or "target" in error_msg:
                        print(f"\n⚠️  检测到浏览器/页面被关闭")
                        break
                    # 其他错误继续重试
                    time.sleep(1)

            if not login_detected:
                elapsed = int(time.time() - start_time)
                print(f"\n[{elapsed}s] ⏰ 未自动检测到登录成功")
                print("   但这不一定意味着登录失败！")
                print("   可能是页面元素检测逻辑需要调整。")
                print()

                # 询问用户
                response = input("   您是否已经在浏览器中看到公众号后台？(y/n): ").strip().lower()
                if response == 'y':
                    print("   ✅ 用户确认已登录成功")
                    login_detected = True
                else:
                    print("   ❌ 用户确认未登录")
                    browser.close()
                    return False

            # 等待页面稳定
            print("\n⏳ 等待页面完全加载...")
            time.sleep(5)

            # 获取页面URL和cookies
            print("\n💾 正在保存登录信息...")
            final_url = page.url
            cookies = context.cookies()

            if len(cookies) == 0:
                print("❌ 未获取到任何 cookies")
                browser.close()
                return False

            print(f"✅ 获取到 {len(cookies)} 个 cookies")
            print(f"   最终URL: {final_url}")

            # 从URL中提取token参数
            token = None
            if 'token=' in final_url:
                match = re.search(r'token=([^&]+)', final_url)
                if match:
                    token = match.group(1)
                    print(f"\n✅ 从URL中提取到 token: {token[:50]}...")

            # 如果URL中没有token，尝试从cookies中找
            if not token:
                print("\n⚠️  URL中未找到token，尝试从cookies中提取...")
                for cookie in cookies:
                    if cookie['name'] in ['token', 'wxtoken']:
                        token = cookie['value']
                        print(f"   ✅ 从cookie中找到 token: {token[:50]}...")
                        break

            # 如果还是没有token，可能需要导航到需要token的页面
            if not token:
                print("\n⚠️  未找到token，尝试访问后台首页获取token...")
                try:
                    # 访问后台首页，URL中会包含token
                    page.goto('https://mp.weixin.qq.com/cgi-bin/home', wait_until='domcontentloaded', timeout=15000)
                    time.sleep(3)
                    final_url = page.url
                    print(f"   访问后台页面: {final_url[:100]}...")

                    if 'token=' in final_url:
                        match = re.search(r'token=([^&]+)', final_url)
                        if match:
                            token = match.group(1)
                            print(f"   ✅ 从后台URL提取到 token: {token[:50]}...")

                    # 更新cookies
                    cookies = context.cookies()
                except Exception as e:
                    print(f"   ⚠️  访问后台页面失败: {e}")

            # 保存配置
            config = {
                'token': token,
                'cookies': cookies,
                'expires_at': time.time() + (90 * 24 * 3600),  # 3个月
                'last_updated': time.time(),
                'login_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                'final_url': final_url
            }

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            print(f"\n✅ 登录信息已保存到：{config_file}")
            print(f"   Token: {'已保存' if token else '未找到（可能影响搜索功能）'}")
            print("✅ 配置有效期约 3 个月，期间无需再次登录")

            print("\n🎉 登录成功！3秒后自动关闭浏览器...")
            time.sleep(3)

            browser.close()
            return True

        except KeyboardInterrupt:
            print("\n\n⚠️  用户取消操作（Ctrl+C）")
            browser.close()
            return False

        except Exception as e:
            print(f"\n❌ 登录过程中出错: {e}")
            import traceback
            traceback.print_exc()
            try:
                browser.close()
            except:
                pass
            return False

def main():
    """主函数"""
    success = login_with_playwright()

    if success:
        print("\n" + "="*60)
        print("✅ 登录完成！")
        print("="*60)
        print("\n测试登录状态：")
        print("  cd scripts && python3 -c \"from wechat_api import WeChatMPAPI; api = WeChatMPAPI(); print('登录状态:', api.is_logged_in())\"")
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("❌ 登录失败")
        print("="*60)
        sys.exit(1)

if __name__ == '__main__':
    main()

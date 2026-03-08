#!/usr/bin/env python3
"""
使用Playwright实现微信公众号后台登录 - 改进版本
使用更灵活的登录检测机制
"""
import sys
import os
import json
import time
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
    print("🔐 微信公众号后台登录")
    print("="*60)
    print("\n📱 即将打开浏览器...")
    print("   请在浏览器中用微信扫描二维码")
    print("   扫码并确认登录后，请稍等几秒")
    print("="*60 + "\n")

    with sync_playwright() as p:
        print("🌐 正在启动浏览器...")
        # 启动浏览器（非无头模式，让用户看到）
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
            print("   登录成功后请稍等，不要关闭浏览器...\n")

            # 记录初始URL
            initial_url = page.url
            login_detected = False

            # 等待URL变化（离开登录页面）
            max_wait_time = 300  # 5分钟
            start_time = time.time()

            while time.time() - start_time < max_wait_time:
                try:
                    current_url = page.url

                    # 检测是否已经离开登录页面
                    # 登录成功后URL会变化，包含token或跳转到后台
                    if current_url != initial_url and 'mp.weixin.qq.com' in current_url:
                        # 检查是否包含登录成功的特征
                        if 'token=' in current_url or '/cgi-bin/' in current_url:
                            print(f"\n✅ 检测到登录成功！")
                            print(f"   当前URL: {current_url[:80]}...")
                            login_detected = True
                            break

                    # 每秒检查一次
                    time.sleep(1)

                except Exception as e:
                    # 如果页面被关闭，退出循环
                    if "closed" in str(e).lower():
                        print(f"\n⚠️  浏览器被关闭")
                        break
                    time.sleep(1)

            if not login_detected:
                print("\n⏰ 未检测到登录成功")
                print("   可能原因：")
                print("   • 超时未扫码")
                print("   • 扫码后未在手机上确认")
                print("   • 浏览器被提前关闭")

                # 即使未检测到URL变化，也尝试保存cookies
                print("\n💾 尝试保存当前会话的 cookies...")
                cookies = context.cookies()
                if len(cookies) > 5:  # 如果有足够多的cookies，可能已经登录
                    print(f"   发现 {len(cookies)} 个 cookies，可能已经登录")
                else:
                    browser.close()
                    return False

            # 等待页面稳定
            print("⏳ 等待页面完全加载...")
            time.sleep(5)

            # 获取并保存cookies
            print("\n💾 正在保存登录信息...")
            cookies = context.cookies()

            if len(cookies) == 0:
                print("❌ 未获取到任何 cookies")
                browser.close()
                return False

            print(f"✅ 获取到 {len(cookies)} 个 cookies")

            # 提取token
            token = None
            for cookie in cookies:
                if cookie['name'] in ['token', 'wxtoken', 'data_ticket']:
                    token = cookie['value']
                    print(f"✅ 找到 token: {cookie['name']}")
                    break

            # 保存配置
            config = {
                'token': token,
                'cookies': cookies,
                'expires_at': time.time() + (90 * 24 * 3600),  # 3个月
                'last_updated': time.time(),
                'login_time': time.strftime('%Y-%m-%d %H:%M:%S')
            }

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            print(f"✅ 登录信息已保存到：{config_file}")
            print("✅ 配置有效期约 3 个月，期间无需再次登录")

            print("\n🎉 登录成功！3秒后自动关闭浏览器...")
            time.sleep(3)

            browser.close()
            return True

        except KeyboardInterrupt:
            print("\n\n⚠️  用户取消操作")
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
        print("\n现在您可以使用账号搜索功能了。")
        print("\n测试登录状态：")
        print("  python3 -c \"from scripts.wechat_api import WeChatMPAPI; api = WeChatMPAPI(); print('登录状态:', api.is_logged_in())\"")
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("❌ 登录失败")
        print("="*60)
        print("\n可能的原因：")
        print("  • 超时未扫码（需在5分钟内完成）")
        print("  • 扫码后未在手机上点击确认")
        print("  • 浏览器被提前关闭")
        print("  • 网络连接问题")
        print("\n💡 提示：")
        print("  • 确保在手机上点击「确认登录」后等待几秒")
        print("  • 不要在登录完成前关闭浏览器")
        print("  • 保持网络连接稳定")
        print("\n请重新运行此脚本重试。")
        sys.exit(1)

if __name__ == '__main__':
    main()

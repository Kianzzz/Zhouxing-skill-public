#!/usr/bin/env python3
"""
使用Playwright实现微信公众号后台登录 - 智能快速检测版本
通过监测cookies数量和token自动判断登录成功，无需等待超时
"""
import sys
import os
import json
import time
import re
import signal
from pathlib import Path

# 全局引用，用于信号处理时清理浏览器
_browser_ref = None

def _cleanup_on_signal(signum, frame):
    """进程被终止时关闭浏览器"""
    global _browser_ref
    if _browser_ref:
        try:
            _browser_ref.close()
            print("\n⚠️ 收到终止信号，浏览器已关闭")
        except Exception:
            pass
    sys.exit(1)

signal.signal(signal.SIGTERM, _cleanup_on_signal)
signal.signal(signal.SIGINT, _cleanup_on_signal)

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
    print("🔐 微信公众号后台登录（智能快速检测）")
    print("="*60)
    print("\n📱 即将打开浏览器...")
    print("   扫码登录后会自动检测并立即完成")
    print("="*60 + "\n")

    with sync_playwright() as p:
        global _browser_ref
        print("🌐 正在启动浏览器...")
        browser = p.chromium.launch(
            headless=False,
            args=['--window-size=900,1000']
        )
        _browser_ref = browser  # 保存全局引用，供信号处理清理

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
            print("\n⏳ 智能检测中...")
            print("   登录成功后会自动识别并完成\n")

            # 记录初始cookies数量
            initial_cookies = len(context.cookies())
            print(f"[0s] 初始cookies: {initial_cookies} 个")

            login_detected = False
            token = None  # 在循环前初始化，避免后续引用未定义变量
            max_wait_time = 300  # 最长5分钟
            start_time = time.time()
            last_cookie_count = initial_cookies

            while time.time() - start_time < max_wait_time:
                try:
                    elapsed = int(time.time() - start_time)

                    # 每秒检测一次cookies变化
                    current_cookies = context.cookies()
                    cookie_count = len(current_cookies)

                    # 如果cookies数量显著增加，说明可能已登录
                    if cookie_count != last_cookie_count:
                        print(f"[{elapsed}s] 🔄 Cookies变化: {last_cookie_count} → {cookie_count}")
                        last_cookie_count = cookie_count

                    # 智能检测：如果cookies超过10个，很可能已经登录成功
                    if cookie_count >= 10:
                        print(f"\n[{elapsed}s] ✅ 检测到足够的cookies ({cookie_count}个)")
                        print(f"[{elapsed}s] 🔍 尝试访问后台提取token...")

                        # 等待一下让页面稳定
                        time.sleep(2)

                        try:
                            # 尝试访问后台首页
                            page.goto('https://mp.weixin.qq.com/cgi-bin/home',
                                     wait_until='domcontentloaded', timeout=10000)

                            # 立即捕获URL（不要等待，避免JS跳转导致token消失）
                            current_url = page.url
                            token = None

                            if 'token=' in current_url:
                                match = re.search(r'token=([^&]+)', current_url)
                                if match:
                                    token = match.group(1)
                                    print(f"[{elapsed}s] ✅ 从URL提取到token: {token[:20]}...")
                                    login_detected = True
                                    break

                            # 如果访问成功但URL没有token，也认为登录成功
                            if '/cgi-bin/home' in current_url:
                                print(f"[{elapsed}s] ✅ 成功访问后台页面")
                                # 尝试从页面提取token
                                try:
                                    # 执行JavaScript获取页面中的token
                                    token_from_page = page.evaluate("""
                                        () => {
                                            // 尝试多种方式提取token
                                            const url = window.location.href;
                                            const match = url.match(/token=([^&]+)/);
                                            if (match) return match[1];

                                            // 尝试从window对象中找
                                            if (window.wx && window.wx.data && window.wx.data.token) {
                                                return window.wx.data.token;
                                            }

                                            return null;
                                        }
                                    """)

                                    if token_from_page:
                                        token = token_from_page
                                        print(f"[{elapsed}s] ✅ 从页面提取到token: {token[:20]}...")

                                except Exception as e:
                                    print(f"[{elapsed}s] ⚠️  从页面提取token失败: {e}")

                                login_detected = True
                                break

                        except Exception as e:
                            print(f"[{elapsed}s] ⚠️  访问后台失败，继续等待: {e}")
                            # 返回登录页继续等待
                            page.goto('https://mp.weixin.qq.com/', wait_until='domcontentloaded')

                    # 每10秒输出一次等待状态
                    if elapsed % 10 == 0 and elapsed > 0:
                        print(f"[{elapsed}s] ⏳ 等待中... (当前{cookie_count}个cookies)")

                    time.sleep(1)

                except Exception as e:
                    error_msg = str(e).lower()
                    if "closed" in error_msg or "target" in error_msg:
                        print(f"\n⚠️  检测到浏览器被关闭")
                        break
                    time.sleep(1)

            if not login_detected:
                elapsed = int(time.time() - start_time)
                print(f"\n[{elapsed}s] ⏰ 未自动检测到登录成功")

                # 最后尝试：检查cookies
                final_cookies = context.cookies()
                if len(final_cookies) >= 10:
                    print(f"   但发现 {len(final_cookies)} 个cookies，可能已登录")
                    print("   尝试保存...")
                    login_detected = True
                else:
                    print(f"   只有 {len(final_cookies)} 个cookies，可能未登录")
                    browser.close()
                    return False

            # 等待页面稳定，确保所有cookies已通过Set-Cookie响应设置
            print("\n⏳ 等待页面稳定...")
            try:
                page.wait_for_load_state('networkidle', timeout=15000)
            except Exception:
                pass  # networkidle 超时没关系
            time.sleep(2)

            # 获取最终的cookies和token
            print("\n💾 正在保存登录信息...")
            cookies = context.cookies()

            if len(cookies) == 0:
                print("❌ 未获取到任何 cookies")
                browser.close()
                return False

            print(f"✅ 获取到 {len(cookies)} 个 cookies")

            # 最后一次尝试提取token（仅在之前未获取到时）
            final_url = page.url

            if token is None:
                if 'token=' in final_url:
                    match = re.search(r'token=([^&]+)', final_url)
                    if match:
                        token = match.group(1)
                        print(f"✅ Token: {token[:30]}...")
            else:
                print(f"✅ 使用检测阶段获取的Token: {str(token)[:30]}...")

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
            print("✅ 配置有效期约 3 个月，期间无需再次登录")

            elapsed_total = int(time.time() - start_time)
            print(f"\n🎉 登录成功！总耗时 {elapsed_total} 秒")
            print("   3秒后自动关闭浏览器...")
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
        print("\n现在您可以使用账号搜索功能了。")
        print("\n测试搜索功能：")
        print("  python3 scripts/wechat_api_browser.py")
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("❌ 登录失败")
        print("="*60)
        print("\n请重新运行此脚本重试。")
        sys.exit(1)

if __name__ == '__main__':
    main()

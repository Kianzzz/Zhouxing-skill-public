#!/usr/bin/env python3
"""
使用Playwright实现微信公众号后台登录 - 调试版本
实时显示URL变化，帮助诊断问题
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
    print("🔐 微信公众号后台登录（调试版本）")
    print("="*60)
    print("\n📱 即将打开浏览器...")
    print("   请在浏览器中用微信扫描二维码")
    print("   扫码并确认登录后，请稍等几秒")
    print("   这个版本会实时显示URL变化")
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
            print("   登录成功后请稍等，不要关闭浏览器...")
            print("   🔍 实时URL监控中...\n")

            # 记录初始URL
            initial_url = page.url
            print(f"[0s] 初始URL: {initial_url}")

            login_detected = False
            last_url = initial_url
            check_count = 0

            # 等待URL变化（离开登录页面）
            max_wait_time = 300  # 5分钟
            start_time = time.time()

            while time.time() - start_time < max_wait_time:
                try:
                    current_url = page.url
                    elapsed = int(time.time() - start_time)
                    check_count += 1

                    # 如果URL变化了，打印出来
                    if current_url != last_url:
                        print(f"[{elapsed}s] 🔄 URL变化!")
                        print(f"       旧: {last_url[:100]}")
                        print(f"       新: {current_url[:100]}")
                        last_url = current_url

                    # 每10次检查输出一次状态（每10秒）
                    if check_count % 10 == 0:
                        print(f"[{elapsed}s] ⏳ 仍在等待... (当前URL未变化)")

                    # 检测是否已经离开登录页面
                    if current_url != initial_url:
                        print(f"\n[{elapsed}s] ✅ 检测到URL已离开登录页面！")
                        print(f"       当前URL: {current_url}")

                        # 检查URL特征
                        if 'token=' in current_url:
                            print("       ✓ URL包含 token 参数")
                        if '/cgi-bin/' in current_url:
                            print("       ✓ URL包含 /cgi-bin/ 路径")
                        if 'mp.weixin.qq.com' in current_url:
                            print("       ✓ URL属于微信公众号域名")

                        login_detected = True
                        break

                    # 每秒检查一次
                    time.sleep(1)

                except Exception as e:
                    error_msg = str(e).lower()
                    # 如果页面被关闭，退出循环
                    if "closed" in error_msg or "target" in error_msg:
                        print(f"\n⚠️  检测到浏览器/页面被关闭")
                        print(f"    错误: {e}")
                        break
                    print(f"⚠️  检测URL时出错: {e}")
                    time.sleep(1)

            if not login_detected:
                elapsed = int(time.time() - start_time)
                print(f"\n[{elapsed}s] ⏰ 未检测到登录成功")
                print("   可能原因：")
                print("   • 超时未扫码")
                print("   • 扫码后未在手机上确认")
                print("   • URL没有发生预期的变化")
                print("   • 浏览器被关闭")

                # 即使未检测到URL变化，也尝试保存cookies
                print("\n💾 尝试保存当前会话的 cookies...")
                try:
                    cookies = context.cookies()
                    print(f"   当前有 {len(cookies)} 个 cookies")

                    if len(cookies) > 5:  # 如果有足够多的cookies，可能已经登录
                        print(f"   ✓ 发现足够多的cookies，可能已经登录成功")
                        # 继续保存流程
                    else:
                        print(f"   ✗ cookies数量太少，可能未登录")
                        browser.close()
                        return False
                except Exception as e:
                    print(f"   ✗ 获取cookies失败: {e}")
                    browser.close()
                    return False

            # 等待页面稳定
            print("\n⏳ 等待页面完全加载...")
            time.sleep(5)

            # 获取并保存cookies
            print("\n💾 正在保存登录信息...")
            cookies = context.cookies()

            if len(cookies) == 0:
                print("❌ 未获取到任何 cookies")
                browser.close()
                return False

            print(f"✅ 获取到 {len(cookies)} 个 cookies")

            # 打印部分cookie信息用于调试
            print("\n📋 Cookies 列表（前5个）：")
            for i, cookie in enumerate(cookies[:5]):
                print(f"   {i+1}. {cookie['name']} = {cookie['value'][:20]}...")

            # 提取token（从URL参数中提取，不是从cookies）
            token = None
            final_url = page.url

            # 从URL中提取token参数
            if 'token=' in final_url:
                import re
                match = re.search(r'token=([^&]+)', final_url)
                if match:
                    token = match.group(1)
                    print(f"\n✅ 从URL中提取到 token: {token[:30]}...")

            # 如果URL中没有token，尝试从cookies中找
            if not token:
                print("\n⚠️  URL中未找到token，尝试从cookies中提取...")
                for cookie in cookies:
                    if cookie['name'] in ['token', 'wxtoken', 'data_ticket', 'data_bizuin', 'bizuin']:
                        token = cookie['value']
                        print(f"   找到 cookie token: {cookie['name']} = {token[:30]}...")
                        break

            # 保存配置
            config = {
                'token': token,
                'cookies': cookies,
                'expires_at': time.time() + (90 * 24 * 3600),  # 3个月
                'last_updated': time.time(),
                'login_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                'final_url': page.url  # 保存最终URL用于调试
            }

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            print(f"\n✅ 登录信息已保存到：{config_file}")
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
        print("\n现在您可以使用账号搜索功能了。")
        print("\n测试登录状态：")
        print("  cd scripts && python3 -c \"from wechat_api import WeChatMPAPI; api = WeChatMPAPI(); print('登录状态:', api.is_logged_in())\"")
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("❌ 登录失败")
        print("="*60)
        print("\n💡 如果您看到了cookies被保存但仍显示失败，")
        print("   请检查 ~/.wechat-extractor/config.json")
        print("   可能实际上已经登录成功了。")
        print("\n请重新运行此脚本重试。")
        sys.exit(1)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
使用Playwright实现微信公众号后台登录
解决直接API调用被拒绝的问题
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
    print("🔐 微信公众号后台登录（Playwright版本）")
    print("="*60)
    print("\n这个脚本将：")
    print("1. 打开微信公众号登录页面")
    print("2. 显示二维码供您扫描")
    print("3. 扫码成功后自动保存登录信息")
    print("4. 关闭浏览器")
    print("\n准备就绪？按 Enter 继续...")
    input()

    with sync_playwright() as p:
        print("\n🌐 正在启动浏览器...")
        # 启动浏览器（非无头模式，让用户看到）
        browser = p.chromium.launch(
            headless=False,
            args=['--window-size=800,900']
        )

        context = browser.new_context(
            viewport={'width': 800, 'height': 900},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        page = context.new_page()

        try:
            print("📄 正在打开登录页面...")
            page.goto('https://mp.weixin.qq.com/', wait_until='networkidle', timeout=30000)

            print("\n" + "="*60)
            print("📱 请在浏览器窗口中用微信扫描二维码")
            print("="*60)
            print("提示：")
            print("  1. 用微信「扫一扫」扫描浏览器中的二维码")
            print("  2. 在手机上选择你的公众号")
            print("  3. 点击「确认登录」")
            print("  4. 登录成功后，脚本会自动继续...")
            print("="*60)
            print("\n⏳ 等待扫码中（最长5分钟）...\n")

            # 等待登录成功（检测URL变化或特定元素）
            try:
                # 等待跳转到后台首页（URL包含/cgi-bin/home）
                page.wait_for_url('**/cgi-bin/home**', timeout=300000)  # 5分钟超时
                print("✅ 检测到登录成功！")

                # 等待页面完全加载，确保所有cookies已通过Set-Cookie响应设置
                try:
                    page.wait_for_load_state('networkidle', timeout=15000)
                except PlaywrightTimeout:
                    pass  # networkidle 超时没关系，cookies 大概率已经设置好了
                time.sleep(2)

            except PlaywrightTimeout:
                print("\n⏰ 等待超时（5分钟），请重新运行脚本")
                browser.close()
                return False

            # 获取并保存cookies
            print("\n💾 正在保存登录信息...")
            cookies = context.cookies()
            print(f"✅ 获取到 {len(cookies)} 个 cookies")

            # 提取token（从URL获取，不是从cookies！）
            token = None
            current_url = page.url
            if 'token=' in current_url:
                match = re.search(r'token=([^&]+)', current_url)
                if match:
                    token = match.group(1)
                    print(f"✅ 从URL提取到token: {token}")

            # 备用：从页面JS提取
            if not token:
                try:
                    token = page.evaluate("""
                        () => {
                            const url = window.location.href;
                            const match = url.match(/token=([^&]+)/);
                            if (match) return match[1];
                            if (window.wx && window.wx.data && window.wx.data.token) {
                                return window.wx.data.token;
                            }
                            return null;
                        }
                    """)
                    if token:
                        print(f"✅ 从页面JS提取到token: {token}")
                except Exception:
                    pass

            if not token:
                print("⚠️ 未能提取到token，登录可能不完整")

            # 保存配置
            config = {
                'token': token,
                'cookies': cookies,
                'expires_at': time.time() + (90 * 24 * 3600),  # 3个月
                'last_updated': time.time(),
                'login_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                'final_url': current_url
            }

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            print(f"✅ 登录信息已保存到：{config_file}")
            print("✅ 配置有效期约 3 个月，期间无需再次登录")

            print("\n🎉 登录成功！3秒后自动关闭浏览器...")
            time.sleep(3)

            browser.close()
            return True

        except Exception as e:
            print(f"\n❌ 登录过程中出错: {e}")
            import traceback
            traceback.print_exc()
            browser.close()
            return False

def main():
    """主函数"""
    success = login_with_playwright()

    if success:
        print("\n" + "="*60)
        print("✅ 登录完成！")
        print("="*60)
        print("\n现在您可以使用账号搜索功能了。")
        print("\n例如，在 Python 中：")
        print("  from wechat_api import WeChatMPAPI")
        print("  api = WeChatMPAPI()")
        print("  results = api.search_account('测试公众号')")
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("❌ 登录失败")
        print("="*60)
        print("\n可能的原因：")
        print("  • 超时未扫码")
        print("  • 扫码后未确认")
        print("  • 网络连接问题")
        print("  • Playwright未正确安装")
        print("\n请重新运行此脚本重试。")
        sys.exit(1)

if __name__ == '__main__':
    main()

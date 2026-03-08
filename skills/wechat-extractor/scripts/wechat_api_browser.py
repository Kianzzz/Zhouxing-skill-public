#!/usr/bin/env python3
"""
微信公众号API - Playwright版本
使用浏览器上下文执行所有API调用，避免session问题
"""
import json
import time
import re
from pathlib import Path


class WeChatMPAPIBrowser:
    """基于Playwright的微信公众号API客户端"""

    def __init__(self, config_dir=None):
        """初始化API客户端"""
        if config_dir is None:
            config_dir = Path.home() / ".wechat-extractor"

        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "config.json"
        self.cache_dir = self.config_dir / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.config = self.load_config()
        self.browser = None
        self.context = None
        self.page = None

    def load_config(self):
        """加载本地配置"""
        if not self.config_file.exists():
            return None

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 检查是否过期
            if 'expires_at' in config:
                if time.time() > config['expires_at']:
                    print("⚠️ 配置已过期，需要重新登录")
                    return None

            return config
        except Exception as e:
            print(f"加载配置失败: {e}")
            return None

    def is_logged_in(self):
        """检查是否已登录"""
        return self.config is not None and 'cookies' in self.config

    def _ensure_browser(self):
        """确保浏览器已启动"""
        if self.browser is not None:
            return

        try:
            from playwright.sync_api import sync_playwright
            self._playwright = sync_playwright().start()
            self.browser = self._playwright.chromium.launch(headless=True)
            self.context = self.browser.new_context()

            # 加载cookies
            if self.config and 'cookies' in self.config:
                self.context.add_cookies(self.config['cookies'])

            self.page = self.context.new_page()
            print("✅ 浏览器已启动（无头模式）")

        except Exception as e:
            print(f"❌ 启动浏览器失败: {e}")
            raise

    def _get_token(self):
        """获取有效的token"""
        # 先尝试使用保存的token
        saved_token = self.config.get('token')

        # 访问后台首页获取新token
        try:
            self._ensure_browser()

            # 尝试1: 访问首页触发重定向，从URL提取token
            # 关键：访问根路径会自动重定向到带token的完整URL
            self.page.goto('https://mp.weixin.qq.com/',
                          wait_until='load', timeout=15000)

            # 立即捕获URL（不要等待，避免JS跳转导致token消失）
            current_url = self.page.url
            token = None

            if 'token=' in current_url:
                match = re.search(r'token=([^&]+)', current_url)
                if match:
                    token = match.group(1)
                    print(f"✅ 从URL获取到token: {token[:20]}...")

            # 尝试2: 从页面JavaScript中提取token
            if not token:
                try:
                    token = self.page.evaluate("""
                        () => {
                            // 方法1: 从URL提取
                            const url = window.location.href;
                            let match = url.match(/token=([^&]+)/);
                            if (match) return match[1];

                            // 方法2: 从wx.data对象
                            if (window.wx && window.wx.data && window.wx.data.token) {
                                return window.wx.data.token;
                            }

                            // 方法3: 从localStorage
                            try {
                                const stored = localStorage.getItem('token');
                                if (stored) return stored;
                            } catch(e) {}

                            // 方法4: 从cookies
                            try {
                                const cookies = document.cookie;
                                match = cookies.match(/token=([^;]+)/);
                                if (match) return match[1];
                            } catch(e) {}

                            return null;
                        }
                    """)
                    if token:
                        print(f"✅ 从页面JS获取到token: {token[:20]}...")
                except Exception as e:
                    print(f"⚠️  从页面提取token失败: {e}")

            # 尝试3: 访问搜索页面触发token生成
            if not token:
                try:
                    print("⚠️  尝试访问搜索页面获取token...")
                    self.page.goto('https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit&action=edit&type=10&token=&lang=zh_CN',
                                  wait_until='domcontentloaded', timeout=10000)
                    time.sleep(2)
                    current_url = self.page.url
                    if 'token=' in current_url:
                        match = re.search(r'token=([^&]+)', current_url)
                        if match:
                            token = match.group(1)
                            print(f"✅ 从搜索页面获取到token: {token[:20]}...")
                except Exception as e:
                    print(f"⚠️  访问搜索页面失败: {e}")

            # 保存新token
            if token:
                self.config['token'] = token
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
                return token

            # 如果都失败了，使用保存的token
            if saved_token:
                print(f"⚠️  使用保存的token: {saved_token[:20]}...")
                return saved_token

            print("❌ 无法获取token")
            return None

        except Exception as e:
            print(f"❌ 获取token失败: {e}")
            if saved_token:
                print(f"   使用保存的token")
                return saved_token
            return None

    def search_account(self, query, count=10):
        """搜索公众号"""
        if not self.is_logged_in():
            print("❌ 未登录，请先登录")
            return []

        try:
            self._ensure_browser()

            # 先访问首页触发重定向并建立session
            # 关键：访问根路径会自动重定向到带token的完整URL
            print("🔍 正在建立session...")
            self.page.goto('https://mp.weixin.qq.com/',
                          wait_until='load', timeout=15000)

            # 立即捕获URL中的token（不要等待，避免JS跳转导致token消失）
            current_url = self.page.url
            token = None
            if 'token=' in current_url:
                match = re.search(r'token=([^&]+)', current_url)
                if match:
                    token = match.group(1)
                    print(f"✅ 获取到token: {token[:20]}...")
                    # 保存token到配置
                    self.config['token'] = token
                    with open(self.config_file, 'w', encoding='utf-8') as f:
                        json.dump(self.config, f, indent=2, ensure_ascii=False)

            # 方法2: 如果URL没有token，通过导航到搜索页面获取
            if not token:
                print("⚠️  URL中没有token，尝试通过导航获取...")
                # 点击左侧菜单的"新建群发"触发导航
                try:
                    # 直接访问消息管理页面，这个页面的URL通常包含token
                    self.page.goto('https://mp.weixin.qq.com/cgi-bin/message?t=message/list&count=20&day=7',
                                  wait_until='domcontentloaded', timeout=10000)
                    time.sleep(2)
                    current_url = self.page.url
                    if 'token=' in current_url:
                        match = re.search(r'token=([^&]+)', current_url)
                        if match:
                            token = match.group(1)
                            print(f"✅ 从消息页获取到token: {token[:20]}...")
                except Exception as e:
                    print(f"⚠️  导航失败: {e}")

            # 方法3: 使用空token尝试（有些接口cookies就够了）
            if not token:
                print("⚠️  无token，尝试仅用cookies调用API...")
                token = ""  # 空token

            # 构建搜索URL
            url = f'https://mp.weixin.qq.com/cgi-bin/searchbiz?action=search_biz&query={query}&count={count}&token={token}&lang=zh_CN&f=json&ajax=1'

            print(f"🔍 搜索公众号: {query}")
            self.page.goto(url, wait_until='domcontentloaded', timeout=10000)
            time.sleep(1)

            # 获取响应
            content = self.page.content()
            json_match = re.search(r'<pre[^>]*>(.*?)</pre>', content, re.DOTALL)

            if json_match:
                data = json.loads(json_match.group(1))

                if data.get('base_resp', {}).get('ret') == 0:
                    accounts = data.get('list', [])
                    print(f"✅ 找到 {len(accounts)} 个公众号")
                    return accounts
                else:
                    error_msg = data.get('base_resp', {}).get('err_msg', '未知错误')
                    error_ret = data.get('base_resp', {}).get('ret', -1)
                    print(f"❌ 搜索失败 (ret={error_ret}): {error_msg}")
                    return []
            else:
                print("❌ 无法解析响应")
                print(f"   响应内容: {content[:500]}")
                return []

        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            import traceback
            traceback.print_exc()
            return []

    def close(self):
        """关闭浏览器"""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if hasattr(self, '_playwright'):
            self._playwright.stop()
        print("✅ 浏览器已关闭")

    def __del__(self):
        """析构函数"""
        try:
            self.close()
        except:
            pass


# 测试代码
if __name__ == '__main__':
    api = WeChatMPAPIBrowser()

    if not api.is_logged_in():
        print("❌ 未登录，请先运行登录脚本")
        exit(1)

    try:
        results = api.search_account('人民日报', count=3)

        if results:
            print("\n📋 搜索结果：")
            for i, account in enumerate(results, 1):
                print(f"{i}. {account.get('nickname', '未知')}")
                print(f"   微信号: {account.get('alias', '无')}")
                print()
        else:
            print("\n❌ 搜索失败或无结果")

    finally:
        api.close()

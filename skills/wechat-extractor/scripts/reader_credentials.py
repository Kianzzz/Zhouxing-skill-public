#!/usr/bin/env python3
"""
读者凭证管理器
管理 appmsg_token 和 Cookie（读者端凭证）
用于获取阅读数据和评论
"""
import json
import time
from pathlib import Path


class ReaderCredentials:
    """读者凭证管理（appmsg_token + Cookie）"""

    def __init__(self, config_dir=None):
        if config_dir is None:
            config_dir = Path.home() / ".wechat-extractor"
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.cred_file = self.config_dir / "reader_credentials.json"

    def load(self):
        """加载已保存的凭证

        Returns:
            dict: {'key': ..., 'appmsg_token': ..., 'cookie': ..., ...}
            None: 无凭证或已过期
        """
        if not self.cred_file.exists():
            return None

        try:
            with open(self.cred_file, 'r', encoding='utf-8') as f:
                cred = json.load(f)

            # 检查必要字段：key 是最关键的（比 appmsg_token 更重要）
            if not cred.get('key') and not cred.get('appmsg_token'):
                if not cred.get('cookie'):
                    return None

            # 检查过期
            saved_at = cred.get('saved_at', 0)
            # 支持新格式（max_age_minutes）和旧格式（max_age_hours）
            if 'max_age_minutes' in cred:
                max_age = cred['max_age_minutes'] * 60
                age_desc = f"{cred['max_age_minutes']} 分钟"
            else:
                max_age = cred.get('max_age_hours', 2) * 3600
                age_desc = f"{cred.get('max_age_hours', 2)} 小时"

            if time.time() - saved_at > max_age:
                age_min = int((time.time() - saved_at) / 60)
                print(f"⚠️ 读者凭证已过期（{age_min} 分钟前保存，有效期 {age_desc}）")
                return None

            return cred
        except Exception as e:
            print(f"⚠️ 加载读者凭证失败: {e}")
            return None

    def save(self, appmsg_token, cookie, max_age_hours=2, **extra):
        """保存读者凭证

        Args:
            appmsg_token: 从抓包获取的 appmsg_token
            cookie: 从抓包获取的完整 Cookie 字符串
            max_age_hours: 有效期（小时），默认 2 小时
            **extra: 额外字段（key, uin, pass_ticket, wap_sid2 等）
        """
        cred = {
            'appmsg_token': appmsg_token,
            'cookie': cookie,
            'saved_at': time.time(),
            'saved_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'max_age_hours': max_age_hours
        }
        # 合并额外字段
        for k, v in extra.items():
            if v:  # 只保存非空值
                cred[k] = v

        with open(self.cred_file, 'w', encoding='utf-8') as f:
            json.dump(cred, f, indent=2, ensure_ascii=False)

        print(f"✅ 读者凭证已保存（有效期 {max_age_hours} 小时）")

    def validate(self, credentials=None):
        """验证凭证是否有效（通过实际 API 调用测试）

        Args:
            credentials: 要验证的凭证，None 则使用已保存的

        Returns:
            bool: 凭证是否有效
        """
        if credentials is None:
            credentials = self.load()

        if not credentials:
            return False

        try:
            import requests

            # 用一个已知的公众号文章测试（人民日报的一篇老文章）
            test_url = "https://mp.weixin.qq.com/mp/getappmsgext"
            headers = {
                'User-Agent': (
                    'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 '
                    'Chrome/57.0.2987.132 MQQBrowser/6.2 TBS/044304 '
                    'MicroMessenger/8.0.44.2502(0x28002C35) NetType/WIFI'
                ),
                'Cookie': credentials['cookie']
            }
            params = {'appmsg_token': credentials['appmsg_token'], 'x5': '0'}
            # 只发一个最小请求，看返回码
            data = {'is_only_read': '1'}

            resp = requests.post(test_url, params=params, data=data,
                                 headers=headers, timeout=10)
            result = resp.json()

            ret = result.get('base_resp', {}).get('ret', -1)
            if ret == 302:
                print("❌ 读者凭证已过期（ret=302）")
                return False
            # ret=0 或其他非 302 值都算凭证本身有效（可能文章参数不全导致其他错误）
            return True

        except Exception as e:
            print(f"⚠️ 验证凭证失败: {e}")
            return False

    def is_available(self):
        """检查是否有可用的凭证（未过期）"""
        return self.load() is not None

    def get_age_info(self):
        """获取凭证的时间信息

        Returns:
            str: 描述性文字，如 "保存于 35 分钟前，剩余 85 分钟"
            None: 无凭证
        """
        if not self.cred_file.exists():
            return None

        try:
            with open(self.cred_file, 'r', encoding='utf-8') as f:
                cred = json.load(f)

            saved_at = cred.get('saved_at', 0)
            # 支持新格式（max_age_minutes）和旧格式（max_age_hours）
            if 'max_age_minutes' in cred:
                max_age = cred['max_age_minutes'] * 60
            else:
                max_age = cred.get('max_age_hours', 2) * 3600
            elapsed = time.time() - saved_at
            remaining = max_age - elapsed

            elapsed_min = int(elapsed / 60)

            if remaining <= 0:
                return f"已过期（{elapsed_min} 分钟前保存）"
            else:
                remaining_min = int(remaining / 60)
                return f"保存于 {elapsed_min} 分钟前，剩余 {remaining_min} 分钟"

        except Exception:
            return None

    def is_valid_for_biz(self, target_biz):
        """检查凭证是否有效且匹配目标公众号的 __biz

        读者凭证（key）是 session 绑定的，跨公众号请求会 302 captcha。
        此方法检查：1) 凭证未过期 2) __biz 匹配目标公众号

        Args:
            target_biz: 目标公众号的 __biz 值

        Returns:
            dict: {
                'valid': True/False,
                'reason': '...',  # 无效原因
                'credentials': {...}  # 有效时返回凭证
            }
        """
        cred = self.load()
        if cred is None:
            return {
                'valid': False,
                'reason': 'no_credentials',
                'credentials': None
            }

        # 检查 __biz 是否匹配
        saved_biz = cred.get('__biz', '')
        if not saved_biz:
            # 旧格式凭证没有 __biz 字段，无法判断
            return {
                'valid': False,
                'reason': 'no_biz_in_credentials',
                'credentials': cred
            }

        if saved_biz != target_biz:
            return {
                'valid': False,
                'reason': f'biz_mismatch (saved: {saved_biz[:8]}..., target: {target_biz[:8]}...)',
                'credentials': cred
            }

        return {
            'valid': True,
            'reason': 'ok',
            'credentials': cred
        }

    def clear(self):
        """清除已保存的凭证"""
        if self.cred_file.exists():
            self.cred_file.unlink()
            print("✅ 读者凭证已清除")

    def save_from_mitmproxy(self, intercepted_data):
        """从 mitmproxy 截获的数据保存凭证

        Args:
            intercepted_data: dict with 'appmsg_token' and 'cookie'
        """
        self.save(
            appmsg_token=intercepted_data['appmsg_token'],
            cookie=intercepted_data['cookie']
        )

    def prompt_manual_input(self):
        """交互式手动输入凭证（用于无法使用 mitmproxy 时的备选方案）

        Returns:
            dict: 凭证 or None
        """
        print("\n" + "=" * 60)
        print("📋 手动输入读者凭证")
        print("=" * 60)
        print("\n获取方法：")
        print("  1. 在电脑端微信打开任意公众号文章")
        print("  2. 右键 → 在浏览器中打开")
        print("  3. 按 F12 打开开发者工具 → Network 标签")
        print("  4. 刷新页面，找到 'getappmsgext' 请求")
        print("  5. 复制 URL 中的 appmsg_token 参数值")
        print("  6. 复制 Request Headers 中的 Cookie 值")
        print("=" * 60)

        try:
            appmsg_token = input("\nappmsg_token: ").strip()
            if not appmsg_token:
                print("❌ appmsg_token 不能为空")
                return None

            cookie = input("Cookie: ").strip()
            if not cookie:
                print("❌ Cookie 不能为空")
                return None

            self.save(appmsg_token, cookie)
            return self.load()

        except (KeyboardInterrupt, EOFError):
            print("\n取消输入")
            return None


if __name__ == '__main__':
    mgr = ReaderCredentials()

    cred = mgr.load()
    if cred:
        age = mgr.get_age_info()
        print(f"✅ 已有读者凭证（{age}）")
        print(f"   appmsg_token: {cred['appmsg_token'][:30]}...")
    else:
        print("❌ 无有效的读者凭证")
        print("\n可以通过以下方式获取：")
        print("  1. 运行 capture_credentials.py（自动抓包）")
        print("  2. 手动输入（运行此脚本加 --manual 参数）")

        import sys
        if len(sys.argv) > 1 and sys.argv[1] == '--manual':
            mgr.prompt_manual_input()

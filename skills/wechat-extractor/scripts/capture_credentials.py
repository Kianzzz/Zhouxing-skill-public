#!/usr/bin/env python3
"""
读者凭证捕获脚本 V6
通过 mitmproxy 截获微信客户端的 key/uin/pass_ticket 和 __biz
使用 Shadowrocket（或其他 VPN 工具）路由 mp.weixin.qq.com 流量

V6 改进：
- request hook 捕获凭证（比 response hook 更早、更可靠）
- 追踪 __biz（支持 biz 匹配校验）
- 保存 key/uin/pass_ticket（不再依赖 appmsg_token + cookie）
- max_age_minutes: 25（准确反映凭证有效期）
- 移除系统代理管理，改用 Shadowrocket 引导

使用方式：
  python3 scripts/capture_credentials.py                    # 自动模式
  python3 scripts/capture_credentials.py --manual           # 手动输入
  python3 scripts/capture_credentials.py --upstream 1082    # 指定上游代理端口
"""
import sys
import os
import json
import time
import signal
import subprocess
from pathlib import Path

# 添加脚本目录到 path
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))
from reader_credentials import ReaderCredentials


# ============================================================
# mitmproxy V6 插件（request hook + __biz 追踪）
# ============================================================

MITM_ADDON_V6 = r'''
"""mitmproxy V6 addon: request hook 凭证捕获 + __biz 追踪"""
import json
import time
import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from mitmproxy import http

CRED_FILE = Path.home() / ".wechat-extractor" / "reader_credentials.json"
CAPTURED = False

class WeChatCredCaptureV6:
    """V6 凭证捕获器

    监听 mp.weixin.qq.com 的文章页面请求（/s 或 /s?__biz=...），
    从 URL 参数中提取 key, uin, pass_ticket 等凭证，
    同时追踪 __biz 用于 biz 匹配校验。
    """

    def request(self, flow: http.HTTPFlow):
        global CAPTURED
        if CAPTURED:
            return

        url = flow.request.pretty_url
        host = flow.request.pretty_host

        # 只关注 mp.weixin.qq.com
        if 'mp.weixin.qq.com' not in host:
            return

        # 匹配文章页面请求（包含 key 参数）
        # 场景1: /s?__biz=...&key=...
        # 场景2: /s/SHORTID?key=...
        if '/s' not in flow.request.path:
            return

        query = dict(flow.request.query.fields) if flow.request.query else {}

        # 必须有 key 参数（这是凭证的核心）
        key = query.get('key', '')
        if not key:
            return

        uin = query.get('uin', '')
        pass_ticket = query.get('pass_ticket', '')

        # 提取 __biz（可能在 URL 参数中）
        biz = query.get('__biz', '')

        # 提取 Cookie（备用）
        cookie = flow.request.headers.get('Cookie', '')

        # 保存凭证
        cred = {
            'key': key,
            'uin': uin,
            'pass_ticket': pass_ticket,
            '__biz': biz,
            'cookie': cookie,
            'appmsg_token': '',  # 将从 HTML 中提取
            'saved_at': time.time(),
            'saved_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'max_age_minutes': 25,
            'capture_url': url[:100],
        }

        CRED_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CRED_FILE, 'w', encoding='utf-8') as f:
            json.dump(cred, f, indent=2, ensure_ascii=False)

        CAPTURED = True
        print('\n' + '=' * 55)
        print('✅ 凭证捕获成功！')
        print(f'   key: {key[:20]}...')
        print(f'   uin: {uin}')
        print(f'   __biz: {biz[:12]}...' if biz else '   __biz: (未获取)')
        print(f'   有效期: ~25 分钟')
        print('=' * 55)
        print('\n⚠️  请立即执行：')
        print('   1. 按 Ctrl+C 关闭 mitmproxy')
        print('   2. 在 Shadowrocket 中将 mp.weixin.qq.com 规则改回 DIRECT')
        print('      （否则 Python 请求会路由循环！）')

addons = [WeChatCredCaptureV6()]
'''


# ============================================================
# 工具函数
# ============================================================

def check_mitmproxy():
    """检查 mitmproxy 是否已安装"""
    try:
        result = subprocess.run(
            ['mitmdump', '--version'],
            capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def find_vpn_proxy_port():
    """检测 VPN 工具的 HTTP 代理端口"""
    import socket
    # 常见端口：Shadowrocket 1082, ClashX 7890, Surge 6152
    for port in [1082, 1087, 1080, 7890, 6152, 1086]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            if result == 0:
                return port
        except Exception:
            pass
    return None


# ============================================================
# 自动捕获模式（Shadowrocket 流程）
# ============================================================

def auto_capture(upstream_port=None):
    """使用 mitmproxy + Shadowrocket 截获凭证

    流程：
    1. 检测 VPN 代理端口
    2. 启动 mitmproxy（upstream 模式）
    3. 引导用户在 Shadowrocket 中添加规则
    4. 用户在微信中打开目标公众号的一篇文章
    5. 捕获凭证
    6. 提醒用户改回 DIRECT 规则
    """
    if not check_mitmproxy():
        print("❌ mitmproxy 未安装")
        print("\n安装方法：")
        print("  pip3 install mitmproxy")
        print("\n或使用手动模式：")
        print("  python3 scripts/capture_credentials.py --manual")
        return False

    # 检测 VPN 代理端口
    if upstream_port is None:
        upstream_port = find_vpn_proxy_port()

    if upstream_port:
        print(f"🚀 检测到 VPN 代理端口: {upstream_port}")
    else:
        print("⚠️ 未检测到 VPN 代理端口，尝试常用端口 1082")
        upstream_port = 1082

    mitm_port = 8899

    # 写入 V6 addon 脚本
    addon_file = Path('/tmp/wechat_cred_capture_v6.py')
    addon_file.write_text(MITM_ADDON_V6, encoding='utf-8')

    mitm_process = None

    def cleanup(signum=None, frame=None):
        """清理：停止 mitmproxy"""
        nonlocal mitm_process
        if mitm_process:
            mitm_process.terminate()
            mitm_process = None
        if addon_file.exists():
            addon_file.unlink()
        if signum:
            sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    try:
        # 启动 mitmproxy（upstream 模式连接 VPN 代理）
        cmd = [
            'mitmdump',
            '--listen-port', str(mitm_port),
            '--mode', f'upstream:http://127.0.0.1:{upstream_port}/',
            '--ssl-insecure',
            '--set', 'connection_strategy=lazy',
            '--set', 'http2=false',
            '-s', str(addon_file)
        ]

        print(f"\n🔧 启动 mitmproxy（端口 {mitm_port}，上游 {upstream_port}）...")
        mitm_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        # 等 mitmproxy 启动
        time.sleep(3)
        if mitm_process.poll() is not None:
            print("❌ mitmproxy 启动失败")
            cleanup()
            return False

        # 引导用户设置 Shadowrocket 规则
        print("\n" + "=" * 60)
        print("📱 凭证捕获已就绪")
        print("=" * 60)
        print(f"\n🔧 请在 Shadowrocket（或其他 VPN 工具）中设置规则：")
        print(f"   DOMAIN-SUFFIX,mp.weixin.qq.com,mitmproxy")
        print(f"   （mitmproxy 代理指向 127.0.0.1:{mitm_port}）")
        print(f"\n📱 然后在微信 Mac 客户端中：")
        print(f"   打开目标公众号的任意一篇文章")
        print(f"   （凭证与公众号绑定，请打开你要获取数据的那个号的文章）")
        print(f"\n⏳ 等待捕获...\n")

        # 等待捕获
        cred_mgr = ReaderCredentials()
        while True:
            if cred_mgr.is_available():
                print("\n🎉 凭证已保存！")
                time.sleep(1)
                break

            # 检查 mitmproxy 是否还在运行
            if mitm_process.poll() is not None:
                print("❌ mitmproxy 意外退出")
                break

            time.sleep(1)

        cleanup()

        # 提醒改回 DIRECT
        print("\n" + "=" * 60)
        print("⚠️  重要：请立即在 Shadowrocket 中将规则改回 DIRECT")
        print("   DOMAIN-SUFFIX,mp.weixin.qq.com,DIRECT")
        print("   否则 Python 请求会路由循环！")
        print("=" * 60)

        return cred_mgr.is_available()

    except Exception as e:
        print(f"❌ 捕获失败: {e}")
        cleanup()
        return False


def manual_input():
    """手动输入模式"""
    cred_mgr = ReaderCredentials()
    result = cred_mgr.prompt_manual_input()
    return result is not None


# ============================================================
# 主入口
# ============================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description='读者凭证捕获工具 V6')
    parser.add_argument('--manual', action='store_true', help='手动输入模式')
    parser.add_argument('--upstream', type=int, default=None,
                       help='指定上游 VPN 代理端口（默认自动检测）')
    parser.add_argument('--force', action='store_true',
                       help='强制重新捕获（忽略现有凭证）')

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("🔐 读者凭证捕获工具 V6")
    print("=" * 60)

    # 检查现有凭证
    cred_mgr = ReaderCredentials()
    if cred_mgr.is_available() and not args.force:
        age = cred_mgr.get_age_info()
        cred = cred_mgr.load()
        biz = cred.get('__biz', '未知') if cred else '未知'
        print(f"\n✅ 已有有效凭证（{age}）")
        print(f"   __biz: {biz[:12]}..." if len(biz) > 12 else f"   __biz: {biz}")
        print("\n如需重新捕获，请加 --force 参数")
        return

    # 选择模式
    if args.manual:
        success = manual_input()
    else:
        if check_mitmproxy():
            success = auto_capture(upstream_port=args.upstream)
        else:
            print("\n⚠️ mitmproxy 未安装，切换到手动输入模式")
            print("（如需自动捕获，请先安装：pip3 install mitmproxy）\n")
            success = manual_input()

    if success:
        print("\n✅ 凭证获取成功！现在可以获取阅读数据了。")
    else:
        print("\n❌ 凭证获取失败，请重试。")
        sys.exit(1)


if __name__ == '__main__':
    main()

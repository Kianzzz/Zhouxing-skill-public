#!/usr/bin/env python3
"""
微信公众号后台重新登录 - 交互式版本
"""
from wechat_api import WeChatMPAPI
import os

def main():
    api = WeChatMPAPI()

    print("\n" + "="*60)
    print("🔐 微信公众号后台登录")
    print("="*60)

    print("\n📋 准备工作：")
    print("   • 请确保您有一个微信公众号（订阅号或服务号）")
    print("   • 如果还没有，请先注册：https://mp.weixin.qq.com/")
    print("   • 个人可注册订阅号，完全免费")

    input("\n按 Enter 键继续...")

    print("\n正在生成登录二维码...")
    qrcode_path = api.get_login_qrcode()

    if not qrcode_path:
        print("❌ 生成二维码失败")
        return

    print(f"\n✅ 二维码已保存到：{qrcode_path}")
    print("\n" + "="*60)
    print("📱 请按以下步骤操作：")
    print("="*60)
    print(f"1. 打开文件：{qrcode_path}")
    print("2. 用微信扫描二维码")
    print("3. 在手机上选择您的公众号")
    print("4. 点击确认登录")
    print("\n⏳ 等待扫码中...")
    print("   （此窗口将在扫码后自动继续，或5分钟后超时）")
    print("="*60)

    # 尝试打开二维码（macOS）
    try:
        os.system(f'open "{qrcode_path}"')
    except:
        pass

    # 开始登录流程
    success = api.login(timeout=300)

    if success:
        # 获取账号名称
        account_name = api.config.get('account_name', '未知')
        print(f"\n✅ 登录成功！")
        print(f"   账号：{account_name}")
        print(f"   配置已保存，几个月内无需再次登录")
        print("\n现在可以继续使用公众号搜索功能了。")
    else:
        print("\n❌ 登录失败")
        print("\n可能的原因：")
        print("  • 超时未扫码")
        print("  • 扫码后未确认")
        print("  • 网络连接问题")
        print("\n请重新运行此脚本重试。")

if __name__ == '__main__':
    main()

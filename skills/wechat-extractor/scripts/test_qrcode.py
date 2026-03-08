#!/usr/bin/env python3
"""测试获取登录二维码"""
from wechat_api import WeChatMPAPI
import traceback

api = WeChatMPAPI()
print("开始获取登录二维码...")

try:
    qrcode_path = api.get_login_qrcode()
    print(f"二维码路径: {qrcode_path}")

    if qrcode_path:
        import os
        file_size = os.path.getsize(qrcode_path)
        print(f"文件大小: {file_size} 字节")

        if file_size == 0:
            print("⚠️ 文件是空的，获取二维码可能失败")
        else:
            print("✅ 二维码生成成功")
    else:
        print("❌ 获取二维码返回 None")

except Exception as e:
    print(f"❌ 错误: {e}")
    traceback.print_exc()

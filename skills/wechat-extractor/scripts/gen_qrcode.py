#!/usr/bin/env python3
"""只生成二维码，不等待"""
from wechat_api import WeChatMPAPI

api = WeChatMPAPI()
qrcode_path = api.get_login_qrcode()

if qrcode_path:
    print(f"SUCCESS:{qrcode_path}")
else:
    print("FAILED:无法生成二维码")

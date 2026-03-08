#!/usr/bin/env python3
"""重新登录微信公众号后台"""
from wechat_api import WeChatMPAPI

api = WeChatMPAPI()
print("🔐 准备重新登录...")
success = api.login(timeout=300)

if success:
    print("\n✅ 登录成功！现在可以继续使用了。")
else:
    print("\n❌ 登录失败，请重试。")

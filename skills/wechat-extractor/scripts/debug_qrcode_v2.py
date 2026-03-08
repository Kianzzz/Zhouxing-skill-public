#!/usr/bin/env python3
"""调试二维码获取问题 - V2: 先访问登录页面"""
import requests
import time

base_url = "https://mp.weixin.qq.com"
session = requests.Session()

# 设置请求头
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
})

print("🔍 开始调试二维码获取 V2...")

# 步骤1: 先访问登录页面，获取必要的cookie
print("\n步骤1: 访问登录页面...")
login_page_url = "https://mp.weixin.qq.com/"
try:
    response = session.get(login_page_url, timeout=10)
    print(f"✅ 登录页面状态码: {response.status_code}")
    print(f"Cookies: {dict(session.cookies)}")
except Exception as e:
    print(f"❌ 访问登录页面失败: {e}")

# 步骤2: 获取二维码
print("\n步骤2: 获取二维码...")
qrcode_url = f"{base_url}/cgi-bin/loginqrcode"
params = {'action': 'getqrcode', 'param': '4300', 'rd': int(time.time())}

# 更新referer
session.headers['Referer'] = 'https://mp.weixin.qq.com/'

print(f"请求URL: {qrcode_url}")
print(f"请求参数: {params}")

try:
    response = session.get(qrcode_url, params=params, timeout=10)
    print(f"\n✅ 响应状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print(f"响应内容长度: {len(response.content)} 字节")

    if len(response.content) > 0:
        # 检查是否是图片
        if response.content[:4] == b'\xff\xd8\xff\xe0' or response.content[:4] == b'\xff\xd8\xff\xe1':
            print("✅ 内容是JPEG图片")
            # 保存测试
            test_path = "/Users/relax/.wechat-extractor/test_qrcode.jpg"
            with open(test_path, 'wb') as f:
                f.write(response.content)
            print(f"✅ 已保存测试二维码到: {test_path}")
        else:
            print(f"⚠️ 内容不是JPEG图片")
            print(f"前100字节: {response.content[:100]}")
    else:
        print("❌ 响应内容为空")
        print(f"RetKey: {response.headers.get('RetKey')}")
        print(f"LogicRet: {response.headers.get('LogicRet')}")

except Exception as e:
    print(f"\n❌ 请求失败: {e}")
    import traceback
    traceback.print_exc()

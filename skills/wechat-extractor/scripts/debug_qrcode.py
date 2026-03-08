#!/usr/bin/env python3
"""调试二维码获取问题"""
import requests
import time

base_url = "https://mp.weixin.qq.com"
session = requests.Session()

# 设置请求头
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://mp.weixin.qq.com'
})

print("🔍 开始调试二维码获取...")
print(f"请求URL: {base_url}/cgi-bin/loginqrcode")

url = f"{base_url}/cgi-bin/loginqrcode"
params = {'action': 'getqrcode', 'param': '4300', 'rd': int(time.time())}

print(f"请求参数: {params}")
print("\n发送请求...")

try:
    response = session.get(url, params=params, timeout=10)
    print(f"\n✅ 响应状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print(f"响应内容类型: {response.headers.get('Content-Type', 'unknown')}")
    print(f"响应内容长度: {len(response.content)} 字节")

    if len(response.content) > 0:
        # 检查是否是图片
        if response.content[:4] == b'\xff\xd8\xff\xe0' or response.content[:4] == b'\xff\xd8\xff\xe1':
            print("✅ 内容是JPEG图片")
        else:
            print(f"⚠️ 内容不是JPEG图片")
            print(f"前100字节: {response.content[:100]}")
            # 尝试解析为文本
            try:
                print(f"文本内容: {response.text[:500]}")
            except:
                pass
    else:
        print("❌ 响应内容为空")

except Exception as e:
    print(f"\n❌ 请求失败: {e}")
    import traceback
    traceback.print_exc()

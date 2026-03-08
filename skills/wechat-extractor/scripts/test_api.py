#!/usr/bin/env python3
"""直接测试获取二维码 API"""
import requests
import time

base_url = "https://mp.weixin.qq.com"
url = f"{base_url}/cgi-bin/loginqrcode"
params = {'action': 'getqrcode', 'param': '4300', 'rd': int(time.time())}

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Referer': 'https://mp.weixin.qq.com'
}

print(f"请求 URL: {url}")
print(f"参数: {params}")

try:
    response = requests.get(url, params=params, headers=headers, timeout=10)
    print(f"\n响应状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print(f"内容长度: {len(response.content)} 字节")
    print(f"内容类型: {response.headers.get('Content-Type')}")

    if response.status_code == 200:
        if len(response.content) > 0:
            print("\n✅ 获取到内容")
            # 保存到文件
            with open('/Users/relax/.wechat-extractor/test_qrcode.jpg', 'wb') as f:
                f.write(response.content)
            print("已保存到: /Users/relax/.wechat-extractor/test_qrcode.jpg")
        else:
            print("\n❌ 内容为空")
            print(f"响应文本: {response.text[:500]}")
    else:
        print(f"\n❌ 请求失败")
        print(f"响应文本: {response.text[:500]}")

except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()

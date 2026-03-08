#!/usr/bin/env python3
"""调试搜索API请求"""
from wechat_api import WeChatMPAPI
import json

api = WeChatMPAPI()

print('🔍 调试搜索API请求')
print('='*60)
print()

# 检查登录状态
print(f'1. 登录状态: {api.is_logged_in()}')
print(f'2. Token: {api.config.get("token", "无")[:30]}...')
print()

# 检查cookies
print(f'3. Session cookies:')
for cookie in api.session.cookies:
    print(f'   {cookie.name}: {cookie.value[:30]}... (domain={cookie.domain})')
print()

# 构建请求
url = f"{api.base_url}/cgi-bin/searchbiz"
params = {
    'action': 'search_biz',
    'query': '人民日报',
    'count': 3,
    'token': api.config.get('token', ''),
    'lang': 'zh_CN',
    'f': 'json',
    'ajax': '1'
}

print('4. 请求信息:')
print(f'   URL: {url}')
print(f'   Params: {json.dumps(params, indent=6, ensure_ascii=False)}')
print()
print(f'   Headers:')
for key, value in api.session.headers.items():
    print(f'      {key}: {value}')
print()

# 发送请求
print('5. 发送请求...')
try:
    response = api.session.get(url, params=params, timeout=10)
    print(f'   状态码: {response.status_code}')
    print(f'   响应头: {dict(response.headers)}')
    print()

    # 尝试解析JSON
    try:
        data = response.json()
        print(f'6. 响应内容:')
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except:
        print(f'6. 响应文本（非JSON）:')
        print(response.text[:500])

except Exception as e:
    print(f'   ❌ 请求失败: {e}')
    import traceback
    traceback.print_exc()

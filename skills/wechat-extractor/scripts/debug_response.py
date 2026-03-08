#!/usr/bin/env python3
"""调试新接口的响应格式"""
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.wechat_api import WeChatMPAPI

api = WeChatMPAPI()

if not api.is_logged_in():
    print("❌ 未登录")
    exit(1)

# 搜索公众号
accounts = api.search_account('反向的猫', count=1)
if not accounts:
    print("❌ 搜索失败")
    exit(1)

fakeid = accounts[0]['fakeid']

# 直接发送请求查看原始响应
import requests
url = f"{api.base_url}/cgi-bin/appmsgpublish"
params = {
    'sub': 'list',
    'search_field': 'null',
    'begin': 0,
    'count': 1,
    'query': '',
    'fakeid': fakeid,
    'type': '101_1',
    'free_publish_type': 1,
    'sub_action': 'list_ex',
    'token': api.config.get('token', ''),
    'lang': 'zh_CN',
    'f': 'json',
    'ajax': '1'
}

response = api.session.get(url, params=params)
data = response.json()

print("=" * 60)
print("📊 原始响应结构")
print("=" * 60)
print()

# 打印base_resp
print("1. base_resp:")
print(json.dumps(data.get('base_resp', {}), indent=2, ensure_ascii=False))
print()

# 解析publish_page
if 'publish_page' in data:
    publish_page_str = data['publish_page']
    print("2. publish_page (原始字符串长度):", len(publish_page_str))
    print()

    publish_page = json.loads(publish_page_str)

    print("3. publish_page 解析后的键:")
    print(list(publish_page.keys()))
    print()

    print("4. total_count:", publish_page.get('total_count'))
    print()

    if 'publish_list' in publish_page and len(publish_page['publish_list']) > 0:
        first_item = publish_page['publish_list'][0]
        print("5. publish_list[0] 的键:")
        print(list(first_item.keys()))
        print()

        print("6. publish_list[0] 的完整内容:")
        print(json.dumps(first_item, indent=2, ensure_ascii=False))
        print()

        if 'publish_info' in first_item:
            publish_info_str = first_item['publish_info']
            publish_info = json.loads(publish_info_str)

            print("7. publish_info 的键:")
            print(list(publish_info.keys()))
            print()

            if 'appmsgex' in publish_info and len(publish_info['appmsgex']) > 0:
                first_article = publish_info['appmsgex'][0]
                print("8. appmsgex[0] (第一篇文章) 的键:")
                print(list(first_article.keys()))
                print()

                print("9. appmsgex[0] 的完整内容:")
                print(json.dumps(first_article, indent=2, ensure_ascii=False))

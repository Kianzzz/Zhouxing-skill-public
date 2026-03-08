#!/usr/bin/env python3
"""
改进的公众号搜索脚本 - V2.7 迭代版
包含自动数据验证，避免数据不完整的问题

关键改进：
✅ 自动验证数据完整性 - 比较新旧接口的差异
✅ 优先使用新接口 (appmsgpublish) - 返回完整数据
✅ 清晰的数据检验提示 - 告知用户数据是否完整
✅ 更好的错误处理 - 自动降级和提示
"""

import sys
from pathlib import Path
from wechat_api import WeChatMPAPI

def main():
    # 检查登录
    api = WeChatMPAPI()
    if not api.is_logged_in():
        print("❌ 未登录，请先运行登录脚本")
        print("   python3 login_smart.py")
        return

    # 获取搜索关键词
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
    else:
        query = input("请输入要搜索的公众号名称：").strip()

    if not query:
        print("❌ 搜索关键词不能为空")
        return

    print(f"\n{'='*70}")
    print(f"🔍 开始搜索：{query}")
    print(f"{'='*70}\n")

    # 使用改进的搜索方法（包含验证）
    result = api.search_account_with_validation(query)

    if result['status'] == 'error':
        print(f"❌ {result['message']}")
        return

    accounts = result['accounts']
    validation = result['validation']

    # 显示搜索结果
    print(f"\n📊 搜索结果（共 {len(accounts)} 个）：\n")
    for idx, account in enumerate(accounts, 1):
        print(f"{idx}. {account.get('nickname', '未知')}")
        print(f"   微信号：{account.get('alias', '未知')}")
        print(f"   ID：{account.get('fakeid', '未知')}")
        print()

    # 显示第一个结果的验证信息
    if accounts:
        print(f"\n{'='*70}")
        print(f"📋 首个结果的数据验证报告")
        print(f"{'='*70}\n")

        first_account = accounts[0]
        fakeid = first_account.get('fakeid')
        nickname = first_account.get('nickname')

        print(f"公众号：{nickname}")
        print(f"微信号：{first_account.get('alias', '未知')}")
        print(f"简介：{first_account.get('signature', '无')}\n")

        # 显示验证结果
        print(f"📊 数据验证结果：\n")
        print(f"  新接口 (appmsgpublish): {validation.get('new_api_count', 0):>6} 篇")
        print(f"  旧接口 (appmsg):        {validation.get('old_api_count', 0):>6} 篇")
        print(f"  数据差异率：            {validation.get('difference_ratio', 0)*100:>5.1f}%\n")

        # 验证状态
        if validation['status'] == 'warning':
            print(f"⚠️  数据可能不完整！")
            print(f"    旧接口只能返回部分数据，已自动使用新接口的完整数据")
        elif validation['status'] == 'success':
            print(f"✅ 数据一致且完整！")
        else:
            print(f"❌ 数据验证失败")

        print(f"\n{'='*70}\n")

        # 获取文章信息
        print(f"📥 正在获取文章列表...\n")
        articles_result = api.get_articles(fakeid, begin=0, count=10)
        articles = articles_result.get('articles', [])
        total = articles_result.get('total', 0)

        print(f"✅ 共有 {total} 篇文章\n")
        print(f"📋 最近 10 篇：\n")

        for idx, article in enumerate(articles, 1):
            title = article.get('title', '未知标题')[:50]
            create_time = article.get('create_time', '未知时间')
            print(f"{idx:2d}. {title}")
            print(f"    📅 {create_time}\n")

        print(f"\n{'='*70}")
        print(f"\n💡 你现在可以：")
        print(f"   📥 下载文章")
        print(f"   🔍 按时间/关键词筛选")
        print(f"   📊 分析写作风格")
        print(f"   或其他操作\n")

if __name__ == '__main__':
    main()

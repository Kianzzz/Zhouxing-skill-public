#!/usr/bin/env python3
"""全面测试新的appmsgpublish接口"""
import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.wechat_api import WeChatMPAPI

def test_search_and_list():
    """测试1: 搜索公众号并获取文章列表"""
    print("=" * 70)
    print("🧪 测试1: 搜索公众号并获取文章列表")
    print("=" * 70)
    print()

    api = WeChatMPAPI()

    if not api.is_logged_in():
        print("❌ 未登录")
        return False

    # 搜索公众号
    print("🔍 搜索公众号: 反向的猫")
    accounts = api.search_account('反向的猫', count=3)

    if not accounts:
        print("❌ 搜索失败")
        return False

    print(f"✅ 找到 {len(accounts)} 个公众号")
    target = accounts[0]
    print(f"   选择: {target.get('nickname')}")
    print()

    # 获取文章列表
    print("📄 获取最新5篇文章...")
    result = api.get_articles(target['fakeid'], begin=0, count=5)

    if result['articles']:
        print(f"✅ 成功！获取到 {len(result['articles'])} 篇文章")
        for i, article in enumerate(result['articles'][:3], 1):
            print(f"   {i}. {article.get('title', '未知')[:30]}...")
        print()
        return True
    else:
        print("❌ 获取失败")
        return False

def test_pagination():
    """测试2: 分页功能"""
    print("=" * 70)
    print("🧪 测试2: 分页功能")
    print("=" * 70)
    print()

    api = WeChatMPAPI()
    accounts = api.search_account('反向的猫', count=1)

    if not accounts:
        print("❌ 搜索失败")
        return False

    fakeid = accounts[0]['fakeid']

    # 获取第1页
    print("📄 获取第1页（0-5）...")
    page1 = api.get_articles(fakeid, begin=0, count=5)
    time.sleep(0.5)

    # 获取第2页
    print("📄 获取第2页（5-10）...")
    page2 = api.get_articles(fakeid, begin=5, count=5)

    if page1['articles'] and page2['articles']:
        title1 = page1['articles'][0].get('title', '')
        title2 = page2['articles'][0].get('title', '')

        print(f"✅ 分页成功！")
        print(f"   第1页首篇: {title1[:30]}...")
        print(f"   第2页首篇: {title2[:30]}...")

        # 验证两页不同
        if title1 != title2:
            print(f"✅ 确认获取到不同文章")
            print()
            return True
        else:
            print(f"⚠️  两页内容相同（异常）")
            print()
            return False
    else:
        print("❌ 分页失败")
        return False

def test_keyword_search():
    """测试3: 关键词搜索"""
    print("=" * 70)
    print("🧪 测试3: 关键词搜索")
    print("=" * 70)
    print()

    api = WeChatMPAPI()
    accounts = api.search_account('反向的猫', count=1)

    if not accounts:
        print("❌ 搜索失败")
        return False

    fakeid = accounts[0]['fakeid']

    # 搜索包含"女性"关键词的文章
    print("🔍 搜索关键词: 女性")
    result = api.get_articles(fakeid, begin=0, count=5, query='女性')

    if result['articles']:
        print(f"✅ 搜索成功！找到 {len(result['articles'])} 篇相关文章")
        for i, article in enumerate(result['articles'][:3], 1):
            title = article.get('title', '未知')
            print(f"   {i}. {title[:40]}...")
            # 验证标题或摘要包含关键词
            digest = article.get('digest', '')
            if '女性' in title or '女性' in digest:
                print(f"      ✓ 包含关键词")
        print()
        return True
    else:
        print("⚠️  未找到相关文章")
        print()
        return False

def test_speed():
    """测试4: 速度测试（5次请求）"""
    print("=" * 70)
    print("🧪 测试4: 速度测试")
    print("=" * 70)
    print()

    api = WeChatMPAPI()
    accounts = api.search_account('反向的猫', count=1)

    if not accounts:
        print("❌ 搜索失败")
        return False

    fakeid = accounts[0]['fakeid']

    print("⏱️  连续5次获取文章（无延迟）...")
    times = []

    for i in range(5):
        start = time.time()
        result = api.get_articles(fakeid, begin=i*5, count=5)
        elapsed = time.time() - start
        times.append(elapsed)

        if result['articles']:
            print(f"   请求{i+1}: {elapsed:.2f}秒 ✓")
        else:
            print(f"   请求{i+1}: 失败 ✗")
            return False

    avg_time = sum(times) / len(times)
    print()
    print(f"✅ 平均耗时: {avg_time:.2f}秒")
    print(f"✅ 总耗时: {sum(times):.2f}秒（5次请求）")
    print()

    if avg_time < 3:
        print("✅ 速度优秀！（<3秒/次）")
        return True
    elif avg_time < 5:
        print("✅ 速度良好（3-5秒/次）")
        return True
    else:
        print("⚠️  速度较慢（>5秒/次）")
        return False

def test_no_security_check():
    """测试5: 验证不触发安全验证（10次连续请求）"""
    print("=" * 70)
    print("🧪 测试5: 安全验证检测（10次连续请求）")
    print("=" * 70)
    print()

    api = WeChatMPAPI()
    accounts = api.search_account('反向的猫', count=1)

    if not accounts:
        print("❌ 搜索失败")
        return False

    fakeid = accounts[0]['fakeid']

    print("🔥 连续10次快速请求（压力测试）...")
    success_count = 0

    for i in range(10):
        result = api.get_articles(fakeid, begin=i*5, count=5)

        if result['articles']:
            success_count += 1
            print(f"   请求{i+1:2d}: ✅ 成功")
        else:
            print(f"   请求{i+1:2d}: ❌ 失败（可能触发验证）")

        # 不加延迟，测试极限情况
        # time.sleep(0)

    print()
    print(f"📊 成功率: {success_count}/10 = {success_count*10}%")

    if success_count == 10:
        print("🎉 完美！所有请求成功，未触发安全验证")
        return True
    elif success_count >= 8:
        print("✅ 良好！成功率>=80%")
        return True
    else:
        print("⚠️  部分请求失败，可能触发验证")
        return False

def main():
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + " " * 15 + "新接口全面测试套件" + " " * 28 + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    print()

    tests = [
        ("基础功能", test_search_and_list),
        ("分页功能", test_pagination),
        ("关键词搜索", test_keyword_search),
        ("速度性能", test_speed),
        ("安全验证", test_no_security_check),
    ]

    results = []

    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
            time.sleep(1)  # 测试间隔1秒
        except Exception as e:
            print(f"❌ {name}测试出错: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # 汇总结果
    print()
    print("=" * 70)
    print("📊 测试结果汇总")
    print("=" * 70)
    print()

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {name:12s}: {status}")

    print()
    print(f"总计: {passed}/{total} 通过")

    if passed == total:
        print()
        print("🎉 恭喜！所有测试通过，新接口工作完美！")
    elif passed >= total * 0.8:
        print()
        print("✅ 大部分测试通过，接口工作良好！")
    else:
        print()
        print("⚠️  部分测试失败，需要进一步调试")

if __name__ == '__main__':
    main()

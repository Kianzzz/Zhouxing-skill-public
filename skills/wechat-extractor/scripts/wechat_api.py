#!/usr/bin/env python3
"""
微信公众号后台 API 封装
用于搜索公众号、获取文章列表等操作
"""

import requests
import json
import time
import os
from pathlib import Path
from urllib.parse import urlencode

class WeChatMPAPI:
    """微信公众号后台 API 客户端"""

    def __init__(self, config_dir=None):
        """初始化 API 客户端

        Args:
            config_dir: 配置文件目录，默认为 ~/.wechat-extractor/
        """
        if config_dir is None:
            config_dir = Path.home() / ".wechat-extractor"

        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "config.json"
        self.cache_dir = self.config_dir / "cache"  # 新增：缓存目录
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.config = self.load_config()

        self.base_url = "https://mp.weixin.qq.com"
        self.session = requests.Session()

        # 设置请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Referer': 'https://mp.weixin.qq.com'
        })

        # 如果已有 cookie，设置到 session
        if self.config and 'cookies' in self.config:
            for cookie in self.config['cookies']:
                # 设置完整的cookie信息（包括domain和path）
                self.session.cookies.set(
                    name=cookie['name'],
                    value=cookie['value'],
                    domain=cookie.get('domain', '.weixin.qq.com'),
                    path=cookie.get('path', '/')
                )

    def load_config(self):
        """加载本地配置"""
        if not self.config_file.exists():
            return None

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 检查 token 是否过期
            if 'expires_at' in config:
                if time.time() > config['expires_at']:
                    print("⚠️ Token 已过期，需要重新登录")
                    return None

            return config
        except Exception as e:
            print(f"加载配置失败: {e}")
            return None

    def save_config(self, config):
        """保存配置到本地"""
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # 设置过期时间为 3 个月后
        config['expires_at'] = time.time() + (90 * 24 * 3600)
        config['last_updated'] = time.time()

        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        self.config = config
        print(f"✅ 配置已保存到：{self.config_file}")

    def is_logged_in(self):
        """检查是否已登录"""
        return self.config is not None and 'token' in self.config

    def get_login_qrcode(self):
        """获取登录二维码"""
        url = f"{self.base_url}/cgi-bin/loginqrcode"
        params = {'action': 'getqrcode', 'param': '4300', 'rd': int(time.time())}

        try:
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                # 保存二维码图片
                qrcode_path = self.config_dir / "login_qrcode.jpg"
                qrcode_path.parent.mkdir(parents=True, exist_ok=True)
                with open(qrcode_path, 'wb') as f:
                    f.write(response.content)

                return str(qrcode_path)
            else:
                print(f"获取二维码失败: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"获取二维码失败: {e}")
            return None

    def check_login_status(self):
        """检查登录状态"""
        url = f"{self.base_url}/cgi-bin/loginqrcode"
        params = {'action': 'ask', 'token': '', 'lang': 'zh_CN', 'f': 'json', 'ajax': '1'}

        try:
            response = self.session.get(url, params=params)
            data = response.json()

            # status: 0=等待扫码, 1=已扫码待确认, 2=已确认, 3=已取消, 4=二维码过期
            return data.get('status', -1)
        except Exception as e:
            print(f"检查登录状态失败: {e}")
            return -1

    def login(self, timeout=300):
        """登录流程

        Args:
            timeout: 超时时间（秒），默认 5 分钟

        Returns:
            bool: 登录是否成功
        """
        print("🔐 开始登录流程...")

        # 1. 获取二维码
        qrcode_path = self.get_login_qrcode()
        if not qrcode_path:
            return False

        print(f"\n📱 请用微信扫描二维码：{qrcode_path}")
        print("   选择你的公众号进行登录")
        print("   等待扫码中...\n")

        # 2. 轮询检查登录状态
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = self.check_login_status()

            if status == 1:
                print("✅ 已扫码，等待确认...")
            elif status == 2:
                print("✅ 登录成功！")
                # 保存登录信息
                self._save_login_info()
                return True
            elif status == 3:
                print("❌ 用户取消登录")
                return False
            elif status == 4:
                print("⏰ 二维码已过期，请重新登录")
                return False

            time.sleep(2)

        print("⏰ 登录超时")
        return False

    def _save_login_info(self):
        """保存登录信息"""
        # 提取 token 和 cookies
        token = None
        cookies = []

        for cookie in self.session.cookies:
            cookies.append({
                'name': cookie.name,
                'value': cookie.value,
                'domain': cookie.domain
            })

            # 通常 token 存储在某个特定的 cookie 中
            if cookie.name in ['token', 'wxtoken', 'data_ticket']:
                token = cookie.value

        # 保存到配置文件
        config = {
            'token': token,
            'cookies': cookies
        }
        self.save_config(config)

    def search_account(self, query, count=10):
        """搜索公众号

        Args:
            query: 搜索关键词（公众号名称）
            count: 返回结果数量

        Returns:
            list: 搜索结果列表，带有验证信息的增强版本
        """
        if not self.is_logged_in():
            print("❌ 未登录，请先登录")
            return []

        url = f"{self.base_url}/cgi-bin/searchbiz"
        params = {
            'action': 'search_biz',
            'query': query,
            'count': count,
            'token': self.config.get('token', ''),
            'lang': 'zh_CN',
            'f': 'json',
            'ajax': '1'
        }

        try:
            response = self.session.get(url, params=params)
            data = response.json()

            if data.get('base_resp', {}).get('ret') == 0:
                accounts = data.get('list', [])
                print(f"✅ 找到 {len(accounts)} 个公众号\n")

                # 对第一个搜索结果进行数据验证（可选，避免重复验证）
                if accounts and len(accounts) > 0:
                    first_account = accounts[0]
                    fakeid = first_account.get('fakeid')
                    nickname = first_account.get('nickname')

                    print(f"📋 首个结果：{nickname}")
                    print(f"   微信号：{first_account.get('alias', '未知')}")
                    print(f"   简介：{first_account.get('signature', '无')[:50]}")
                    print()

                return accounts
            else:
                error_msg = data.get('base_resp', {}).get('err_msg', '未知错误')
                print(f"❌ 搜索失败: {error_msg}")
                return []
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            return []

    def search_account_with_validation(self, query, count=10):
        """搜索公众号并验证数据完整性（增强版）

        Args:
            query: 搜索关键词（公众号名称）
            count: 返回结果数量

        Returns:
            dict: 包含搜索结果和验证信息的字典
        """
        accounts = self.search_account(query, count)

        if not accounts:
            return {
                'status': 'error',
                'message': '搜索失败',
                'accounts': []
            }

        # 对第一个结果进行验证
        first_account = accounts[0]
        fakeid = first_account.get('fakeid')
        nickname = first_account.get('nickname')

        print(f"🔍 正在验证首个搜索结果的数据完整性...")
        print(f"   公众号：{nickname}\n")

        validation_result = self.validate_article_count(fakeid)

        return {
            'status': validation_result.get('status', 'success'),
            'message': validation_result.get('message', ''),
            'accounts': accounts,
            'validation': validation_result,
            'first_account': first_account
        }

    def get_articles(self, fakeid, begin=0, count=5, type=9, query=''):
        """获取公众号文章列表（优先使用appmsgpublish接口 ✅）

        ⭐ 重要：
        - 此方法使用新的 appmsgpublish 接口，返回完整的文章列表
        - 可靠返回 total_count（所有文章总数）
        - 比旧的 appmsg 接口更准确、更完整

        Args:
            fakeid: 公众号的 fakeid（从搜索结果中获取）
            begin: 起始位置（用于分页）
            count: 获取数量（每页）
            type: 文章类型（9=全部, 1=原创, 2=转载）- 此参数保留用于兼容但不再使用
            query: 搜索关键词（标题/摘要）

        Returns:
            dict: 包含文章列表和总数的字典
                {
                    'articles': [...],  # 文章列表
                    'total': 2833,      # 文章总数（完整数据）
                    'has_more': True    # 是否有更多数据
                }
        """
        if not self.is_logged_in():
            print("❌ 未登录，请先登录")
            return {'articles': [], 'total': 0}

        # 使用新的appmsgpublish接口
        url = f"{self.base_url}/cgi-bin/appmsgpublish"

        # 判断是否为搜索模式
        is_searching = bool(query)

        params = {
            'sub': 'search' if is_searching else 'list',
            'search_field': '7' if is_searching else 'null',
            'begin': begin,
            'count': count,
            'query': query,
            'fakeid': fakeid,
            'type': '101_1',  # 新接口使用的类型参数
            'free_publish_type': 1,
            'sub_action': 'list_ex',
            'token': self.config.get('token', ''),
            'lang': 'zh_CN',
            'f': 'json',
            'ajax': '1'
        }

        try:
            response = self.session.get(url, params=params)
            data = response.json()

            if data.get('base_resp', {}).get('ret') == 0:
                # 新接口的响应格式：publish_page是JSON字符串
                publish_page_str = data.get('publish_page', '{}')
                publish_page = json.loads(publish_page_str)

                publish_list = publish_page.get('publish_list', [])
                total = publish_page.get('total_count', 0)

                # 解析文章列表
                articles = []
                for item in publish_list:
                    try:
                        # publish_info也是JSON字符串
                        publish_info_str = item.get('publish_info', '{}')
                        publish_info = json.loads(publish_info_str)

                        # 文章列表在appmsgex字段中
                        appmsgex = publish_info.get('appmsgex', [])

                        # 获取发送时间（作为备用）
                        sent_info = publish_info.get('sent_info', {})
                        publish_time_fallback = sent_info.get('time', 0)

                        for article in appmsgex:
                            # 文章自身就包含时间字段，优先使用
                            # create_time: 创建时间, update_time: 更新时间
                            if 'create_time' not in article and publish_time_fallback:
                                article['create_time'] = publish_time_fallback
                            if 'update_time' not in article and publish_time_fallback:
                                article['update_time'] = publish_time_fallback

                            articles.append(article)

                    except json.JSONDecodeError as e:
                        print(f"⚠️  解析文章数据失败: {e}")
                        continue

                print(f"✅ 获取到 {len(articles)} 篇文章（共 {total} 篇）")

                return {
                    'articles': articles,
                    'total': total,
                    'has_more': begin + len(articles) < total
                }
            else:
                error_msg = data.get('base_resp', {}).get('err_msg', '未知错误')
                error_ret = data.get('base_resp', {}).get('ret', -1)
                print(f"❌ 获取文章列表失败 (ret={error_ret}): {error_msg}")
                return {'articles': [], 'total': 0}
        except Exception as e:
            print(f"❌ 获取文章列表失败: {e}")
            import traceback
            traceback.print_exc()
            return {'articles': [], 'total': 0}

    def search_articles(self, fakeid, keyword='', start_date=None, end_date=None,
                       article_type=9, max_count=None):
        """搜索公众号文章（支持关键词和时间筛选）

        Args:
            fakeid: 公众号的 fakeid
            keyword: 搜索关键词（标题/摘要）
            start_date: 开始日期 '2025-01-01' 或时间戳
            end_date: 结束日期 '2025-12-31' 或时间戳
            article_type: 9=全部, 1=原创, 2=转载
            max_count: 最大返回数量

        Returns:
            list: 筛选后的文章列表
        """
        if keyword:
            print(f"🔍 搜索关键词：{keyword}")
        if start_date or end_date:
            print(f"📅 时间范围：{start_date or '不限'} ~ {end_date or '不限'}")

        # 先获取所有文章
        all_articles = self.get_all_articles(fakeid, query=keyword,
                                            article_type=article_type)

        # 时间筛选
        if start_date or end_date:
            all_articles = self.filter_articles_by_time(all_articles, start_date, end_date)

        # 限制数量
        if max_count:
            all_articles = all_articles[:max_count]

        return all_articles

    def filter_articles_by_time(self, articles, start_date=None, end_date=None):
        """按时间范围筛选文章

        Args:
            articles: 文章列表
            start_date: 开始日期（字符串 '2025-01-01' 或时间戳）
            end_date: 结束日期（字符串 '2025-12-31' 或时间戳）

        Returns:
            list: 筛选后的文章列表
        """
        from datetime import datetime

        # 转换日期为时间戳
        start_ts = None
        end_ts = None

        if start_date:
            if isinstance(start_date, str):
                start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
            else:
                start_ts = int(start_date)

        if end_date:
            if isinstance(end_date, str):
                end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp()) + 86400  # 加一天
            else:
                end_ts = int(end_date)

        filtered = []
        for article in articles:
            create_time = article.get('create_time', 0)

            if start_ts and create_time < start_ts:
                continue
            if end_ts and create_time > end_ts:
                continue

            filtered.append(article)

        print(f"✅ 时间筛选后剩余 {len(filtered)} 篇文章")
        return filtered

    def get_all_articles(self, fakeid, max_count=None, query='', article_type=9,
                        show_progress=True):
        """获取公众号所有文章（分页自动加载）

        Args:
            fakeid: 公众号的 fakeid
            max_count: 最大获取数量（None 表示全部）
            query: 搜索关键词
            article_type: 9=全部, 1=原创, 2=转载
            show_progress: 是否显示进度

        Returns:
            list: 所有文章列表
        """
        all_articles = []
        begin = 0
        page_size = 5  # 每页5篇，避免请求过大

        if show_progress:
            print(f"📥 开始获取文章列表...")

        while True:
            result = self.get_articles(fakeid, begin=begin, count=page_size,
                                      type=article_type, query=query)
            articles = result['articles']
            total = result.get('total', 0)

            if not articles:
                break

            all_articles.extend(articles)

            # 显示进度
            if show_progress and total > 0:
                progress = min(100, int(len(all_articles) / total * 100))
                print(f"   进度: {len(all_articles)}/{total} ({progress}%)")

            # 检查是否达到最大数量
            if max_count and len(all_articles) >= max_count:
                all_articles = all_articles[:max_count]
                break

            # 检查是否还有更多
            if not result.get('has_more', False):
                break

            begin += page_size

            # 延迟，避免请求过快
            time.sleep(0.5)

        if show_progress:
            print(f"✅ 共获取 {len(all_articles)} 篇文章")
        return all_articles

    def save_articles_index(self, articles, filename='articles_index.json'):
        """保存文章列表索引到文件

        Args:
            articles: 文章列表
            filename: 保存的文件名

        Returns:
            str: 保存的文件路径
        """
        from datetime import datetime

        # 简化文章信息
        simple_articles = []
        for i, article in enumerate(articles, 1):
            create_time = article.get('create_time', 0)
            date_str = datetime.fromtimestamp(create_time).strftime('%Y-%m-%d')

            simple_articles.append({
                'index': i,
                'title': article.get('title', ''),
                'link': article.get('link', ''),
                'digest': article.get('digest', ''),
                'create_time': create_time,
                'date': date_str,
                'author': article.get('author', '')
            })

        # 保存到文件
        filepath = self.config_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(simple_articles, f, indent=2, ensure_ascii=False)

        print(f"📄 文章列表已保存到：{filepath}")
        return str(filepath)

    def get_article_metadata(self, article_url, credentials=None):
        """获取文章元数据（阅读量、点赞、在看、评论数等）

        Args:
            article_url: 文章链接
            credentials: 可选，包含抓包获取的认证信息
                {
                    'appmsg_token': 'xxx',
                    'cookie': 'xxx'
                }

        Returns:
            dict: 元数据字典
                {
                    'read_num': 10532,      # 阅读量
                    'old_like_num': 256,    # 点赞 👍
                    'like_num': 99,         # 在看 👀
                    'comment_count': 42,    # 评论数
                    'share_count': 0,       # 分享数（如果可用）
                    'is_original': True     # 是否原创
                }
        """
        if not credentials:
            print("⚠️ 未提供 credentials，无法获取元数据")
            print("   获取方法：参考文档 https://docs.mptext.top/advanced/wxdown-service.html")
            return None

        try:
            # 从文章 URL 提取必要参数
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(article_url)

            # 构建元数据请求
            url = f"{self.base_url}/mp/getappmsgext"
            params = {
                'appmsg_token': credentials.get('appmsg_token'),
                '__biz': parse_qs(parsed.query).get('__biz', [''])[0],
                'mid': parse_qs(parsed.query).get('mid', [''])[0],
                'sn': parse_qs(parsed.query).get('sn', [''])[0],
                'idx': parse_qs(parsed.query).get('idx', ['1'])[0],
            }

            headers = {
                'Cookie': credentials.get('cookie'),
                'User-Agent': self.session.headers['User-Agent'],
                'Referer': article_url
            }

            response = requests.get(url, params=params, headers=headers,
                                     verify=False)
            data = response.json()

            if data.get('base_resp', {}).get('ret') == 0:
                appmsgstat = data.get('appmsgstat', {})
                comment_data = data.get('comment_enabled', {})

                metadata = {
                    'read_num': appmsgstat.get('read_num', 0),
                    'like_num': appmsgstat.get('like_num', 0),
                    'old_like_num': appmsgstat.get('old_like_num', 0),
                    'comment_count': comment_data.get('elected_comment_total_cnt', 0),
                    'share_count': appmsgstat.get('share_num', 0),
                    'is_original': data.get('is_original', False)
                }

                print(f"✅ 获取元数据成功：阅读 {metadata['read_num']}，点赞👍 {metadata['old_like_num']}，在看👀 {metadata['like_num']}")
                return metadata
            else:
                error_msg = data.get('base_resp', {}).get('err_msg', '未知错误')
                print(f"❌ 获取元数据失败: {error_msg}")
                return None

        except Exception as e:
            print(f"❌ 获取元数据失败: {e}")
            return None

    def search_articles_advanced(self, fakeid,
                                 keyword='',
                                 start_date=None,
                                 end_date=None,
                                 article_type=9,
                                 author='',
                                 min_read_num=None,
                                 max_read_num=None,
                                 is_original=None,
                                 has_collection=None,
                                 max_count=None):
        """高级搜索公众号文章（支持更多筛选条件）

        Args:
            fakeid: 公众号的 fakeid
            keyword: 搜索关键词（标题/摘要）
            start_date: 开始日期 '2025-01-01' 或时间戳
            end_date: 结束日期 '2025-12-31' 或时间戳
            article_type: 9=全部, 1=原创, 2=转载
            author: 作者名称筛选
            min_read_num: 最小阅读量（需要文章已获取元数据）
            max_read_num: 最大阅读量（需要文章已获取元数据）
            is_original: 是否原创（True/False/None）
            has_collection: 是否属于合集（True/False/None）
            max_count: 最大返回数量

        Returns:
            list: 筛选后的文章列表
        """
        print(f"🔍 开始高级搜索...")

        if keyword:
            print(f"   关键词：{keyword}")
        if start_date or end_date:
            print(f"   时间范围：{start_date or '不限'} ~ {end_date or '不限'}")
        if author:
            print(f"   作者：{author}")
        if min_read_num is not None:
            print(f"   最小阅读量：{min_read_num}")
        if is_original is not None:
            print(f"   原创筛选：{'仅原创' if is_original else '仅非原创'}")
        if has_collection is not None:
            print(f"   合集筛选：{'仅合集文章' if has_collection else '仅非合集文章'}")

        # 先获取所有文章
        all_articles = self.get_all_articles(fakeid, query=keyword, article_type=article_type)

        # 应用各种筛选条件
        filtered = all_articles

        # 时间筛选
        if start_date or end_date:
            filtered = self.filter_articles_by_time(filtered, start_date, end_date)

        # 作者筛选
        if author:
            filtered = [a for a in filtered if author in a.get('author', '')]
            print(f"✅ 作者筛选后剩余 {len(filtered)} 篇文章")

        # 阅读量筛选（需要文章包含元数据）
        if min_read_num is not None or max_read_num is not None:
            temp = []
            for article in filtered:
                read_num = article.get('read_num', 0)
                if min_read_num is not None and read_num < min_read_num:
                    continue
                if max_read_num is not None and read_num > max_read_num:
                    continue
                temp.append(article)
            filtered = temp
            print(f"✅ 阅读量筛选后剩余 {len(filtered)} 篇文章")

        # 原创筛选
        if is_original is not None:
            filtered = [a for a in filtered if a.get('copyright_stat') == (11 if is_original else 0)]
            print(f"✅ 原创筛选后剩余 {len(filtered)} 篇文章")

        # 合集筛选
        if has_collection is not None:
            if has_collection:
                filtered = [a for a in filtered if a.get('album_id')]
            else:
                filtered = [a for a in filtered if not a.get('album_id')]
            print(f"✅ 合集筛选后剩余 {len(filtered)} 篇文章")

        # 限制数量
        if max_count and len(filtered) > max_count:
            filtered = filtered[:max_count]
            print(f"✅ 限制数量为 {max_count} 篇")

        print(f"✅ 搜索完成，共找到 {len(filtered)} 篇文章")
        return filtered

    def load_articles_cache(self, fakeid, max_age_hours=24):
        """加载文章列表缓存

        Args:
            fakeid: 公众号的 fakeid
            max_age_hours: 缓存最大有效期（小时），默认 24 小时

        Returns:
            list: 缓存的文章列表，如果缓存不存在或过期则返回 None
        """
        cache_file = self.cache_dir / f"articles_{fakeid}.json"

        if not cache_file.exists():
            print("📦 缓存不存在")
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            # 检查缓存是否过期
            cache_time = cache_data.get('cache_time', 0)
            age_hours = (time.time() - cache_time) / 3600

            if age_hours > max_age_hours:
                print(f"⏰ 缓存已过期（{age_hours:.1f} 小时前）")
                return None

            articles = cache_data.get('articles', [])
            print(f"✅ 使用缓存数据（{age_hours:.1f} 小时前，共 {len(articles)} 篇文章）")
            return articles

        except Exception as e:
            print(f"❌ 加载缓存失败: {e}")
            return None

    def save_articles_cache(self, fakeid, articles):
        """保存文章列表到缓存

        Args:
            fakeid: 公众号的 fakeid
            articles: 文章列表

        Returns:
            str: 缓存文件路径
        """
        cache_file = self.cache_dir / f"articles_{fakeid}.json"

        cache_data = {
            'cache_time': time.time(),
            'fakeid': fakeid,
            'total': len(articles),
            'articles': articles
        }

        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)

        print(f"💾 缓存已保存：{cache_file}")
        return str(cache_file)

    def get_all_articles_cached(self, fakeid, max_count=None, query='',
                                article_type=9, show_progress=True,
                                use_cache=True, cache_hours=24):
        """获取公众号所有文章（支持缓存）

        Args:
            fakeid: 公众号的 fakeid
            max_count: 最大获取数量（None 表示全部）
            query: 搜索关键词
            article_type: 9=全部, 1=原创, 2=转载
            show_progress: 是否显示进度
            use_cache: 是否使用缓存，默认 True
            cache_hours: 缓存有效期（小时），默认 24 小时

        Returns:
            list: 所有文章列表
        """
        # 尝试从缓存加载
        if use_cache and not query:  # 有搜索关键词时不使用缓存
            cached = self.load_articles_cache(fakeid, max_age_hours=cache_hours)
            if cached is not None:
                if max_count:
                    return cached[:max_count]
                return cached

        # 缓存未命中，从 API 获取
        print("📥 从服务器获取文章列表...")
        articles = self.get_all_articles(fakeid, max_count, query, article_type, show_progress)

        # 保存到缓存（仅当没有搜索关键词时）
        if not query:
            self.save_articles_cache(fakeid, articles)

        return articles

    def clear_cache(self, fakeid=None):
        """清除缓存

        Args:
            fakeid: 可选，指定清除某个公众号的缓存。如果不指定则清除所有缓存
        """
        if fakeid:
            cache_file = self.cache_dir / f"articles_{fakeid}.json"
            if cache_file.exists():
                cache_file.unlink()
                print(f"✅ 已清除缓存：{cache_file}")
            else:
                print(f"⚠️ 缓存不存在：{cache_file}")
        else:
            # 清除所有缓存
            count = 0
            for cache_file in self.cache_dir.glob("articles_*.json"):
                cache_file.unlink()
                count += 1
            print(f"✅ 已清除 {count} 个缓存文件")

    def validate_article_count(self, fakeid):
        """验证文章数据完整性 - 比较新旧接口的数据

        Args:
            fakeid: 公众号的fakeid

        Returns:
            dict: 包含验证结果和统计数据的字典
        """
        if not self.is_logged_in():
            return {'status': 'error', 'message': '未登录'}

        import time as time_module

        print(f"\n🔍 正在验证文章数据完整性...\n")

        # 方法1：使用新的 appmsgpublish 接口
        print(f"📍 方法1：新接口 (appmsgpublish)...")
        new_api_count = 0
        try:
            result = self.get_articles(fakeid, begin=0, count=1)
            new_api_count = result.get('total', 0)
            print(f"   ✅ 返回总数：{new_api_count} 篇")
        except Exception as e:
            print(f"   ❌ 获取失败：{e}")

        # 方法2：使用旧的 appmsg 接口
        print(f"\n📍 方法2：旧接口 (appmsg)...")
        old_api_count = 0
        try:
            url = f"{self.base_url}/cgi-bin/appmsg"
            params = {
                'action': 'list',
                'begin': '0',
                'count': '1',
                'fakeid': fakeid,
                'token': self.config.get('token', ''),
                'type': '101_1',
                'lang': 'zh_CN',
                'f': 'json',
                'ajax': '1'
            }
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            file_cnt = data.get('app_msg_info', {}).get('file_cnt', {})
            old_api_count = file_cnt.get('app_msg_cnt', 0)
            print(f"   ✅ 返回总数：{old_api_count} 篇")
        except Exception as e:
            print(f"   ❌ 获取失败：{e}")

        # 分析数据差异
        print(f"\n📊 数据对比：")
        print(f"   新接口 (appmsgpublish): {new_api_count} 篇")
        print(f"   旧接口 (appmsg):        {old_api_count} 篇")

        if new_api_count == 0:
            return {
                'status': 'error',
                'message': '新接口获取失败，无法验证',
                'new_api_count': new_api_count,
                'old_api_count': old_api_count
            }

        difference_ratio = abs(new_api_count - old_api_count) / new_api_count if new_api_count > 0 else 0

        print(f"   数据差异率：{difference_ratio*100:.1f}%")

        # 判断数据是否完整
        if difference_ratio > 0.5:  # 差异超过50%视为数据不完整
            print(f"\n⚠️  WARNING: 数据可能不完整！")
            print(f"   • 新接口显示 {new_api_count} 篇（可信度高）")
            print(f"   • 旧接口只返回 {old_api_count} 篇（可能受限）")
            print(f"   • 差异率：{difference_ratio*100:.1f}%")
            print(f"   ✅ 建议：已自动使用新接口的完整数据")
            return {
                'status': 'warning',
                'message': '旧接口数据不完整，已使用新接口',
                'new_api_count': new_api_count,
                'old_api_count': old_api_count,
                'difference_ratio': difference_ratio,
                'use_new_api': True
            }
        else:
            print(f"\n✅ 数据一致，验证通过！")
            return {
                'status': 'success',
                'message': '数据完整且一致',
                'new_api_count': new_api_count,
                'old_api_count': old_api_count,
                'difference_ratio': difference_ratio,
                'use_new_api': True
            }

    # ===== DNS & __biz 工具方法 =====

    @staticmethod
    def dns_monkey_patch():
        """Monkey-patch socket.getaddrinfo 绕过 Shadowrocket Fake DNS

        Shadowrocket 等 VPN 工具会劫持 DNS 返回 198.18.0.x 假 IP，
        导致 Python 直接请求时连接失败。此方法通过 dig 命令解析
        mp.weixin.qq.com 的真实 IP，然后 patch socket 使其直接使用真实 IP。

        Returns:
            str: 解析到的真实 IP（如 '183.2.142.78'），失败返回 None
        """
        import socket
        import subprocess

        target_host = 'mp.weixin.qq.com'

        try:
            # 使用 dig 通过公共 DNS 解析真实 IP（绕过本地 DNS 劫持）
            result = subprocess.run(
                ['dig', '+short', target_host, '@8.8.8.8'],
                capture_output=True, text=True, timeout=10
            )
            ips = [line.strip() for line in result.stdout.strip().split('\n')
                   if line.strip() and not line.strip().endswith('.')]

            if not ips:
                print("⚠️ DNS monkey-patch 失败：dig 未返回 IP")
                return None

            real_ip = ips[0]

            # 检查是否为 Fake DNS IP
            current_ip = socket.gethostbyname(target_host)
            if current_ip.startswith('198.18.'):
                print(f"🔧 检测到 Fake DNS ({current_ip})，patch 为真实 IP: {real_ip}")
            else:
                print(f"🔧 DNS monkey-patch: {target_host} → {real_ip}")

            # Patch socket.getaddrinfo
            _original_getaddrinfo = socket.getaddrinfo

            def patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
                if host == target_host:
                    return _original_getaddrinfo(real_ip, port, family, type, proto, flags)
                return _original_getaddrinfo(host, port, family, type, proto, flags)

            socket.getaddrinfo = patched_getaddrinfo
            return real_ip

        except Exception as e:
            print(f"⚠️ DNS monkey-patch 失败: {e}")
            return None

    @staticmethod
    def get_biz_from_articles(articles):
        """从文章列表中提取 __biz 参数

        从文章的 link 字段中解析 __biz 参数。通常同一公众号的所有文章
        共享相同的 __biz。

        Args:
            articles: 文章列表，每个元素需有 'link' 字段

        Returns:
            str: __biz 值，失败返回 None
        """
        from urllib.parse import urlparse, parse_qs

        for article in articles:
            link = article.get('link', '')
            if not link:
                continue

            parsed = urlparse(link)
            qs = parse_qs(parsed.query)
            biz = qs.get('__biz', [''])[0]
            if biz:
                return biz

        return None

    # ===== 阅读量 & 评论 API（V2.8 新增）=====

    # 微信读者端 User-Agent（必须包含 MQQBrowser，否则接口拒绝）
    READER_UA = (
        'Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro Build/UQ1A.240205.004) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 '
        'Chrome/57.0.2987.132 MQQBrowser/6.2 TBS/044304 Mobile Safari/537.36 '
        'MicroMessenger/8.0.44.2502(0x28002C35) NetType/WIFI Language/zh_CN'
    )

    @staticmethod
    def parse_article_url(article_url):
        """从文章 URL 提取 __biz, mid, idx, sn 参数

        支持两种 URL 格式：
        - 完整：https://mp.weixin.qq.com/s?__biz=XXX&mid=123&idx=1&sn=abc
        - 短链：https://mp.weixin.qq.com/s/SHORTID（自动解析）

        Returns:
            dict: {'__biz': ..., 'mid': ..., 'idx': ..., 'sn': ...}
        """
        from urllib.parse import urlparse, parse_qs
        import re as _re

        # 短链需要 GET 请求解析（HEAD 不会触发重定向）
        if '/s/' in article_url and '?' not in article_url:
            try:
                # 绕过系统代理（VPN工具可能拦截 mp.weixin.qq.com）
                session = requests.Session()
                session.trust_env = False
                resp = session.get(
                    article_url,
                    allow_redirects=True,
                    timeout=15,
                    verify=False,
                    headers={
                        'User-Agent': (
                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                            'AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/120.0.0.0 Safari/537.36'
                        )
                    }
                )
                # 检查重定向后的 URL 是否包含参数
                redirected = urlparse(resp.url)
                qs_r = parse_qs(redirected.query)
                if qs_r.get('__biz') and qs_r.get('mid'):
                    return {
                        '__biz': qs_r.get('__biz', [''])[0],
                        'mid': qs_r.get('mid', [''])[0],
                        'idx': qs_r.get('idx', ['1'])[0],
                        'sn': qs_r.get('sn', [''])[0].rstrip('#'),
                    }

                # 重定向后仍无参数，从 HTML JS 变量中提取
                html = resp.text
                biz_m = (_re.search(r'var\s+biz\s*=\s*["\']([^"\']+)["\']', html)
                         or _re.search(r'__biz\s*[:=]\s*["\']([^"\']+)["\']', html)
                         or _re.search(r'[?&]__biz=([A-Za-z0-9%+=]+)', html))
                mid_m = (_re.search(r'var\s+mid\s*=\s*["\']?(\d+)["\']?', html)
                         or _re.search(r'["\'\s&?]mid["\']?\s*[:=]\s*["\']?(\d+)', html))
                idx_m = (_re.search(r'var\s+idx\s*=\s*["\']?(\d+)["\']?', html)
                         or _re.search(r'["\'\s&?]idx["\']?\s*[:=]\s*["\']?(\d+)', html))
                sn_m = (_re.search(r'var\s+sn\s*=\s*["\']([^"\']+)["\']', html)
                        or _re.search(r'["\'\s&?]sn["\']?\s*[:=]\s*["\']([^"\']+)["\']', html)
                        or _re.search(r'[?&]sn=([a-f0-9]+)', html))

                if biz_m and mid_m:
                    return {
                        '__biz': biz_m.group(1),
                        'mid': mid_m.group(1),
                        'idx': idx_m.group(1) if idx_m else '1',
                        'sn': sn_m.group(1).rstrip('#') if sn_m else '',
                    }
            except Exception:
                pass

        parsed = urlparse(article_url)
        qs = parse_qs(parsed.query)

        return {
            '__biz': qs.get('__biz', [''])[0],
            'mid': qs.get('mid', [''])[0],
            'idx': qs.get('idx', ['1'])[0],
            'sn': qs.get('sn', [''])[0].rstrip('#')
        }

    # Mac WeChat User-Agent
    MAC_WECHAT_UA = (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 '
        'MicroMessenger/6.8.0(0x16080000) MacWechat/3.8.8(0x13080810) '
        'NetType/WIFI WindowsWechat'
    )

    def get_reading_stats_html(self, article_url, credentials):
        """通过 HTML 页面提取阅读数据（主方法，推荐）

        原理：带认证参数请求文章页面，服务器返回的 HTML 中嵌入了
        JavaScript 变量包含阅读量等数据。

        与 getappmsgext API 相比优势：
        - 一次请求获取所有统计数据
        - 同时提取 appmsg_token 和 comment_id（可用于后续 API 调用）
        - 不需要 appmsg_token 作为前置条件

        Args:
            article_url: 文章链接
            credentials: 读者凭证 {
                'key': ...,          # 必须
                'uin': ...,          # 必须
                'pass_ticket': ...,  # 可选但推荐
                'cookie': ...,       # 可选但推荐
            }

        Returns:
            dict: {
                'read_num': 38785,
                'like_num': 99,
                'old_like_num': 12,
                'share_count': 0,
                'comment_count': 42,
                'appmsg_token': '...',   # 从HTML提取，可用于后续API调用
                'comment_id': '...',     # 评论区ID
                'error': None
            }
        """
        import re as _re

        try:
            # 认证参数（所有请求共用）
            auth_query = {
                'key': credentials['key'],
                'uin': credentials.get('uin', ''),
                'pass_ticket': credentials.get('pass_ticket', ''),
                'scene': '27',
                'devicetype': 'UnifiedPCMac',
                'version': '6309091f',
                'lang': 'zh_CN',
                'ascene': '1',
                'wx_header': '1',
            }

            # 判断是短链（/s/XXX）还是完整链接（/s?__biz=...）
            is_short_url = '/s/' in article_url and '__biz' not in article_url

            if is_short_url:
                # 短链模式：直接在短链后追加认证参数，服务器自动解析文章
                url = article_url.split('?')[0]  # 去掉可能的尾部参数
                query = auth_query
            else:
                # 完整链接模式：提取 __biz/mid/sn 参数
                params = self.parse_article_url(article_url)
                if not params['__biz'] or not params['mid']:
                    return {'error': 'invalid_url', 'read_num': 0}
                url = f"{self.base_url}/s"
                query = {
                    '__biz': params['__biz'],
                    'mid': params['mid'],
                    'idx': params['idx'],
                    'sn': params['sn'],
                    **auth_query,
                }

            headers = {
                'User-Agent': self.MAC_WECHAT_UA,
            }
            cookie = credentials.get('cookie', '')
            if cookie:
                headers['Cookie'] = cookie

            response = requests.get(url, params=query, headers=headers,
                                     timeout=20, verify=False)
            html = response.text

            # 检查是否被拦截（key 过期或无效）
            if 'var read_num' not in html and 'read_num_new' not in html:
                # 检查是否是验证页面
                if '环境异常' in html:
                    return {'error': 'env_anomaly（环境异常，凭证可能已过期或IP异常）', 'read_num': 0}
                if '请在微信客户端打开' in html or 'verify' in html.lower():
                    return {'error': 'auth_required', 'read_num': 0}
                if 'key过期' in html or '链接已过期' in html:
                    return {'error': 'credentials_expired', 'read_num': 0}
                return {'error': 'no_stats_in_html', 'read_num': 0}

            # 提取阅读数据
            def extract_int(pattern, text, default=0):
                m = _re.search(pattern, text)
                if m:
                    try:
                        return int(m.group(1))
                    except (ValueError, IndexError):
                        pass
                return default

            read_num = extract_int(r"var\s+read_num_new\s*=\s*['\"]?(\d+)['\"]?", html)
            if read_num == 0:
                read_num = extract_int(r"var\s+read_num\s*=\s*['\"]?(\d+)['\"]?", html)
            old_like = extract_int(r"old_like_count\s*[:=]\s*['\"]?(\d+)['\"]?", html)
            like = extract_int(r"(?<!old_)like_count\s*[:=]\s*['\"]?(\d+)['\"]?", html)
            share = extract_int(r"share_count\s*[:=]\s*['\"]?(\d+)['\"]?", html)
            comment_count = extract_int(r"comment_count\s*[:=]\s*['\"]?(\d+)['\"]?", html)

            # 提取 appmsg_token（可用于后续 getcomment 等 API 调用）
            appmsg_token = ''
            m = _re.search(r"appmsg_token\s*=\s*['\"]([^'\"]+)['\"]", html)
            if m:
                appmsg_token = m.group(1)

            # 提取 comment_id
            comment_id = ''
            m = _re.search(r"var\s+comment_id\s*=\s*['\"](\d+)['\"]", html)
            if m:
                comment_id = m.group(1)

            # 从 Set-Cookie 响应头提取 cookie（可补充凭证）
            set_cookies = response.headers.get('Set-Cookie', '')

            result = {
                'read_num': read_num,
                'like_num': like,
                'old_like_num': old_like,
                'share_count': share,
                'comment_count': comment_count,
                'appmsg_token': appmsg_token,
                'comment_id': comment_id,
                'error': None,
            }

            # 如果从 HTML 中获取到了 appmsg_token，更新凭证
            if appmsg_token and not credentials.get('appmsg_token'):
                credentials['appmsg_token'] = appmsg_token

            return result

        except Exception as e:
            return {'error': str(e), 'read_num': 0}

    def get_reading_stats(self, article_url, credentials):
        """获取单篇文章的阅读数据

        Args:
            article_url: 文章链接
            credentials: 读者凭证 {
                'key': ...,          # 必须！从文章页面URL提取
                'appmsg_token': ..., # 从cookie或getappmsgext请求提取
                'cookie': ...,       # 请求cookie
                'uin': ...,          # 用户ID
                'pass_ticket': ...,  # 会话凭证
            }

        Returns:
            dict: {
                'read_num': 38785,
                'like_num': 99,         # 在看数
                'old_like_num': 12,     # 点赞数
                'friend_like_num': 3,
                'comment_enabled': 1,
                'error': None
            }
            失败时 error 字段非 None
        """
        try:
            params = self.parse_article_url(article_url)
            if not params['__biz'] or not params['mid']:
                return {'error': 'invalid_url', 'read_num': 0}

            url = f"{self.base_url}/mp/getappmsgext"
            query = {
                'appmsg_token': credentials.get('appmsg_token', ''),
                'x5': '0',
            }
            # key 参数是获取阅读量的关键
            if credentials.get('key'):
                query['key'] = credentials['key']
            if credentials.get('uin'):
                query['uin'] = credentials['uin']
            if credentials.get('pass_ticket'):
                query['pass_ticket'] = credentials['pass_ticket']

            post_data = {
                '__biz': params['__biz'],
                'mid': params['mid'],
                'idx': params['idx'],
                'sn': params['sn'],
                'is_only_read': '1',
                'is_temp_url': '0',
                'appmsg_type': '9'
            }
            headers = {
                'User-Agent': self.MAC_WECHAT_UA,
                'Referer': article_url
            }
            cookie = credentials.get('cookie', '')
            if cookie:
                headers['Cookie'] = cookie

            response = requests.post(url, params=query, data=post_data,
                                     headers=headers, timeout=15,
                                     verify=False)
            data = response.json()

            # 检查凭证是否过期
            ret = data.get('base_resp', {}).get('ret', -1)
            if ret == 302 or ret == 301:
                return {'error': 'credentials_expired', 'read_num': 0}

            stats = data.get('appmsgstat', {})
            if 'read_num' in stats:
                return {
                    'read_num': stats.get('read_num', 0),
                    'like_num': stats.get('like_num', 0),
                    'old_like_num': stats.get('old_like_num', 0),
                    'friend_like_num': stats.get('friend_like_num', 0),
                    'comment_enabled': data.get('comment_enabled', 0),
                    'error': None
                }
            else:
                return {'error': f"no_appmsgstat: ret={ret}",
                        'read_num': 0}

        except Exception as e:
            return {'error': str(e), 'read_num': 0}

    def get_batch_reading_stats(self, articles, credentials, delay=5,
                                 max_count=None, show_progress=True,
                                 method='html'):
        """批量获取文章阅读数据（自动限流）

        Args:
            articles: 文章列表，每个元素需有 'link' 字段
            credentials: 读者凭证
            delay: 请求间隔（秒），默认 5 秒
            max_count: 最大获取数量，None 表示全部
            show_progress: 是否显示进度
            method: 'html'（推荐，从页面提取）或 'api'（getappmsgext）

        Returns:
            list: 带 reading_stats 字段的文章列表
        """
        target = articles[:max_count] if max_count else articles
        total = len(target)

        method_name = 'HTML页面' if method == 'html' else 'getappmsgext API'
        if show_progress:
            print(f"📊 开始获取 {total} 篇文章的阅读数据（{method_name}，间隔{delay}秒）...")

        for i, article in enumerate(target):
            link = article.get('link', '')
            if not link:
                article['reading_stats'] = {'error': 'no_link', 'read_num': 0}
                continue

            if method == 'html':
                stats = self.get_reading_stats_html(link, credentials)
            else:
                stats = self.get_reading_stats(link, credentials)
            article['reading_stats'] = stats

            # 凭证过期，立即停止
            if stats.get('error') == 'credentials_expired':
                print("⚠️ 读者凭证已过期，停止获取")
                break

            if show_progress:
                if stats.get('error'):
                    print(f"   [{i+1}/{total}] ❌ {article.get('title', '?')[:30]}... - {stats['error']}")
                else:
                    print(f"   [{i+1}/{total}] ✅ {article.get('title', '?')[:30]}... "
                          f"- 阅读 {stats['read_num']} | 点赞👍 {stats.get('old_like_num', 0)} | 在看👀 {stats.get('like_num', 0)}")

            # 限流（最后一篇不需要等）
            if i < total - 1:
                time.sleep(delay)

        if show_progress:
            success = sum(1 for a in target if a.get('reading_stats', {}).get('error') is None)
            print(f"✅ 阅读数据获取完成：{success}/{total} 篇成功")

        return target

    def _get_comment_id(self, article_url, credentials):
        """从文章 HTML 中提取 comment_id

        Args:
            article_url: 文章链接
            credentials: 读者凭证

        Returns:
            str: comment_id，无评论功能则返回 None
        """
        import re as _re
        try:
            headers = {
                'User-Agent': self.READER_UA,
                'Cookie': credentials['cookie']
            }
            response = requests.get(article_url, headers=headers, timeout=15,
                                     verify=False)

            # 主要匹配模式
            match = _re.search(r'var\s+comment_id\s*=\s*["\'](\d+)["\']', response.text)
            if match:
                return match.group(1)

            # 备用模式
            match = _re.search(r'comment_id\s*=\s*["\'](\d+)["\']', response.text)
            if match:
                return match.group(1)

            return None
        except Exception as e:
            print(f"⚠️ 获取 comment_id 失败: {e}")
            return None

    def get_comments(self, article_url, credentials, comment_id=None, limit=100):
        """获取文章精选评论

        Args:
            article_url: 文章链接
            credentials: 读者凭证
            comment_id: 评论区 ID（不提供则自动从文章提取）
            limit: 最大评论数

        Returns:
            dict: {
                'comments': [
                    {
                        'nick_name': '昵称',
                        'content': '评论内容',
                        'like_num': 3,
                        'create_time': 1520098511,
                        'is_top': 0,
                        'replies': [{'content': '作者回复', ...}]
                    }
                ],
                'total': 22,
                'error': None
            }
        """
        try:
            params = self.parse_article_url(article_url)
            if not params['__biz']:
                return {'comments': [], 'total': 0, 'error': 'invalid_url'}

            # 自动获取 comment_id
            if not comment_id:
                comment_id = self._get_comment_id(article_url, credentials)
                if not comment_id:
                    return {'comments': [], 'total': 0, 'error': 'no_comment_id（文章可能未开启评论）'}

            url = f"{self.base_url}/mp/appmsg_comment"
            query = {
                'action': 'getcomment',
                '__biz': params['__biz'],
                'appmsgid': params['mid'],
                'idx': params['idx'],
                'comment_id': comment_id,
                'offset': 0,
                'limit': limit,
                'appmsg_token': credentials['appmsg_token']
            }
            headers = {
                'User-Agent': self.READER_UA,
                'Cookie': credentials['cookie'],
                'Referer': article_url
            }

            response = requests.get(url, params=query, headers=headers,
                                     timeout=15, verify=False)
            data = response.json()

            if data.get('base_resp', {}).get('ret') == 0:
                elected = data.get('elected_comment', [])
                comments = []
                for c in elected:
                    comment = {
                        'nick_name': c.get('nick_name', ''),
                        'content': c.get('content', ''),
                        'like_num': c.get('like_num', 0),
                        'create_time': c.get('create_time', 0),
                        'is_top': c.get('is_top', 0),
                        'logo_url': c.get('logo_url', ''),
                        'replies': []
                    }
                    # 提取作者回复
                    reply_list = c.get('reply', {}).get('reply_list', [])
                    for r in reply_list:
                        comment['replies'].append({
                            'content': r.get('content', ''),
                            'create_time': r.get('create_time', 0),
                            'reply_like_num': r.get('reply_like_num', 0)
                        })
                    comments.append(comment)

                total = data.get('elected_comment_total_cnt', len(comments))
                print(f"✅ 获取到 {len(comments)} 条精选评论（共 {total} 条）")
                return {'comments': comments, 'total': total, 'error': None}

            elif data.get('base_resp', {}).get('ret') == 302:
                return {'comments': [], 'total': 0, 'error': 'credentials_expired'}
            else:
                err = data.get('base_resp', {}).get('errmsg', '未知错误')
                return {'comments': [], 'total': 0, 'error': err}

        except Exception as e:
            return {'comments': [], 'total': 0, 'error': str(e)}


def main():
    """测试函数"""
    api = WeChatMPAPI()

    # 测试登录
    if not api.is_logged_in():
        print("需要登录")
        if api.login():
            print("登录成功")
        else:
            print("登录失败")
            return

    # 测试搜索
    accounts = api.search_account("婷在路上的日子")
    if accounts:
        print("\n搜索结果：")
        for acc in accounts:
            print(f"- {acc['nickname']} (fakeid: {acc['fakeid']})")

        # 测试获取文章
        fakeid = accounts[0]['fakeid']
        articles = api.get_all_articles(fakeid, max_count=10)
        print(f"\n获取到 {len(articles)} 篇文章")
        for article in articles[:5]:
            print(f"- {article['title']}")


if __name__ == '__main__':
    main()

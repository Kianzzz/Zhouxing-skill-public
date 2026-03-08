#!/usr/bin/env python3
"""
文章提取器 - 多方式降级策略
支持 Firecrawl > HTTP 请求 > WebFetch > Playwright
"""

import sys
import json
import re
from datetime import datetime
from pathlib import Path


class ArticleExtractor:
    """文章提取器，实现多方式降级策略"""

    def __init__(self):
        # 方法优先级（根据实际测试结果调整）:
        # 1. HTTP请求 - 最快最稳定（网络调整后）
        # 2. WebFetch - Claude内置，缓存好
        # 3. Firecrawl - 专业服务，但可能走海外
        # 4. Playwright - 最慢，仅作最后备选
        self.methods = [
            ('HTTP请求', self._extract_with_http),
            ('WebFetch', self._extract_with_webfetch),
            ('Firecrawl', self._extract_with_firecrawl),
            ('Playwright', self._extract_with_playwright)
        ]

    def extract(self, url, cookie=None):
        """提取文章内容，按优先级尝试不同方式

        Args:
            url: 文章链接
            cookie: 可选的 Cookie 字符串

        Returns:
            dict: 提取结果
                {
                    'success': True/False,
                    'method': '使用的方法',
                    'title': '标题',
                    'author': '作者',
                    'source': '来源',
                    'content': '正文',
                    'date': '发布日期',
                    'error': '错误信息（如果失败）'
                }
        """
        print(f"🔍 开始提取文章：{url}")
        print(f"📋 将按以下顺序尝试：")
        for i, (name, _) in enumerate(self.methods, 1):
            print(f"   {i}. {name}")
        print()

        for method_name, method_func in self.methods:
            print(f"⏳ 尝试使用 {method_name}...")

            try:
                # HTTP 请求方式支持 Cookie
                if method_name == 'HTTP请求':
                    result = method_func(url, cookie=cookie)
                else:
                    result = method_func(url)

                if result and result.get('success'):
                    print(f"✅ {method_name} 成功！")
                    result['method'] = method_name
                    return result
                else:
                    error = result.get('error', '未知错误') if result else '返回空结果'
                    print(f"❌ {method_name} 失败: {error}")

            except Exception as e:
                print(f"❌ {method_name} 出错: {e}")
                continue

        # 所有方法都失败
        return {
            'success': False,
            'error': '所有提取方式都失败了'
        }

    def _extract_with_firecrawl(self, url):
        """方式1: 使用 Firecrawl（需要 MCP 工具支持）"""
        # 这个方法需要通过 Claude 调用 MCP 工具
        # 这里返回一个指示，让 Claude 知道需要使用 Firecrawl
        return {
            'success': False,
            'error': '需要在 Claude 中调用 mcp__firecrawl__firecrawl_scrape 工具'
        }

    def _extract_with_http(self, url, cookie=None):
        """方式2: 使用 HTTP 请求直接获取

        Args:
            url: 文章链接
            cookie: 可选的 Cookie 字符串，用于绕过安全验证
        """
        try:
            import requests
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            from bs4 import BeautifulSoup

            # 设置请求头（模拟微信浏览器）
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.38(0x18002633) NetType/WIFI Language/zh_CN',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Referer': 'https://mp.weixin.qq.com/',
            }

            # 如果提供了 Cookie，添加到请求头
            if cookie:
                headers['Cookie'] = cookie
                print("   使用提供的 Cookie")

            # 发送请求（verify=False 避免 Shadowrocket TLS MITM 导致的 SSL 错误）
            response = requests.get(url, headers=headers, timeout=30, allow_redirects=True, verify=False)
            response.raise_for_status()

            # 检查是否遇到安全验证
            if '安全验证' in response.text or '验证码' in response.text:
                return {
                    'success': False,
                    'error': '遇到微信安全验证，需要在微信客户端打开'
                }

            # 解析 HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取标题
            title = None
            title_elem = soup.select_one('#activity-name, .rich_media_title')
            if title_elem:
                title = title_elem.get_text(strip=True)

            # 提取作者
            author = None
            author_elem = soup.select_one('#js_name, .rich_media_meta_nickname')
            if author_elem:
                author = author_elem.get_text(strip=True)

            # 提取发布时间
            # 优先从 JavaScript 变量中提取时间戳
            date = None
            ct_match = re.search(r'var\s+ct\s*=\s*["\']?(\d{10,})["\']?', response.text)
            if ct_match:
                try:
                    timestamp = int(ct_match.group(1))
                    date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
                except:
                    pass

            # 如果没找到时间戳，尝试从元素中提取
            if not date:
                date_elem = soup.select_one('#publish_time, .rich_media_meta_text')
                if date_elem:
                    date_text = date_elem.get_text(strip=True)
                    # 尝试解析日期
                    date = self._parse_date(date_text)

            # 提取正文
            content_elem = soup.select_one('#js_content, .rich_media_content')
            if not content_elem:
                return {
                    'success': False,
                    'error': '未找到文章内容'
                }

            # 移除图片、视频等媒体元素
            for tag in content_elem.select('img, video, iframe, script, style'):
                tag.decompose()

            # 提取纯文本内容
            content = self._clean_content(content_elem)

            if not content:
                return {
                    'success': False,
                    'error': '提取的内容为空'
                }

            return {
                'success': True,
                'title': title or '无标题',
                'author': author or '未知作者',
                'source': '微信公众号',
                'content': content,
                'date': date or datetime.now().strftime('%Y-%m-%d'),
                'url': url
            }

        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': '请求超时（网络可能较慢）'
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'HTTP 请求失败: {e}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'解析失败: {e}'
            }

    def _extract_with_webfetch(self, url):
        """方式3: 使用 WebFetch（需要 Claude 工具支持）"""
        # 这个方法需要通过 Claude 调用 WebFetch 工具
        return {
            'success': False,
            'error': '需要在 Claude 中调用 WebFetch 工具'
        }

    def _extract_with_playwright(self, url):
        """方式4: 使用 Playwright（需要 MCP 工具支持）"""
        # 这个方法需要通过 Claude 调用 Playwright 工具
        return {
            'success': False,
            'error': '需要在 Claude 中调用 Playwright 工具'
        }

    def _clean_content(self, element):
        """清理内容，提取纯文本"""
        # 获取所有段落
        paragraphs = []

        for p in element.find_all(['p', 'section', 'div']):
            text = p.get_text(strip=True)
            if text and len(text) > 10:  # 过滤太短的段落
                paragraphs.append(text)

        return '\n\n'.join(paragraphs)

    def _parse_date(self, date_text):
        """解析日期字符串"""
        try:
            # 尝试各种日期格式
            patterns = [
                r'(\d{4})-(\d{2})-(\d{2})',
                r'(\d{4})年(\d{1,2})月(\d{1,2})日',
            ]

            for pattern in patterns:
                match = re.search(pattern, date_text)
                if match:
                    year, month, day = match.groups()
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

            return None
        except:
            return None

    def save_to_markdown(self, article_data, output_dir):
        """保存为 Markdown 文件

        Args:
            article_data: 文章数据
            output_dir: 输出目录

        Returns:
            str: 保存的文件路径
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        date = article_data.get('date', datetime.now().strftime('%Y-%m-%d'))
        title = article_data.get('title', '无标题')
        author = article_data.get('author', '')

        # 清理文件名中的特殊字符
        safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)[:50]

        if author:
            safe_author = re.sub(r'[<>:"/\\|?*]', '_', author)[:20]
            filename = f"{date}_{safe_title}-{safe_author}.md"
        else:
            filename = f"{date}_{safe_title}.md"

        filepath = output_dir / filename

        # 生成 Markdown 内容
        markdown = self._generate_markdown(article_data)

        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown)

        return str(filepath)

    def _generate_markdown(self, article_data):
        """生成 Markdown 格式"""
        lines = []

        # 添加 YAML frontmatter
        lines.append('---')
        lines.append(f"title: {article_data.get('title', '无标题')}")
        lines.append(f"author: {article_data.get('author', '未知作者')}")
        lines.append(f"date: {article_data.get('date', '')}")
        lines.append(f"source: {article_data.get('source', '微信公众号')}")
        lines.append(f"url: {article_data.get('url', '')}")

        # 如果有元数据，添加
        if 'read_num' in article_data:
            lines.append(f"read_num: {article_data['read_num']}")
        if 'like_num' in article_data:
            lines.append(f"like_num: {article_data['like_num']}")

        lines.append(f"extracted_by: {article_data.get('method', 'unknown')}")
        lines.append('---')
        lines.append('')

        # 添加标题
        lines.append(f"# {article_data.get('title', '无标题')}")
        lines.append('')

        # 添加元信息
        lines.append(f"**作者**：{article_data.get('author', '未知作者')}")
        lines.append(f"**来源**：{article_data.get('source', '微信公众号')}")
        lines.append(f"**链接**：{article_data.get('url', '')}")
        lines.append('')
        lines.append('---')
        lines.append('')

        # 添加正文
        lines.append(article_data.get('content', ''))

        return '\n'.join(lines)


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='微信文章提取工具（支持多方式降级）')
    parser.add_argument('url', help='文章链接')
    parser.add_argument('output_dir', nargs='?', default='./output', help='输出目录（默认: ./output）')
    parser.add_argument('--cookie', help='Cookie 字符串（用于绕过安全验证）')

    args = parser.parse_args()

    extractor = ArticleExtractor()

    # 提取文章
    result = extractor.extract(args.url, cookie=args.cookie)

    if result['success']:
        # 保存为 Markdown
        filepath = extractor.save_to_markdown(result, args.output_dir)
        print(f"\n✅ 成功保存到：{filepath}")
        print(f"   使用方法：{result['method']}")
    else:
        print(f"\n❌ 提取失败：{result.get('error', '未知错误')}")
        print(f"\n💡 建议：")
        print(f"   1. 使用批量搜索模式（更可靠）")
        print(f"   2. 从浏览器复制 Cookie 后重试：")
        print(f"      python3 {sys.argv[0]} <URL> --cookie \"your_cookie\"")
        sys.exit(1)


if __name__ == '__main__':
    main()

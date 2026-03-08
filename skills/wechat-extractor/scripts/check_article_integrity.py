#!/usr/bin/env python3
"""
文章完整性检查器
用于验证提取的文章是否完整、是否被截断等
"""

import json
import re
from pathlib import Path


class ArticleIntegrityChecker:
    """检查文章完整性的工具类"""

    def __init__(self):
        # 最小字符数：文章至少要有这么多字符才认为是有内容的
        self.min_content_length = 100
        # 警告阈值：字符数少于这个值会给出警告
        self.warning_threshold = 500

    def check_article(self, article_data):
        """检查单篇文章的完整性

        Args:
            article_data: dict，包含以下字段：
                - title: 标题
                - author: 作者
                - content: 正文内容
                - source: 来源（可选）
                - url: 链接（可选）

        Returns:
            dict: 检查结果
                {
                    'is_complete': bool,  # 是否完整
                    'status': str,        # 'complete', 'warning', 'error'
                    'message': str,       # 简短说明
                    'details': {
                        'title_ok': bool,
                        'author_ok': bool,
                        'content_length': int,
                        'content_ok': bool,
                        'paragraph_count': int,
                        'common_end_patterns': bool
                    }
                }
        """
        result = {
            'is_complete': True,
            'status': 'complete',
            'message': '文章完整 ✓',
            'details': {}
        }

        # 检查标题
        title = article_data.get('title', '').strip()
        result['details']['title_ok'] = len(title) > 0
        if not result['details']['title_ok']:
            result['is_complete'] = False
            result['status'] = 'error'
            result['message'] = '❌ 缺少标题'
            return result

        # 检查作者
        author = article_data.get('author', '').strip()
        result['details']['author_ok'] = len(author) > 0

        # 检查正文内容
        content = article_data.get('content', '').strip()
        content_length = len(content)
        result['details']['content_length'] = content_length
        result['details']['content_ok'] = content_length >= self.min_content_length

        if content_length < self.min_content_length:
            result['is_complete'] = False
            result['status'] = 'error'
            result['message'] = f'❌ 内容过短 ({content_length}字符，最少需要{self.min_content_length}字符)'
            return result

        # 统计段落数
        paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
        result['details']['paragraph_count'] = len(paragraphs)

        # 检查是否有常见的末尾标记（表示文章可能被截断）
        incomplete_patterns = [
            r'\.\.\.+\s*$',  # 省略号结尾
            r'【未完待续】',  # 未完待续标记
            r'阅读全文',      # 阅读全文链接
            r'继续阅读',      # 继续阅读链接
        ]

        has_incomplete_pattern = False
        for pattern in incomplete_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                has_incomplete_pattern = True
                break

        result['details']['common_end_patterns'] = has_incomplete_pattern

        # 根据各项检查结果综合判断
        if has_incomplete_pattern:
            result['is_complete'] = False
            result['status'] = 'warning'
            result['message'] = '⚠️  可能不完整（检测到常见截断标记）'
        elif content_length < self.warning_threshold:
            result['status'] = 'warning'
            result['message'] = f'⚠️  内容较短 ({content_length}字符，建议人工检查)'
        else:
            result['message'] = f'✅ 文章完整 ({content_length}字符，{len(paragraphs)}段落)'

        return result

    def format_check_message(self, check_result):
        """格式化检查结果为用户友好的消息"""
        status = check_result['status']
        title = ''

        if status == 'complete':
            return f"✅ {check_result['message']}"
        elif status == 'warning':
            return f"⚠️  {check_result['message']}"
        else:  # error
            return f"❌ {check_result['message']}"

    def batch_check(self, articles_list):
        """批量检查多篇文章

        Args:
            articles_list: list of dict，每个元素为一篇文章

        Returns:
            dict: 批量检查结果
                {
                    'total': int,          # 总数
                    'complete': int,       # 完整数
                    'warning': int,        # 警告数
                    'error': int,          # 错误数
                    'results': [...]       # 详细检查结果
                }
        """
        results = {
            'total': len(articles_list),
            'complete': 0,
            'warning': 0,
            'error': 0,
            'results': []
        }

        for article in articles_list:
            check_result = self.check_article(article)
            results['results'].append(check_result)

            status = check_result['status']
            if status == 'complete':
                results['complete'] += 1
            elif status == 'warning':
                results['warning'] += 1
            else:  # error
                results['error'] += 1

        return results


def check_article_file(file_path):
    """检查本地保存的 Markdown 文件是否完整

    Args:
        file_path: Markdown 文件路径

    Returns:
        dict: 检查结果
    """
    file_path = Path(file_path)
    if not file_path.exists():
        return {
            'is_complete': False,
            'status': 'error',
            'message': f'❌ 文件不存在: {file_path}'
        }

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 简单的 Markdown 文件完整性检查
    lines = content.split('\n')
    file_size = len(content)

    # 检查是否有标题
    has_title = any(line.startswith('#') for line in lines)

    # 检查是否有足够的内容
    non_empty_lines = len([l for l in lines if l.strip()])

    result = {
        'is_complete': True,
        'status': 'complete',
        'message': f'✅ 文件完整 ({file_size}字节，{non_empty_lines}行)',
        'details': {
            'file_size': file_size,
            'non_empty_lines': non_empty_lines,
            'has_title': has_title
        }
    }

    # 警告检查
    if file_size < 500:
        result['status'] = 'warning'
        result['message'] = f'⚠️  文件较小 ({file_size}字节)'
    elif not has_title:
        result['status'] = 'warning'
        result['message'] = '⚠️  缺少 Markdown 标题'

    return result


# 简单的命令行使用示例
if __name__ == '__main__':
    # 示例：检查一篇文章
    checker = ArticleIntegrityChecker()

    sample_article = {
        'title': '测试文章标题',
        'author': '测试作者',
        'content': '这是一篇测试文章。' * 50,  # 重复内容以达到最小长度
        'source': '测试公众号'
    }

    result = checker.check_article(sample_article)
    print('检查结果:', json.dumps(result, ensure_ascii=False, indent=2))
    print('简短消息:', checker.format_check_message(result))

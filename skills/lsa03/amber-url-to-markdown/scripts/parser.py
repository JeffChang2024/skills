#!/usr/bin/env python3
"""
Amber Url to Markdown - HTML 解析与 Markdown 转换模块（V3.1 优化版）
负责 HTML 清理、优化、转换为 Markdown 格式，支持特殊元素保留（LaTeX、代码块）

作者：小文
时间：2026-03-24
版本：V3.1
"""

from bs4 import BeautifulSoup
from markdownify import markdownify as md
from typing import Optional, List, Tuple
import re

# 导入配置
import sys
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
from config import get_convert_config


# ============================================================================
# 特殊元素提取
# ============================================================================

def extract_special_elements(html: str) -> Tuple[str, List[Tuple[str, str]], List[Tuple[str, str, str]]]:
    """
    提取特殊元素（代码块、LaTeX 公式），避免转换丢失
    
    Args:
        html: 原始 HTML
    
    Returns:
        Tuple: (清理后的 HTML, 代码块列表 [(key, code), ...], LaTeX 列表 [(key, latex, type), ...])
    """
    code_blocks = []
    latex_blocks = []
    
    # 1. 提取<pre><code>代码块
    code_pattern = re.compile(r"<pre.*?><code.*?>(.*?)</code></pre>", re.DOTALL | re.IGNORECASE)
    
    def replace_code(match):
        code = match.group(1)
        code_key = f"__CODE_{len(code_blocks)}__"
        code_blocks.append((code_key, code))
        return code_key
    
    html = code_pattern.sub(replace_code, html)
    
    # 2. 提取 LaTeX 公式（$...$ / $$...$$）
    latex_patterns = [
        (r"\$\$(.*?)\$\$", "BLOCK"),   # 块级公式
        (r"\$(.*?)\$", "INLINE"),      # 行内公式
    ]
    
    for pattern, typ in latex_patterns:
        def replace_latex(match, typ=typ):
            latex = match.group(1)
            latex_key = f"__LATEX_{len(latex_blocks)}__"
            latex_blocks.append((latex_key, latex, typ))
            return latex_key
        
        html = re.sub(pattern, replace_latex, html, flags=re.DOTALL)
    
    return html, code_blocks, latex_blocks


def restore_special_elements(
    markdown_text: str,
    code_blocks: List[Tuple[str, str]],
    latex_blocks: List[Tuple[str, str, str]]
) -> str:
    """
    还原特殊元素到 Markdown 中
    
    Args:
        markdown_text: 基础转换后的 Markdown
        code_blocks: 代码块列表
        latex_blocks: LaTeX 公式列表
    
    Returns:
        str: 还原特殊元素后的 Markdown
    """
    # 1. 还原代码块
    for code_key, code in code_blocks:
        # 清理代码块中的多余空白
        code = re.sub(r"^\s+", "", code)
        code = re.sub(r"\s+$", "", code)
        markdown_text = markdown_text.replace(code_key, f"\n```\n{code}\n```\n")
    
    # 2. 还原 LaTeX 公式
    for latex_key, latex, typ in latex_blocks:
        if typ == "INLINE":
            # 行内公式
            markdown_text = markdown_text.replace(latex_key, f"${latex}$")
        else:
            # 块级公式
            markdown_text = markdown_text.replace(latex_key, f"\n$$\n{latex}\n$$\n")
    
    return markdown_text


# ============================================================================
# HTML 优化函数
# ============================================================================

def optimize_html_for_markdown(html: str) -> str:
    """
    优化 HTML 以便 markdownify 正确处理代码块
    
    微信文章使用 <span>三重引号</span> 来表示代码块边界
    将其转换为 <pre><code>...</code></pre> 格式
    
    Args:
        html: 原始 HTML
    
    Returns:
        str: 优化后的 HTML
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    # 查找所有包含三重引号的 span 标签
    quote_spans = []
    for span in soup.find_all('span'):
        if span.get_text(strip=True) == '"""':
            quote_spans.append(span)
    
    # 成对处理三重引号标签
    if len(quote_spans) >= 2:
        # 每两个 """ 为一对，包裹中间的内容
        for i in range(0, len(quote_spans) - 1, 2):
            start_span = quote_spans[i]
            end_span = quote_spans[i + 1]
            
            # 收集两个 """ 之间的所有内容
            content_elements = []
            current = start_span.next_sibling
            while current and current != end_span:
                content_elements.append(current)
                current = current.next_sibling
            
            # 创建 <pre><code> 标签包裹内容
            if content_elements:
                code_wrapper = soup.new_tag('pre')
                code_inner = soup.new_tag('code')
                code_wrapper.append(code_inner)
                
                # 将内容移动到 code 标签内
                for elem in content_elements:
                    if hasattr(elem, 'extract'):
                        code_inner.append(elem.extract())
                    else:
                        code_inner.append(soup.new_string(str(elem)))
                
                # 替换起始 """ 为 pre 标签，删除结束 """
                start_span.replace_with(code_wrapper)
                end_span.extract()
    
    return str(soup)


def clean_html(html: str) -> str:
    """
    清理 HTML，移除无关标签和广告
    
    Args:
        html: 原始 HTML
    
    Returns:
        str: 清理后的 HTML
    """
    cfg = get_convert_config()
    soup = BeautifulSoup(html, 'html.parser')
    
    # 移除配置的无关标签
    for tag in soup.find_all(cfg.STRIP_TAGS):
        tag.decompose()
    
    # 移除广告（常见广告类名）
    ad_patterns = [
        r"ad-",
        r"_ad_",
        r"ads-",
        r"banner",
        r"promotion",
        r"sponsor",
    ]
    
    for tag in soup.find_all(class_=True):
        class_str = " ".join(tag.get('class', []))
        for pattern in ad_patterns:
            if re.search(pattern, class_str, re.IGNORECASE):
                tag.decompose()
                break
    
    # 移除 style 标签中的广告
    for style_tag in soup.find_all('style'):
        style_tag.decompose()
    
    # 合并连续空白
    html_str = str(soup)
    html_str = re.sub(r"\s+", " ", html_str)
    
    return html_str


def optimize_for_tables(html: str) -> str:
    """
    优化 HTML 表格，确保 Markdown 正确转换
    
    Args:
        html: 原始 HTML
    
    Returns:
        str: 优化后的 HTML
    """
    cfg = get_convert_config()
    
    if not cfg.KEEP_TABLES:
        return html
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # 处理表格
    for table in soup.find_all('table'):
        # 确保表格有 thead 和 tbody
        if not table.find('thead'):
            # 尝试从第一行创建 thead
            first_row = table.find('tr')
            if first_row:
                thead = soup.new_tag('thead')
                thead.append(first_row.extract())
                table.insert(0, thead)
        
        # 确保表格有 tbody
        if not table.find('tbody'):
            tbody = soup.new_tag('tbody')
            for row in table.find_all('tr'):
                tbody.append(row.extract())
            table.append(tbody)
    
    return str(soup)


# ============================================================================
# HTML 转 Markdown
# ============================================================================

def html_to_markdown(
    html: str,
    heading_style: str = None,
    bullets: str = None,
    code_language: str = None,
    strip_tags: Optional[list] = None
) -> str:
    """
    自定义 HTML 转 Markdown 规则，提升格式准确性，支持特殊元素保留
    
    Args:
        html: 原始 HTML 字符串
        heading_style: 标题样式（"ATX"=# 标题，"UNDERLINED"=下划线）
        bullets: 无序列表符号（"-"、"*"、"+"）
        code_language: 代码块默认语言
        strip_tags: 要移除的标签列表
    
    Returns:
        str: 格式化后的 Markdown 内容
    """
    cfg = get_convert_config()
    
    # 使用配置默认值
    if heading_style is None:
        heading_style = cfg.HEADING_STYLE
    if bullets is None:
        bullets = cfg.BULLETS
    if code_language is None:
        code_language = cfg.CODE_LANGUAGE
    if strip_tags is None:
        strip_tags = cfg.STRIP_TAGS
    
    if not html or not html.strip():
        return ""
    
    # 1. 提取特殊元素（代码块、LaTeX）
    if cfg.KEEP_CODE_BLOCK or cfg.KEEP_LATEX:
        html, code_blocks, latex_blocks = extract_special_elements(html)
    else:
        code_blocks, latex_blocks = [], []
    
    # 2. 优化 HTML
    html = optimize_html_for_markdown(html)
    html = optimize_for_tables(html)
    html = clean_html(html)
    
    # 3. 转换为 Markdown
    markdown_text = md(
        html,
        heading_style=heading_style,      # 标题用 #
        bullets=bullets,                  # 无序列表用 -
        convert_ol=True,                  # 保留有序列表
        image_alt_text=True,              # 保留图片 alt 文本
        linkify=True,                     # 自动识别纯文本链接
        strip=strip_tags,                 # 剔除脚本/样式标签
        escape_underscores=cfg.ESCAPE_UNDERSCORES,  # 禁用下划线转义
        escape_misc=cfg.ESCAPE_MISC,      # 禁用其他字符转义
        code_language=code_language,      # 代码块默认语言
        newline_style="SPACES",           # 使用空格作为换行
    )
    
    # 4. 还原特殊元素
    if code_blocks or latex_blocks:
        markdown_text = restore_special_elements(markdown_text, code_blocks, latex_blocks)
    
    # 5. 后处理
    # 移除空的代码块行
    markdown_text = re.sub(r'```\s*\n\s*```', '', markdown_text)
    
    # 移除多余空行（保留最多 2 个连续空行）
    markdown_text = re.sub(r'\n{4,}', '\n\n', markdown_text)
    
    # 清理每行首尾空格
    lines = [line.rstrip() for line in markdown_text.splitlines() if line.rstrip()]
    markdown_text = '\n\n'.join(lines)
    
    return markdown_text


def extract_title_from_html(html: str) -> Optional[str]:
    """
    从 HTML 中提取标题
    
    Args:
        html: 原始 HTML
    
    Returns:
        str: 标题（如果找到）
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    # 尝试多种方式提取标题
    # 1. 从 title 标签
    title_tag = soup.find("title")
    if title_tag:
        title = title_tag.get_text().strip()
        if title and len(title) < 200:
            return title
    
    # 2. 从 meta[property='og:title']
    meta_title = soup.find("meta", property="og:title")
    if meta_title and meta_title.get("content"):
        title = meta_title.get("content").strip()
        if title and len(title) < 200:
            return title
    
    # 3. 从 h1 标签
    h1_tag = soup.find("h1")
    if h1_tag:
        title = h1_tag.get_text().strip()
        if title and len(title) < 200:
            return title
    
    # 4. 从第一个 h2 标签
    h2_tag = soup.find("h2")
    if h2_tag:
        title = h2_tag.get_text().strip()
        if title and len(title) < 200:
            return title
    
    return None


# ============================================================================
# 测试入口
# ============================================================================

if __name__ == "__main__":
    # 简单测试
    test_html = """
    <html>
        <head><title>测试页面</title></head>
        <body>
            <h1>主标题</h1>
            <p>这是一个<strong>测试</strong>段落。</p>
            <pre><code>print("Hello World")</code></pre>
            <p>行内公式：$E=mc^2$</p>
            <p>块级公式：$$\\int_0^1 x dx$$</p>
        </body>
    </html>
    """
    
    print("原始 HTML:")
    print(test_html)
    print("\n" + "="*60 + "\n")
    
    # 提取标题
    title = extract_title_from_html(test_html)
    print(f"提取标题：{title}")
    print("\n" + "="*60 + "\n")
    
    # 转换为 Markdown
    md_text = html_to_markdown(test_html)
    print("转换后的 Markdown:")
    print(md_text)

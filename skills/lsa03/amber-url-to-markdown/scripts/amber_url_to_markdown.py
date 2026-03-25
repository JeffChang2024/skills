#!/usr/bin/env python3
"""
Amber Url to Markdown - URL 转 Markdown 工具（V3.0 重构版）
支持多网站识别和定制化抓取策略

降级策略：
1. Playwright 无头浏览器（首选 - 支持所有网站）
2. Scrapling（备选 - 支持所有网站）
3. 第三方 API（保底 - 仅微信）

作者：小文
创建时间：2026-03-22
更新时间：2026-03-24
版本：V3.0
"""

import sys
import os
import re
from datetime import datetime
import time

# 添加路径
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

# 导入本地模块
from fetcher import fetch_url_content, is_allowed_by_robots, batch_fetch_urls, fetch_dynamic_content
from parser import html_to_markdown, extract_title_from_html, optimize_html_for_markdown, clean_html
from utils import (
    sanitize_title, format_timestamp, format_datetime,
    create_output_directories, download_image, save_markdown_file,
    create_logger, DEFAULT_OUTPUT_DIR
)


# ============================================================================
# 方案一：Playwright 无头浏览器（支持多网站）
# ============================================================================

def fetch_with_playwright(url: str, output_dir: str = DEFAULT_OUTPUT_DIR, download_images: bool = True):
    """
    方案一：Playwright 无头浏览器（首选方案）
    支持多网站识别和定制化抓取
    
    Args:
        url: 目标 URL
        output_dir: 输出目录
        download_images: 是否下载图片
    
    Returns:
        dict: 抓取结果（包含标题、文件路径、图片数等）
        str: 错误信息（失败时）
    """
    from playwright.sync_api import sync_playwright
    from bs4 import BeautifulSoup
    from url_handler import get_url_config
    
    log = create_logger("Playwright")
    log("=" * 60, "START")
    
    # 识别链接类型并获取配置
    config = get_url_config(url)
    log(f"方案一：Playwright 无头浏览器", "START")
    log(f"链接类型：{config.name}", "INFO")
    log(f"开始抓取：{url}", "START")
    
    total_start = time.time()
    browser = None
    
    try:
        # 创建目录
        os.makedirs(output_dir, exist_ok=True)
        # 【重要】在开始处理时就生成时间戳，后续所有地方都使用同一个时间戳
        timestamp = format_timestamp()
        log(f"时间戳：{timestamp}", "INFO")
        
        # 图片目录
        images_dir = None
        if download_images:
            images_dir = os.path.join(output_dir, "images", f"knowledge_{timestamp}")
            os.makedirs(images_dir, exist_ok=True)
        
        image_count = 0
        
        with sync_playwright() as p:
            log("启动浏览器...", "BROWSER")
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled"
                ]
            )
            log("浏览器启动成功", "BROWSER")
            
            context = browser.new_context(
                user_agent=config.headers.get("User-Agent", "Mozilla/5.0"),
                viewport={"width": 1920, "height": 1080},
                extra_http_headers=config.headers,
            )
            log("上下文创建成功", "BROWSER")
            
            page = context.new_page()
            log("页面创建成功", "BROWSER")
            
            log(f"访问 URL...", "NAVIGATE")
            nav_start = time.time()
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                nav_elapsed = time.time() - nav_start
                log(f"页面加载成功，耗时={nav_elapsed:.1f}s", "NAVIGATE")
            except Exception as e:
                log(f"页面加载失败：{str(e)[:100]}", "ERROR")
                raise
            
            if config.needs_js:
                log(f"等待页面渲染...", "NAVIGATE")
                try:
                    # 等待网络空闲（最多 10 秒）
                    page.wait_for_load_state("networkidle", timeout=10000)
                    log("页面渲染完成（networkidle）", "NAVIGATE")
                except Exception as e:
                    # 超时则继续，使用固定等待作为后备
                    log(f"networkidle 超时，使用固定等待：{str(e)[:50]}", "WARN")
                    time.sleep(config.wait_time)
                    log(f"固定等待完成 ({config.wait_time}s)", "NAVIGATE")
            
            # 提取标题（优化版）
            log("提取标题...", "EXTRACT")
            title = None
            
            # 1. 尝试 meta 标签
            for selector in config.title_selectors:
                if selector.startswith("meta["):
                    try:
                        meta = page.query_selector(selector)
                        if meta:
                            title = meta.get_attribute("content")
                            if title and len(title.strip()) > 0:
                                log(f"标题选择器成功：{selector}", "EXTRACT")
                                break
                    except Exception as e:
                        log(f"标题选择器失败 {selector}: {str(e)[:50]}", "WARN")
            
            # 2. 尝试 HTML 元素
            if not title:
                for selector in config.title_selectors:
                    if not selector.startswith("meta["):
                        try:
                            element = page.query_selector(selector)
                            if element:
                                title_text = element.inner_text().strip()
                                if title_text and len(title_text) < 200:
                                    title = title_text
                                    log(f"标题选择器成功：{selector}", "EXTRACT")
                                    break
                        except Exception as e:
                            log(f"标题选择器失败 {selector}: {str(e)[:50]}", "WARN")
            
            # 3. 使用页面标题
            if not title:
                title = page.title()
                log(f"使用页面标题：{title}", "EXTRACT")
            
            # 4. 最后尝试从正文提取第一个 h1/h2
            if not title or len(title.strip()) == 0:
                try:
                    h1 = page.query_selector("h1")
                    if h1:
                        title = h1.inner_text().strip()
                        log("从 h1 标签提取标题", "EXTRACT")
                    else:
                        h2 = page.query_selector("h2")
                        if h2:
                            title = h2.inner_text().strip()
                            log("从 h2 标签提取标题", "EXTRACT")
                except:
                    pass
            
            # 5. 如果还是没有标题，使用默认值
            if not title or len(title.strip()) == 0:
                title = "未命名文章"
                log("使用默认标题", "WARN")
            
            # 清理标题（去除多余空格和换行）
            title = re.sub(r'\s+', ' ', title)[:100]
            log(f"标题：{title}", "EXTRACT")
            
            # 查找正文
            log("查找正文...", "EXTRACT")
            content_element = None
            for selector in config.content_selectors:
                try:
                    content_element = page.query_selector(selector)
                    if content_element:
                        log(f"正文选择器成功：{selector}", "EXTRACT")
                        break
                except:
                    continue
            
            if not content_element:
                browser.close()
                return None, f"未找到正文内容（已尝试 {len(config.content_selectors)} 个选择器）"
            
            content_html = content_element.inner_html()
            log(f"正文字数：{len(content_html)}", "EXTRACT")
            
            # 优化 HTML：将微信的 """ 转换为标准代码块标签
            log("优化 HTML 代码块格式...", "OPTIMIZE")
            content_html = optimize_html_for_markdown(content_html)
            
            soup = BeautifulSoup(content_html, "html.parser")
            
            # 移除无关标签
            soup = BeautifulSoup(clean_html(str(soup)), "html.parser")
            
            # 处理图片
            log("处理图片...", "IMAGE")
            for img_tag in soup.find_all("img"):
                image_count += 1
                alt = img_tag.get("alt") or "图片"
                src = img_tag.get("data-src") or img_tag.get("src")
                
                if not src or not src.startswith("http"):
                    img_tag.decompose()
                    continue
                
                filename = f"img_{image_count:03d}.jpg"
                save_path = os.path.join(images_dir, filename) if images_dir else None
                # 图片引用使用相对路径：images/knowledge_时间戳/img_001.jpg
                relative_path = f"images/knowledge_{timestamp}/{filename}"
                
                log(f"  ↓ 图片 {image_count}: {filename}", "IMAGE")
                if download_images and save_path and download_image(src, save_path):
                    img_tag.replace_with(f"![{alt}]({relative_path})\n\n")
                else:
                    img_tag.replace_with(f"![{alt}]({src})\n\n")
            
            log(f"图片处理完成，共 {image_count} 张", "IMAGE")
            
            # 转换为 Markdown
            log("转换为 Markdown...", "MARKDOWN")
            clean_html_str = str(soup)
            clean_text = html_to_markdown(clean_html_str)
            
            # 生成内容
            md_content = f"""# {title}

> 链接：{url}  
> 抓取时间：{format_datetime()}  
> 图片数量：{image_count} 张  
> 网站类型：{config.name}  
> 抓取方案：Playwright 无头浏览器

---

{clean_text}
"""
            
            # 文件命名：文章标题.md（清理非法字符）- 直接保存在 output_dir 下
            safe_title = sanitize_title(title)
            output_file = os.path.join(output_dir, f"{safe_title}.md")
            log(f"保存文件：{output_file}", "SAVE")
            
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(md_content)
            
            log("文件保存成功", "SAVE")
            
            browser.close()
            log("浏览器已关闭", "BROWSER")
            
            total_elapsed = time.time() - total_start
            log(f"完成，耗时={total_elapsed:.1f}s", "COMPLETE")
            
            return {
                'success': True,
                'title': title,
                'file': output_file,
                'dir': output_dir,
                'images_dir': images_dir if download_images and image_count > 0 else None,
                'images': image_count,
                'word_count': len(clean_text),
                'elapsed': total_elapsed
            }, None
    
    except Exception as e:
        log(f"失败：{type(e).__name__}: {str(e)[:100]}", "ERROR")
        import traceback
        log(f"堆栈：{traceback.format_exc()}", "ERROR")
        
        try:
            if browser:
                browser.close()
        except:
            pass
        
        return None, f"{type(e).__name__}: {str(e)[:150]}"


# ============================================================================
# 方案二：Scrapling（备选方案）
# ============================================================================

def fetch_with_scrapling(url: str, output_dir: str = DEFAULT_OUTPUT_DIR):
    """
    方案二：Scrapling（备选方案）
    支持多网站识别
    
    Args:
        url: 目标 URL
        output_dir: 输出目录
    
    Returns:
        dict: 抓取结果
        str: 错误信息
    """
    try:
        # 【重要】在开始处理时就生成时间戳，后续所有地方都使用同一个时间戳
        timestamp = format_timestamp()
        print(f"[INFO] 时间戳：{timestamp}")
        
        scrapling_script = os.path.join(
            script_dir,
            "..",
            "third_party",
            "fetch-wx-article",
            "scripts",
            "fetch_wx_article.py"
        )
        
        import importlib.util
        spec = importlib.util.spec_from_file_location("fetch_wx_article", scrapling_script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        print(f"[INFO] 方案二：Scrapling（增强版）")
        
        # 使用新的目录结构：MD 在 output_dir，图片在 images/knowledge_时间戳
        scrapling_images_dir = os.path.join(output_dir, "images", f"knowledge_{timestamp}")
        os.makedirs(scrapling_images_dir, exist_ok=True)
        
        # 修改 fetch_wx_article 的输出目录逻辑
        result = module.fetch_wx_article(
            url, 
            output_dir=output_dir, 
            images_dir=scrapling_images_dir, 
            download_images=True
        )
        
        if result['success']:
            # 调整返回结果格式
            return {
                'success': True,
                'title': result.get('title', 'Unknown'),
                'file': result.get('file', ''),
                'dir': output_dir,
                'images_dir': scrapling_images_dir if result.get('images', 0) > 0 else None,
                'images': result.get('images', 0),
                'word_count': result.get('word_count', 0),
                'elapsed': result.get('elapsed', 0)
            }, None
        else:
            return None, result.get('error', '未知错误')
    
    except Exception as e:
        print(f"[ERROR] Scrapling 方案失败：{type(e).__name__}: {str(e)[:100]}")
        return None, f"{type(e).__name__}: {str(e)[:150]}"


# ============================================================================
# 方案三：第三方 API（保底方案 - 仅支持微信）
# ============================================================================

def fetch_with_api(url: str, output_dir: str = DEFAULT_OUTPUT_DIR, download_images: bool = True):
    """
    方案三：第三方 API（保底方案 - 仅支持微信公众号）
    
    Args:
        url: 目标 URL
        output_dir: 输出目录
        download_images: 是否下载图片
    
    Returns:
        dict: 抓取结果
        str: 错误信息
    """
    import requests
    import urllib.parse
    
    print(f"[INFO] 方案三：第三方 API（仅支持微信）")
    
    if "mp.weixin.qq.com" not in url:
        return None, "第三方 API 仅支持微信公众号链接"
    
    start_time = time.time()
    
    try:
        # 【重要】在开始处理时就生成时间戳，后续所有地方都使用同一个时间戳
        timestamp = format_timestamp()
        print(f"[INFO] 时间戳：{timestamp}")
        
        encoded_url = urllib.parse.quote(url)
        api_url = f"https://down.mptext.top/api/public/v1/download?url={encoded_url}&format=markdown"
        
        print(f"[INFO] 请求 API...")
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        
        content = response.text
        title_match = content.split('\n')[0].replace('#', '').strip() if content.startswith('#') else '微信文章'
        
        os.makedirs(output_dir, exist_ok=True)
        # 图片目录
        images_dir = os.path.join(output_dir, "images", f"knowledge_{timestamp}")
        if download_images:
            os.makedirs(images_dir, exist_ok=True)
        
        image_count = 0
        if download_images:
            print(f"[INFO] 解析并下载图片...")
            img_pattern = r'!\[([^\]]*)\]\((https?://[^)]+)\)'
            
            def download_and_replace(match):
                nonlocal image_count
                image_count += 1
                alt_text = match.group(1)
                img_url = match.group(2)
                filename = f"img_{image_count:03d}.jpg"
                save_path = os.path.join(images_dir, filename)
                # 图片引用使用相对路径
                relative_path = f"images/knowledge_{timestamp}/{filename}"
                
                print(f"  ↓ 图片 {image_count}: {filename}")
                try:
                    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://mp.weixin.qq.com/"}
                    img_response = requests.get(img_url, headers=headers, timeout=10)
                    img_response.raise_for_status()
                    with open(save_path, 'wb') as f:
                        f.write(img_response.content)
                    return f"![{alt_text}]({relative_path})"
                except:
                    print(f"    ⚠️ 下载失败")
                    return match.group(0)
            
            content = re.sub(img_pattern, download_and_replace, content)
            print(f"[INFO] 图片处理完成，共 {image_count} 张")
        
        # 文件命名
        safe_title = sanitize_title(title_match)
        output_file = os.path.join(output_dir, f"{safe_title}.md")
        md_content = f"""# {title_match}

> 链接：{url}  
> 抓取时间：{format_datetime()}  
> 图片数量：{image_count} 张  
> 抓取方案：第三方 API（仅微信公众号）

---

{content}
"""
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(md_content)
        
        elapsed = time.time() - start_time
        print(f"[INFO] 保存成功：{output_file}")
        
        return {
            'success': True,
            'title': title_match,
            'file': output_file,
            'dir': output_dir,
            'images_dir': images_dir if download_images and image_count > 0 else None,
            'images': image_count,
            'word_count': len(content),
            'elapsed': elapsed,
            'scheme': '第三方 API'
        }, None
    
    except Exception as e:
        print(f"[ERROR] API 方案失败：{type(e).__name__}: {str(e)[:100]}")
        return None, f"{type(e).__name__}: {str(e)[:150]}"


# ============================================================================
# 主函数
# ============================================================================

def fetch_url_to_markdown(url: str, output_dir: str = DEFAULT_OUTPUT_DIR):
    """
    Amber Url to Markdown - 主函数
    自动识别链接类型并抓取内容
    
    降级策略：
    1. Playwright（首选 - 支持所有网站）
    2. Scrapling（备选 - 支持所有网站）
    3. 第三方 API（保底 - 仅微信）
    
    Args:
        url: 目标 URL
        output_dir: 输出目录
    
    Returns:
        dict: 抓取结果
    """
    print("\n" + "=" * 60)
    print("Amber Url to Markdown - URL 转 Markdown 工具 (V3.0)")
    print("=" * 60)
    print(f"\n目标链接：{url}\n")
    
    # 方案一：Playwright（首选）
    result, error = fetch_with_playwright(url, output_dir)
    if result:
        print("\n✅ 抓取成功（方案一：Playwright 无头浏览器）")
        print_result(result)
        return result
    
    print(f"\n⚠️ 方案一失败：{error}")
    
    # 方案二：Scrapling（备选）
    print("\n尝试方案二（Scrapling）...\n")
    result, error = fetch_with_scrapling(url, output_dir)
    if result:
        print("\n✅ 抓取成功（方案二：Scrapling 增强版）")
        print_result(result)
        return result
    
    print(f"\n⚠️ 方案二失败：{error}")
    
    # 方案三：第三方 API（保底 - 仅微信）
    if "mp.weixin.qq.com" in url:
        print("\n尝试方案三（第三方 API - 仅微信）...\n")
        result, error = fetch_with_api(url, output_dir)
        if result:
            print("\n✅ 抓取成功（方案三：第三方 API）")
            print_result(result)
            return result
        
        print(f"\n⚠️ 方案三失败：{error}")
    
    print(f"\n❌ 所有方案都失败了：{error}")
    return None


def print_result(result: dict):
    """打印抓取结果"""
    print(f"📄 标题：{result['title']}")
    print(f"📊 字数：{result['word_count']}")
    print(f"🖼️ 图片：{result['images']} 张")
    print(f"⏱️ 耗时：{result['elapsed']:.1f}秒")
    print(f"📂 目录：{result['dir']}")
    print(f"📝 文件：{result['file']}")


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("Usage: python3 amber_url_to_markdown.py <url>")
        print("Example: python3 amber_url_to_markdown.py https://mp.weixin.qq.com/s/xxx")
        print("         python3 amber_url_to_markdown.py https://zhuanlan.zhihu.com/p/xxx")
        sys.exit(1)
    
    url = sys.argv[1]
    result = fetch_url_to_markdown(url)
    
    if not result:
        sys.exit(1)


if __name__ == "__main__":
    main()

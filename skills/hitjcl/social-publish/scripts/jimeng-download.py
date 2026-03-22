#!/usr/bin/env python3
"""
从即梦下载视频
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


def download_video(url: str, output_path: str) -> bool:
    """下载视频到指定路径"""
    try:
        cmd = [
            "Invoke-WebRequest",
            "-Uri", url,
            "-OutFile", output_path
        ]
        result = subprocess.run(
            ["powershell", "-Command", " ".join(cmd)],
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.returncode == 0
    except Exception as e:
        print(f"下载失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="从即梦下载视频")
    parser.add_argument("--url", "-u", type=str, help="视频 URL")
    parser.add_argument("--output", "-o", type=str, default="~/Downloads/jimeng_video.mp4", help="输出路径")
    
    args = parser.parse_args()
    
    if args.url:
        # 直接下载
        output_path = Path(args.output).expanduser()
        print(f"下载视频到: {output_path}")
        if download_video(args.url, str(output_path)):
            print("✅ 下载成功")
        else:
            print("❌ 下载失败")
        return
    
    print("""
即梦视频下载说明
================

由于即梦视频需要登录才能访问，建议通过 OpenClaw 浏览器自动化获取：

1. 打开即梦资产页面: https://jimeng.jianying.com/ai-tool/asset
2. 点击视频进入预览
3. 使用 JavaScript 获取视频 URL:
   document.querySelector('video')?.src
4. 用获取到的 URL 下载视频

示例命令:
  python jimeng-download.py --url "https://..." --output "video.mp4"
""")


if __name__ == "__main__":
    main()

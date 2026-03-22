#!/usr/bin/env python3
"""
多平台视频发布脚本
支持：小红书、抖音、快手、B站
"""

import argparse
import sys
from pathlib import Path

# 平台配置
PLATFORMS = {
    "xiaohongshu": {
        "name": "小红书",
        "publish_url": "https://creator.xiaohongshu.com/publish/publish?from=homepage&target=video",
        "supports_video": True,
        "requires_cover": False,
    },
    "douyin": {
        "name": "抖音",
        "publish_url": "https://creator.douyin.com/",
        "supports_video": True,
        "requires_cover": False,
    },
    "kuaishou": {
        "name": "快手",
        "publish_url": "https://cp.kuaishou.com/article/publish/video",
        "supports_video": True,
        "requires_cover": False,
    },
    "bilibili": {
        "name": "B站",
        "publish_url": "https://member.bilibili.com/platform/upload/video/frame",
        "supports_video": True,
        "requires_cover": True,  # B站需要封面
    },
}


def main():
    parser = argparse.ArgumentParser(description="多平台视频发布工具")
    parser.add_argument("--platform", "-p", choices=list(PLATFORMS.keys()), help="目标平台")
    parser.add_argument("--video", "-v", type=str, help="视频文件路径")
    parser.add_argument("--title", "-t", type=str, help="视频标题")
    parser.add_argument("--cover", "-c", type=str, help="封面图片路径（B站必填）")
    parser.add_argument("--list", "-l", action="store_true", help="列出所有支持的平台")
    
    args = parser.parse_args()
    
    if args.list:
        print("支持的平台：")
        for key, config in PLATFORMS.items():
            cover_note = " (需要封面)" if config["requires_cover"] else ""
            print(f"  - {key}: {config['name']}{cover_note}")
        return
    
    if not args.platform:
        print("请指定目标平台，使用 --platform 或 -p")
        sys.exit(1)
    
    if not args.video:
        print("请指定视频文件路径，使用 --video 或 -v")
        sys.exit(1)
    
    platform = PLATFORMS[args.platform]
    video_path = Path(args.video)
    
    if not video_path.exists():
        print(f"视频文件不存在: {video_path}")
        sys.exit(1)
    
    # B站需要封面
    if platform["requires_cover"] and not args.cover:
        print(f"⚠️ {platform['name']} 需要上传封面图片，请使用 --cover 指定")
        sys.exit(1)
    
    print(f"""
发布配置：
  平台: {platform['name']}
  视频: {video_path}
  标题: {args.title or '(自动生成)'}
  封面: {args.cover or '(不需要)'}
  
发布链接: {platform['publish_url']}

提示：此脚本仅提供发布信息，实际发布需要通过 OpenClaw 浏览器自动化完成。
""")


if __name__ == "__main__":
    main()

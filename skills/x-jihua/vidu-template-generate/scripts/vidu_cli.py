#!/usr/bin/env python3
"""
Vidu Lite CLI - Simplified video/image/audio generation
Supports: text2video, img2video, ref2video, start-end2video, template, 
          nano-image, text2image, tts, voice-clone

域名选择规则：
- 简体中文用户：api.vidu.cn（默认）
- 非简体中文用户：api.vidu.com
"""

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional
import urllib.request
import urllib.error

# Configuration
# 根据用户语言选择域名：简体中文用 api.vidu.cn，其他语言用 api.vidu.com
BASE_URL = "https://api.vidu.cn/ent/v2"  # 默认国内域名
API_KEY = os.environ.get("VIDU_API_KEY", "")

def get_headers():
    if not API_KEY:
        print("Error: VIDU_API_KEY environment variable not set")
        sys.exit(1)
    return {
        "Content-Type": "application/json",
        "Authorization": f"Token {API_KEY}"
    }

def make_request(endpoint: str, data: dict, method: str = "POST") -> dict:
    """Make HTTP request to Vidu API"""
    url = f"{BASE_URL}{endpoint}"
    headers = get_headers()
    
    req_data = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"HTTP Error {e.code}: {error_body}")
        sys.exit(1)
    except Exception as e:
        print(f"Request failed: {e}")
        sys.exit(1)

def image_to_base64(image_path: str) -> str:
    """Convert local image to base64 data URL"""
    path = Path(image_path)
    if not path.exists():
        print(f"Error: Image file not found: {image_path}")
        sys.exit(1)
    
    ext = path.suffix.lower().lstrip('.')
    if ext == 'jpg':
        ext = 'jpeg'
    
    with open(path, 'rb') as f:
        img_data = f.read()
    
    b64_data = base64.b64encode(img_data).decode('utf-8')
    return f"data:image/{ext};base64,{b64_data}"

def process_image_input(image: str) -> str:
    """Process image input (URL or local file)"""
    if image.startswith('http://') or image.startswith('https://'):
        return image
    elif image.startswith('data:'):
        return image
    else:
        return image_to_base64(image)

def download_file(url: str, output_path: str):
    """Download file from URL"""
    print(f"Downloading to: {output_path}")
    urllib.request.urlretrieve(url, output_path)
    print(f"Download complete: {output_path}")

def print_task_result(result: dict):
    """Print task result in a formatted way"""
    print(f"\n{'='*50}")
    print(f"Task ID: {result.get('task_id') or result.get('id', 'N/A')}")
    print(f"State: {result.get('state', 'N/A')}")
    print(f"Model: {result.get('model', 'N/A')}")
    if result.get('prompt'):
        print(f"Prompt: {result.get('prompt', '')[:50]}...")
    if result.get('credits'):
        print(f"Credits: {result['credits']}")
    if result.get('created_at'):
        print(f"Created: {result['created_at']}")
    if result.get('duration'):
        print(f"Duration: {result['duration']}s")
    print('='*50)

# ==================== Video Generation ====================

def cmd_text2video(args):
    """Text to video generation"""
    data = {
        "model": args.model or "viduq3-pro",
        "prompt": args.prompt,
    }
    
    if args.duration:
        data["duration"] = args.duration
    if args.aspect_ratio:
        data["aspect_ratio"] = args.aspect_ratio
    if args.resolution:
        data["resolution"] = args.resolution
    if hasattr(args, 'audio') and args.audio is not None:
        data["audio"] = args.audio
    if args.seed:
        data["seed"] = args.seed
    if hasattr(args, 'off_peak') and args.off_peak:
        data["off_peak"] = True
    
    result = make_request("/text2video", data)
    print_task_result(result)
    return result

def cmd_img2video(args):
    """Image to video generation"""
    images = [process_image_input(args.image)]
    
    data = {
        "model": args.model or "viduq3-pro",
        "images": images,
    }
    
    if args.prompt:
        data["prompt"] = args.prompt
    if args.duration:
        data["duration"] = args.duration
    if args.resolution:
        data["resolution"] = args.resolution
    if hasattr(args, 'audio') and args.audio is not None:
        data["audio"] = args.audio
    if args.seed:
        data["seed"] = args.seed
    if hasattr(args, 'off_peak') and args.off_peak:
        data["off_peak"] = True
    
    result = make_request("/img2video", data)
    print_task_result(result)
    return result

def cmd_ref2video(args):
    """Reference to video"""
    images = [process_image_input(img) for img in args.images]
    
    data = {
        "model": args.model or "viduq3",
        "images": images,
        "prompt": args.prompt,
    }
    
    if args.duration:
        data["duration"] = args.duration
    if args.resolution:
        data["resolution"] = args.resolution
    if hasattr(args, 'audio') and args.audio:
        data["audio"] = True
    if args.seed:
        data["seed"] = args.seed
    
    result = make_request("/reference2video", data)
    print_task_result(result)
    return result

def cmd_start_end2video(args):
    """Start-end frame to video"""
    images = [
        process_image_input(args.start_frame),
        process_image_input(args.end_frame)
    ]
    
    data = {
        "model": args.model or "viduq3-pro",
        "images": images,
    }
    
    if args.prompt:
        data["prompt"] = args.prompt
    if args.duration:
        data["duration"] = args.duration
    if args.resolution:
        data["resolution"] = args.resolution
    if hasattr(args, 'audio') and args.audio is not None:
        data["audio"] = args.audio
    if args.seed:
        data["seed"] = args.seed
    
    result = make_request("/start-end2video", data)
    print_task_result(result)
    return result

def cmd_template(args):
    """Scene template video generation"""
    data = {
        "template": args.template,
        "images": [process_image_input(args.image)],
    }
    
    if args.prompt:
        data["prompt"] = args.prompt
    if args.seed:
        data["seed"] = args.seed
    if args.bgm:
        data["bgm"] = True
    
    result = make_request("/template", data)
    print_task_result(result)
    return result

# ==================== Image Generation ====================

def cmd_nano_image(args):
    """Image generation (nano endpoint)"""
    data = {
        "model": args.model or "q3-fast",
        "prompt": args.prompt,
    }
    
    if args.images:
        data["images"] = [process_image_input(img) for img in args.images]
    if args.aspect_ratio:
        data["aspect_ratio"] = args.aspect_ratio
    if args.resolution:
        data["resolution"] = args.resolution
    
    result = make_request("/reference2image/nano", data)
    print_task_result(result)
    return result

def cmd_text2image(args):
    """Text/reference to image generation (legacy endpoint)"""
    data = {
        "model": args.model or "viduq2",
        "prompt": args.prompt,
    }
    
    if args.images:
        data["images"] = [process_image_input(img) for img in args.images]
    if args.aspect_ratio:
        data["aspect_ratio"] = args.aspect_ratio
    if args.resolution:
        data["resolution"] = args.resolution
    if args.seed:
        data["seed"] = args.seed
    
    result = make_request("/reference2image", data)
    print_task_result(result)
    return result

# ==================== Audio Generation ====================

def cmd_tts(args):
    """Text-to-speech synthesis"""
    text = args.text
    if args.text_file:
        with open(args.text_file, 'r', encoding='utf-8') as f:
            text = f.read().strip()
    if not text:
        print("Error: --text or --text-file is required")
        sys.exit(1)
    
    data = {
        "text": text,
        "voice_setting_voice_id": args.voice_id,
    }
    
    if args.speed:
        data["voice_setting_speed"] = args.speed
    if args.volume is not None:
        data["voice_setting_volume"] = args.volume
    if args.pitch is not None:
        data["voice_setting_pitch"] = args.pitch
    if args.emotion:
        data["voice_setting_emotion"] = args.emotion
    
    result = make_request("/audio-tts", data)
    print_task_result(result)
    
    # TTS is synchronous, download immediately if URL provided
    if result.get("state") == "success" and result.get("file_url"):
        if args.download:
            download_file(result["file_url"], args.download)
        else:
            print(f"Audio URL: {result['file_url']}")
    
    return result

def cmd_voice_clone(args):
    """Voice cloning"""
    text = args.text
    if args.text_file:
        with open(args.text_file, 'r', encoding='utf-8') as f:
            text = f.read().strip()
    
    data = {
        "audio_url": args.audio_url,
        "voice_id": args.voice_id,
        "text": text,
    }
    
    if args.prompt_audio_url:
        data["prompt_audio_url"] = args.prompt_audio_url
    if args.prompt_text:
        data["prompt_text"] = args.prompt_text
    
    result = make_request("/audio-clone", data)
    print_task_result(result)
    return result

# ==================== Task Management ====================

def get_task_by_id(task_id: str) -> Optional[dict]:
    """Get task by ID"""
    result = make_request("/tasks", {}, method="GET")
    tasks = result.get('tasks', [])
    
    for task in tasks:
        if task.get('id') == task_id:
            return task
    
    next_token = result.get('next_page_token')
    while next_token:
        page_result = make_request(f"/tasks?page_token={next_token}", {}, method="GET")
        for task in page_result.get('tasks', []):
            if task.get('id') == task_id:
                return task
        next_token = page_result.get('next_page_token')
    
    return None

def cmd_status(args):
    """Query task status"""
    task = get_task_by_id(args.task_id)
    
    if not task:
        print(f"Task {args.task_id} not found")
        return None
    
    print_task_result(task)
    
    if task.get('state') == 'success':
        creations = task.get('creations', [])
        if creations:
            creation = creations[0]
            if creation.get('url'):
                print(f"Video URL: {creation['url']}")
            if creation.get('cover_url'):
                print(f"Cover URL: {creation['cover_url']}")
    
    # Wait for completion if requested
    if args.wait and task.get('state') not in ['success', 'failed']:
        print(f"\nWaiting for task completion...")
        while True:
            time.sleep(10)
            task = get_task_by_id(args.task_id)
            if not task:
                print("Task not found")
                break
            state = task.get('state')
            print(f"State: {state}")
            
            if state in ['success', 'failed']:
                break
        
        print_task_result(task)
        
        if task and task.get('state') == 'success' and args.download:
            creations = task.get('creations', [])
            if creations:
                url = creations[0].get('url')
                if url:
                    output_path = os.path.join(args.download, f"vidu_{args.task_id}.mp4")
                    download_file(url, output_path)
    
    return task

def cmd_cancel(args):
    """Cancel/delete a task"""
    result = make_request(f"/tasks/{args.task_id}", {}, method="DELETE")
    print(f"Task {args.task_id} cancelled/deleted")
    return result

# ==================== Main CLI ====================

def main():
    parser = argparse.ArgumentParser(
        description="Vidu Lite CLI - Video/Image/Audio Generation",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Text to video
    p_t2v = subparsers.add_parser("text2video", help="Text to video")
    p_t2v.add_argument("--prompt", required=True, help="Video description")
    p_t2v.add_argument("--model", default="viduq3-pro", help="Model (default: viduq3-pro)")
    p_t2v.add_argument("--duration", type=int, default=5, help="Duration in seconds (default: 5)")
    p_t2v.add_argument("--aspect-ratio", default="16:9", help="Aspect ratio (default: 16:9)")
    p_t2v.add_argument("--resolution", default="720p", help="Resolution (default: 720p)")
    p_t2v.add_argument("--audio", type=lambda x: x.lower() == 'true', help="Enable audio")
    p_t2v.add_argument("--seed", type=int, help="Random seed")
    p_t2v.add_argument("--off-peak", action="store_true", help="Off-peak mode")
    
    # Image to video
    p_i2v = subparsers.add_parser("img2video", help="Image to video")
    p_i2v.add_argument("--image", required=True, help="Input image (URL or local file)")
    p_i2v.add_argument("--prompt", help="Video description")
    p_i2v.add_argument("--model", default="viduq3-pro", help="Model (default: viduq3-pro)")
    p_i2v.add_argument("--duration", type=int, default=5, help="Duration (default: 5)")
    p_i2v.add_argument("--resolution", default="720p", help="Resolution")
    p_i2v.add_argument("--audio", type=lambda x: x.lower() == 'true', help="Enable audio")
    p_i2v.add_argument("--seed", type=int, help="Random seed")
    
    # Reference to video
    p_r2v = subparsers.add_parser("ref2video", help="Reference to video (multi-subject)")
    p_r2v.add_argument("--images", nargs='+', required=True, help="Reference images")
    p_r2v.add_argument("--prompt", required=True, help="Video description")
    p_r2v.add_argument("--model", default="viduq3", help="Model (default: viduq3)")
    p_r2v.add_argument("--duration", type=int, default=5, help="Duration")
    p_r2v.add_argument("--resolution", default="720p", help="Resolution")
    p_r2v.add_argument("--audio", action="store_true", help="Enable audio")
    p_r2v.add_argument("--seed", type=int, help="Random seed")
    
    # Start-end to video
    p_se = subparsers.add_parser("start-end2video", help="Start-end frame to video")
    p_se.add_argument("--start-frame", required=True, help="Start frame image")
    p_se.add_argument("--end-frame", required=True, help="End frame image")
    p_se.add_argument("--prompt", help="Video description")
    p_se.add_argument("--model", default="viduq3-pro", help="Model (default: viduq3-pro)")
    p_se.add_argument("--duration", type=int, default=5, help="Duration")
    p_se.add_argument("--resolution", default="720p", help="Resolution")
    p_se.add_argument("--audio", type=lambda x: x.lower() == 'true', help="Enable audio")
    p_se.add_argument("--seed", type=int, help="Random seed")
    
    # Template
    p_tpl = subparsers.add_parser("template", help="Scene template video")
    p_tpl.add_argument("--template", required=True, help="Template name")
    p_tpl.add_argument("--image", required=True, help="Input image")
    p_tpl.add_argument("--prompt", help="Additional prompt")
    p_tpl.add_argument("--seed", type=int, help="Random seed")
    p_tpl.add_argument("--bgm", action="store_true", help="Add BGM")
    
    # Nano image (recommended)
    p_nano = subparsers.add_parser("nano-image", help="Image generation (q3-fast)")
    p_nano.add_argument("--prompt", required=True, help="Image description")
    p_nano.add_argument("--images", nargs='+', help="Reference images (optional)")
    p_nano.add_argument("--model", default="q3-fast", help="Model: q3-fast, q2-fast, q2-pro")
    p_nano.add_argument("--aspect-ratio", default="16:9", help="Aspect ratio")
    p_nano.add_argument("--resolution", default="2K", help="Resolution: 1K, 2K, 4K")
    
    # Text to image (legacy)
    p_t2i = subparsers.add_parser("text2image", help="Image generation (legacy)")
    p_t2i.add_argument("--prompt", required=True, help="Image description")
    p_t2i.add_argument("--images", nargs='+', help="Reference images")
    p_t2i.add_argument("--model", default="viduq2", help="Model")
    p_t2i.add_argument("--aspect-ratio", default="16:9", help="Aspect ratio")
    p_t2i.add_argument("--resolution", default="1080p", help="Resolution")
    p_t2i.add_argument("--seed", type=int, help="Random seed")
    
    # TTS
    p_tts = subparsers.add_parser("tts", help="Text-to-speech")
    p_tts.add_argument("--text", help="Text to synthesize (use --text-file for long texts)")
    p_tts.add_argument("--text-file", help="Path to text file (avoids shell quoting issues)")
    p_tts.add_argument("--voice-id", required=True, help="Voice ID (see references/voice_id_list.md)")
    p_tts.add_argument("--speed", type=float, help="Speech speed (0.5-2.0)")
    p_tts.add_argument("--volume", type=int, help="Volume (0-10)")
    p_tts.add_argument("--pitch", type=int, help="Pitch (-12 to 12)")
    p_tts.add_argument("--emotion", help="Emotion (happy, sad, angry, etc.)")
    p_tts.add_argument("--download", help="Download path")
    
    # Voice clone
    p_vc = subparsers.add_parser("voice-clone", help="Voice cloning")
    p_vc.add_argument("--audio-url", required=True, help="Source audio URL")
    p_vc.add_argument("--voice-id", required=True, help="Custom voice ID")
    p_vc.add_argument("--text", help="Demo text")
    p_vc.add_argument("--text-file", help="Path to text file")
    p_vc.add_argument("--prompt-audio-url", help="Reference audio URL")
    p_vc.add_argument("--prompt-text", help="Reference audio text")
    
    # Status
    p_status = subparsers.add_parser("status", help="Query task status")
    p_status.add_argument("task_id", help="Task ID")
    p_status.add_argument("--wait", action="store_true", help="Wait for completion")
    p_status.add_argument("--download", help="Download directory")
    
    # Cancel
    p_cancel = subparsers.add_parser("cancel", help="Cancel task")
    p_cancel.add_argument("task_id", help="Task ID")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    commands = {
        "text2video": cmd_text2video,
        "img2video": cmd_img2video,
        "ref2video": cmd_ref2video,
        "start-end2video": cmd_start_end2video,
        "template": cmd_template,
        "nano-image": cmd_nano_image,
        "text2image": cmd_text2image,
        "tts": cmd_tts,
        "voice-clone": cmd_voice_clone,
        "status": cmd_status,
        "cancel": cmd_cancel,
    }
    
    commands[args.command](args)

if __name__ == "__main__":
    main()

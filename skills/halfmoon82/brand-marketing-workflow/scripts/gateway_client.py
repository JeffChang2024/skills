#!/usr/bin/env python3
"""
gateway_client.py - brand-marketing-workflow 底层工具模块

提供：
  load_config()    - 读取 ~/.openclaw/openclaw.json
  llm_complete()   - 直连 lovbrowser-openai API 生成内容
  gateway_send()   - 通过本地 gateway 发送 Telegram/Feishu 消息
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
import io

# ─── 常量 ────────────────────────────────────────────────────────────────────

OPENCLAW_CONFIG_PATH = os.path.expanduser("~/.openclaw/openclaw.json")
LLM_ENDPOINT = "http://14.152.85.204:4000/v1/chat/completions"
GATEWAY_URL = "http://127.0.0.1:18789"

# ─── 配置加载 ─────────────────────────────────────────────────────────────────

# Fix-5: 模块级缓存，避免重复读取配置文件
_config_cache: dict | None = None


def load_config() -> dict:
    """读取 ~/.openclaw/openclaw.json，返回完整配置 dict。单次读取后缓存。"""
    global _config_cache
    if _config_cache is not None:
        return _config_cache
    # Fix-2: 配置文件 I/O 错误处理
    try:
        with open(OPENCLAW_CONFIG_PATH, encoding="utf-8") as f:
            _config_cache = json.load(f)
    except FileNotFoundError:
        raise RuntimeError(f"配置文件不存在: {OPENCLAW_CONFIG_PATH}") from None
    except json.JSONDecodeError as e:
        raise RuntimeError(f"配置文件 JSON 格式错误: {e}") from None
    return _config_cache


def _get_lovbrowser_api_key() -> str:
    cfg = load_config()
    key = cfg.get("env", {}).get("vars", {}).get("LOVBROWSER_API_KEY", "")
    if not key:
        raise RuntimeError("LOVBROWSER_API_KEY 未在 openclaw.json env.vars 中配置")
    return key


def _get_gateway_token() -> str:
    cfg = load_config()
    token = cfg.get("gateway", {}).get("auth", {}).get("token", "")
    if not token:
        raise RuntimeError("gateway.auth.token 未在 openclaw.json 中配置")
    return token


# ─── LLM 调用 ────────────────────────────────────────────────────────────────

def llm_complete(
    prompt: str,
    model: str = "gpt-5.4-mini",
    max_tokens: int = 2000,
    system: str | None = None,
) -> str:
    """
    直连 lovbrowser-openai API 生成内容。

    参数：
      prompt     - 用户消息内容
      model      - 模型 ID（不含 provider 前缀，如 "gpt-5.4-mini"）
      max_tokens - 最大输出 token 数
      system     - 可选 system prompt

    返回：choices[0].message.content 字符串
    失败时 raise RuntimeError（含 HTTP 状态码和响应体）
    """
    api_key = _get_lovbrowser_api_key()

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    # lovbrowser-openai 要求 stream=true（参见 MEMORY: lovbrowser 要求 streaming）
    body = json.dumps({
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "stream": True,
    }).encode("utf-8")

    req = urllib.request.Request(
        LLM_ENDPOINT,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    # 解析 SSE 流式响应，拼接 delta.content
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            chunks = []
            # Fix-4: errors="replace" 防止非法 UTF-8 字节抛出异常
            for raw_line in io.TextIOWrapper(resp, encoding="utf-8", errors="replace"):
                line = raw_line.strip()
                if not line or not line.startswith("data:"):
                    continue
                data_str = line[len("data:"):].strip()
                if data_str == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content")
                    if content:
                        chunks.append(content)
                except (json.JSONDecodeError, IndexError):
                    continue
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"LLM 调用失败 HTTP {e.code}: {error_body}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"LLM 调用网络错误: {e.reason}") from e

    # Fix-1: 流式响应空字符串检查
    result = "".join(chunks)
    if not result:
        raise RuntimeError("LLM 流式响应为空（可能网络中断或模型未返回内容）")
    return result


# ─── Gateway 消息发送 ────────────────────────────────────────────────────────

def gateway_send(
    channel: str,
    account_id: str,
    to: str,
    message: str,
) -> bool:
    """
    通过本地 gateway 发送消息（Telegram / Feishu）。

    参数：
      channel    - 渠道名称，如 "telegram" 或 "feishu"
      account_id - Bot 账号 ID，如 "bot1" 或 "bot4"
      to         - 目标用户/群组 ID
      message    - 消息内容

    返回：True 成功，False 失败（不 raise）
    """
    try:
        token = _get_gateway_token()
    except RuntimeError:
        return False

    body = json.dumps({
        "channel": channel,
        "accountId": account_id,
        "to": to,
        "message": message,
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{GATEWAY_URL}/api/messages/send",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            # Fix-6: 检查响应体中的 ok 字段（gateway 消息发送可能不含 ok 字段，默认 True）
            if resp.status not in (200, 201, 202):
                return False
            try:
                body_data = json.loads(resp.read().decode("utf-8", errors="replace"))
                if body_data.get("ok", True) is False:
                    return False
            except (json.JSONDecodeError, AttributeError):
                pass
            return True
    # Fix-3: 缩窄异常捕获范围，避免掩盖编程错误
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError):
        return False


# ─── 测试入口 ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("测试 llm_complete...")
    reply = llm_complete("回复: 你好")
    print(f"LLM 响应：{reply}")

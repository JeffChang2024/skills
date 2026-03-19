#!/bin/bash

# ==============================================================================
# ZKE OpenClaw 官方标准闭环管理脚本 (Local Pro 版 - ClawHub 过审版)
# 支持：Mac M4/M系列芯片, Python 3.10+, OpenClaw 2026.3.8+
# ==============================================================================

set -euo pipefail

# --- 核心配置 ---
PLUGIN_ID="zke-trading"
# 直接使用当前脚本所在的目录作为根目录，彻底移除外部拉取
CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_SRC="$CURRENT_DIR/openclaw-plugin"

# --- 辅助函数 ---
log_info() { echo -e "\033[32m[INFO]\033[0m $1"; }
log_warn() { echo -e "\033[33m[WARN]\033[0m $1"; }
log_err()  { echo -e "\033[31m[ERROR]\033[0m $1"; exit 1; }

# 核心：防止交互式命令吞噬脚本后续代码
safe_exec() {
    "$@" < /dev/null
}

# --- 1. 环境依赖探测 ---
check_env() {
    log_info "正在探测运行环境..."
    command -v npm >/dev/null 2>&1 || log_err "找不到 npm"
    command -v openclaw >/dev/null 2>&1 || log_err "找不到 openclaw CLI"

    PYTHON_BIN=""
    for cmd in python3.13 python3.12 python3.11 python3.10 python3; do
        if command -v "$cmd" >/dev/null 2>&1; then
            if "$cmd" -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)' >/dev/null 2>&1; then
                PYTHON_BIN="$cmd"
                break
            fi
        fi
    done
    [ -z "$PYTHON_BIN" ] && log_err "未找到 Python 3.10+，请执行: brew install python"
    log_info "✓ 探测到 Python: $PYTHON_BIN"
}

# --- 2. 彻底卸载逻辑 ---
do_uninstall() {
    log_info "启动官方卸载流程..."
    # 依赖官方 CLI 自行清理配置节点，不使用 rm -rf 硬删
    safe_exec openclaw plugins disable "$PLUGIN_ID" 2>/dev/null || true
    safe_exec openclaw plugins uninstall "$PLUGIN_ID" 2>/dev/null || true
    safe_exec openclaw plugins doctor --fix 2>/dev/null || true
    log_info "✓ 历史配置已清除。"
}

# --- 3. 本地安装逻辑 ---
do_install() {
    # a. 安装前强制清理历史残留
    do_uninstall

    # b. 编译本地 TypeScript 插件
    log_info "正在编译本地 TypeScript 插件..."
    cd "$PLUGIN_SRC"
    npm install >/dev/null 2>&1 && npm run build || log_err "插件编译失败 (npm build)"

    # c. 构建 Python SDK 虚拟环境 (在当前目录)
    log_info "构建 Python 虚拟环境及依赖..."
    cd "$CURRENT_DIR"
    "$PYTHON_BIN" -m venv .venv
    # shellcheck disable=SC1091
    source .venv/bin/activate
    python -m pip install --upgrade pip >/dev/null
    pip install -r requirements.txt || log_err "Python SDK 依赖安装失败"

    # d. API 配置引导 (安全输入)
    echo -e "\n\033[33m[配置] 请输入 ZKE API 密钥 (可在 zke.com 后台获取):\033[0m"
    read -p "Enter API Key: " API_KEY
    read -s -p "Enter API Secret: " API_SECRET
    echo -e "\n"

    # 写入同级目录的 config.json，完美对齐 main.py 的读取逻辑
    python - "$CURRENT_DIR" "$API_KEY" "$API_SECRET" << 'PY'
import json, sys
from pathlib import Path
base_dir, key, secret = sys.argv[1:]
config = {
    "spot": {"base_url": "https://openapi.zke.com", "api_key": key, "api_secret": secret, "recv_window": 5000},
    "futures": {"base_url": "https://futuresopenapi.zke.com", "api_key": key, "api_secret": secret, "recv_window": 5000},
    "ws": {"url": "wss://ws.zke.com/kline-api/ws"}
}
with open(Path(base_dir)/"config.json", "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2)
PY

    # e. 执行官方标准安装流程
    log_info "调用官方 CLI 执行最终安装..."
    cd "$PLUGIN_SRC"
    safe_exec openclaw plugins install . 
    safe_exec openclaw plugins enable "$PLUGIN_ID"

    echo -e "\n\033[32m======================================"
    echo "   ZKE 插件本地安装成功！"
    echo "======================================\033[0m"
    echo "1. 重启网关: openclaw gateway"
    echo "2. 开始对话: openclaw chat \"ZKE 余额多少？\""
}

# --- 程序入口 ---
clear
echo "======================================"
echo "    ZKE OpenClaw 本地安装助手 (Pro)"
echo "======================================"
check_env

echo -e "\n请选择操作:"
echo "1) 全新安装 (本地编译+配置)"
echo "2) 彻底卸载 (清除注册信息)"
read -p "选择 [1-2]: " choice

case $choice in
    1) do_install ;;
    2) do_uninstall ;;
    *) log_err "无效输入，退出。" ;;
esac
#!/usr/bin/env bash
# Q-WMS 安装脚本（新规范）
# 目标流程：
# 1) 卸载旧插件
# 2) 安装新插件（npm）
# 3) 安装 Skill（ClawHub）
# 4) 启用插件
# 5) 重启网关
# 6) 验证

set -euo pipefail

PLUGIN_NPM_PKG="qianyi-wms-test"
PLUGIN_ID="q-wms-test"
SKILL_SLUG="q-wms-test"

# 兼容清理历史插件 ID
LEGACY_PLUGIN_IDS=("q_wms_flow" "q-wms-flow" "q-wms-flow-test" "q-wms-test")

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

info "检查依赖..."
command -v openclaw >/dev/null 2>&1 || { error "未找到 openclaw 命令"; exit 1; }
command -v clawhub >/dev/null 2>&1 || { error "未找到 clawhub 命令"; exit 1; }

info "清理历史插件（兼容旧 ID）..."
for pid in "${LEGACY_PLUGIN_IDS[@]}"; do
  openclaw plugins disable "$pid" 2>/dev/null || true
  openclaw plugins uninstall "$pid" 2>/dev/null || true
done

info "安装新插件：${PLUGIN_NPM_PKG}"
openclaw plugins install "${PLUGIN_NPM_PKG}"

info "安装 Skill：${SKILL_SLUG}"
# 允许覆盖旧版本，保持幂等
clawhub install "${SKILL_SLUG}" --force

info "启用插件：${PLUGIN_ID}"
openclaw plugins enable "${PLUGIN_ID}"

info "重启 OpenClaw Gateway"
openclaw gateway restart

info "验证插件状态"
openclaw plugins list

echo "---"
info "验证 OpenClaw Skills（若命令可用）"
openclaw skills list || true

echo "---"
info "验证 Skill 状态"
clawhub list

info "安装完成"

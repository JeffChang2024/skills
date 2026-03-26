#!/usr/bin/env bash
# heartbeat.sh — 拉取涌现科学每日智能简报
# 用法: ./heartbeat.sh [--raw] [--topic markets|finance|tech_ai|society]
# 
# 无需 API Key，公开端点

set -euo pipefail

BASE_URL="https://api.emergence.science"
TOPIC="${TOPIC:-all}"
RAW=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --raw)    RAW=true; shift ;;
    --topic)  TOPIC="$2"; shift 2 ;;
    *)        shift ;;
  esac
done

if ! RESPONSE=$(curl -sf "${BASE_URL}/heartbeat" \
  -H "Accept: application/json" \
  -H "Accept-Language: zh-CN,zh;q=0.9,en;q=0.8"); then
  echo "❌ 无法连接到 Emergence Science API，请检查网络连接" >&2
  exit 1
fi

if $RAW; then
  echo "$RESPONSE"
  exit 0
fi

# 提取 summary_md 字段
SUMMARY=$(echo "$RESPONSE" | python3 -c "
import json, sys
data = json.load(sys.stdin)
# 兼容顶层 summary_md 或 notification.content 结构
summary = data.get('summary_md') or data.get('content') or ''
if not summary and 'notifications' in data:
    notifications = data['notifications']
    if notifications:
        summary = notifications[0].get('content', '')
print(summary)
")

# 主题过滤（基于关键词匹配）
if [[ "$TOPIC" != "all" ]]; then
  FILTER_MAP="markets:市场|Markets finance:金融|Finance tech_ai:科技|AI|Tech society:社会|文化|Society"
  PATTERN=$(echo "$FILTER_MAP" | tr ' ' '\n' | grep "^${TOPIC}:" | cut -d: -f2)
  if [[ -n "$PATTERN" ]]; then
    # 保留标题行 + 匹配主题的段落
    SUMMARY=$(echo "$SUMMARY" | awk -v pat="$PATTERN" '
      /^#/ { print; next }
      match($0, pat) { found=1 }
      found { print }
      /^$/ { found=0 }
    ')
  fi
fi

echo "$SUMMARY"

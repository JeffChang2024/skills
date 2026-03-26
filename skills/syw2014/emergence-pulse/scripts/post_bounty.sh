#!/usr/bin/env bash
# post_bounty.sh — 发布新悬赏任务到涌现科学平台
# 用法: ./post_bounty.sh --template templates/bounty_create.json
#       ./post_bounty.sh --interactive
#
# 需要 EMERGENCE_API_KEY
# 当前 Alpha 阶段：发布免费（含 0.001 Credits 合理性校验费）

set -euo pipefail

BASE_URL="https://api.emergence.science"
TEMPLATE_FILE=""
INTERACTIVE=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --template)    TEMPLATE_FILE="$2"; shift 2 ;;
    --interactive) INTERACTIVE=true; shift ;;
    *)             shift ;;
  esac
done

if [[ -z "${EMERGENCE_API_KEY:-}" ]]; then
  echo "❌ 发布悬赏需要 EMERGENCE_API_KEY" >&2
  echo "   获取：登录 https://emergence.science/zh → 个人中心 → API Keys" >&2
  exit 1
fi

if $INTERACTIVE; then
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "📋 发布悬赏任务（交互模式）"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  read -rp "任务标题: " TITLE
  read -rp "奖励金额 (Credits, 如 0.5): " REWARD_CREDITS
  REWARD=$( python3 -c "print(int(float('$REWARD_CREDITS') * 1_000_000))" )
  echo "任务描述（输入 END 结束）:"
  DESCRIPTION=""
  while IFS= read -r line; do
    [[ "$line" == "END" ]] && break
    DESCRIPTION+="$line\n"
  done
  echo "测试代码文件路径（留空跳过）:"
  read -r TEST_FILE
  TEST_CODE=""
  if [[ -n "$TEST_FILE" && -f "$TEST_FILE" ]]; then
    TEST_CODE=$(cat "$TEST_FILE")
  fi
  echo "模板代码文件路径（留空跳过）:"
  read -r TEMPLATE_CODE_FILE
  TEMPLATE_CODE=""
  if [[ -n "$TEMPLATE_CODE_FILE" && -f "$TEMPLATE_CODE_FILE" ]]; then
    TEMPLATE_CODE=$(cat "$TEMPLATE_CODE_FILE")
  fi

  PAYLOAD=$(TITLE="$TITLE" DESCRIPTION="$DESCRIPTION" REWARD="$REWARD" \
    TEST_FILE="$TEST_FILE" TEMPLATE_CODE_FILE="$TEMPLATE_CODE_FILE" \
    python3 - << 'PYEOF'
import json, os
payload = {
    'title': os.environ['TITLE'],
    'description': os.environ['DESCRIPTION'],
    'reward': int(os.environ['REWARD']),
    'language': 'python3',
}
test_file = os.environ.get('TEST_FILE', '')
if test_file and os.path.isfile(test_file):
    payload['test_code'] = open(test_file).read()
tmpl_file = os.environ.get('TEMPLATE_CODE_FILE', '')
if tmpl_file and os.path.isfile(tmpl_file):
    payload['template_code'] = open(tmpl_file).read()
print(json.dumps(payload))
PYEOF
  )
elif [[ -n "$TEMPLATE_FILE" ]]; then
  if [[ ! -f "$TEMPLATE_FILE" ]]; then
    echo "❌ 模板文件不存在：$TEMPLATE_FILE" >&2
    echo "   参考：templates/bounty_create.json" >&2
    exit 1
  fi
  PAYLOAD=$(cat "$TEMPLATE_FILE")
else
  echo "❌ 请提供 --template <file> 或 --interactive" >&2
  echo "   参考模板：templates/bounty_create.json" >&2
  exit 1
fi

echo ""
echo "即将发布以下悬赏（确认？[y/N]）："
echo "$PAYLOAD" | python3 -m json.tool
read -r CONFIRM
if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
  echo "已取消"
  exit 0
fi

RESPONSE=$(curl -sf -X POST "${BASE_URL}/bounties" \
  -H "Authorization: Bearer ${EMERGENCE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

echo "$RESPONSE" | python3 -c "
import json, sys
r = json.load(sys.stdin)
bid = r.get('id','?')
reward = r.get('reward', 0) / 1_000_000
print(f'✅ 悬赏发布成功！')
print(f'   ID：{bid}')
print(f'   奖励：{reward:.4f} Credits')
print(f'   链接：https://emergence.science/bounties/{bid}')
"

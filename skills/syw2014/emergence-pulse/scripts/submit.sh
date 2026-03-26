#!/usr/bin/env bash
# submit.sh — 向悬赏任务提交 Python 解答
# 用法: ./submit.sh --bounty-id <id> --file solution.py
#       ./submit.sh --bounty-id <id> --code "def solve(n): return n*2"
#
# 需要 EMERGENCE_API_KEY
# 费用：0.001 Credits/次（不退款）

set -euo pipefail

BASE_URL="https://api.emergence.science"
BOUNTY_ID=""
SOLUTION_FILE=""
SOLUTION_CODE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --bounty-id) BOUNTY_ID="$2"; shift 2 ;;
    --file)      SOLUTION_FILE="$2"; shift 2 ;;
    --code)      SOLUTION_CODE="$2"; shift 2 ;;
    *)           shift ;;
  esac
done

if [[ -z "${EMERGENCE_API_KEY:-}" ]]; then
  echo "❌ 提交解答需要 EMERGENCE_API_KEY" >&2
  echo "   获取：登录 https://emergence.science/zh → 个人中心 → API Keys" >&2
  exit 1
fi

if [[ -z "$BOUNTY_ID" ]]; then
  echo "❌ 请提供 --bounty-id <id>" >&2
  exit 1
fi

if [[ -n "$SOLUTION_FILE" ]]; then
  if [[ ! -f "$SOLUTION_FILE" ]]; then
    echo "❌ 文件不存在：$SOLUTION_FILE" >&2
    exit 1
  fi
  SOLUTION_CODE=$(cat "$SOLUTION_FILE")
fi

if [[ -z "$SOLUTION_CODE" ]]; then
  echo "❌ 请提供 --file <path> 或 --code <python_code>" >&2
  exit 1
fi

echo "⚠️  提交将消耗 0.001 Credits（不退款），确认提交？[y/N]"
read -r CONFIRM
if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
  echo "已取消"
  exit 0
fi

# 生成幂等键防止重复提交
IDEMPOTENCY_KEY=$(python3 -c "import uuid; print(str(uuid.uuid4()))")

PAYLOAD=$(python3 -c "
import json, sys
code = sys.stdin.read()
print(json.dumps({'code': code, 'idempotency_key': '$IDEMPOTENCY_KEY'}))
" <<< "$SOLUTION_CODE")

echo "🚀 正在提交解答..."

RESPONSE=$(curl -sf -X POST "${BASE_URL}/bounties/${BOUNTY_ID}/submissions" \
  -H "Authorization: Bearer ${EMERGENCE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

echo "$RESPONSE" | python3 -c "
import json, sys
r = json.load(sys.stdin)
status = r.get('status', '?')
sub_id = r.get('id', '?')
icons = {'pending':'⏳','processing':'🔄','verified':'🔍','accepted':'✅','rejected':'❌','failed':'💥','error':'⚠️'}
icon = icons.get(status, '❓')
print(f'{icon} 提交成功 | 状态：{status.upper()}')
print(f'   提交 ID：{sub_id}')
print(f'   结果通常在数分钟内更新')
print(f'   查看状态：https://emergence.science/bounties/{\"$BOUNTY_ID\"}')
"

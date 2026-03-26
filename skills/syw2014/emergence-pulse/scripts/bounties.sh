#!/usr/bin/env bash
# bounties.sh — 浏览涌现科学悬赏任务列表
# 用法:
#   ./bounties.sh                        # 列出 open 状态，默认 10 条
#   ./bounties.sh --status completed     # 已完成悬赏（学习参考）
#   ./bounties.sh --limit 5              # 限制返回数量
#   ./bounties.sh --id <bounty_id>       # 获取单个悬赏详情
#   ./bounties.sh --my-submissions       # 我的提交记录（需 API Key）
#
# 公开端点无需 API Key

set -euo pipefail

BASE_URL="https://api.emergence.science"
STATUS="open"
LIMIT=10
BOUNTY_ID=""
MY_SUBMISSIONS=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --status)         STATUS="$2"; shift 2 ;;
    --limit)          LIMIT="$2"; shift 2 ;;
    --id)             BOUNTY_ID="$2"; shift 2 ;;
    --my-submissions) MY_SUBMISSIONS=true; shift ;;
    *)                shift ;;
  esac
done

# 查我的提交记录
if $MY_SUBMISSIONS; then
  if [[ -z "${EMERGENCE_API_KEY:-}" ]]; then
    echo "❌ 查看我的提交记录需要 EMERGENCE_API_KEY" >&2
    echo "   获取方式：登录 https://emergence.science/zh → 个人中心 → API Keys" >&2
    exit 1
  fi
  curl -sf "${BASE_URL}/bounties/submissions/me" \
    -H "Authorization: Bearer ${EMERGENCE_API_KEY}" \
    -H "Accept: application/json" | \
    python3 -c "
import json, sys
subs = json.load(sys.stdin)
if not subs:
    print('暂无提交记录')
    sys.exit(0)
for s in subs:
    status_icon = {'accepted':'✅','rejected':'❌','pending':'⏳','processing':'🔄','verified':'🔍','failed':'💥','error':'⚠️'}.get(s.get('status',''),'❓')
    print(f\"{status_icon} [{s.get('status','?').upper()}] Bounty: {s.get('bounty_id','?')[:8]}... | 提交: {s.get('id','?')[:8]}...\")
"
  exit 0
fi

# 获取单个悬赏详情
if [[ -n "$BOUNTY_ID" ]]; then
  curl -sf "${BASE_URL}/bounties/${BOUNTY_ID}" \
    -H "Accept: application/json" | \
    python3 -c "
import json, sys
b = json.load(sys.stdin)
reward = b.get('reward', 0) / 1_000_000
print(f\"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\")
print(f\"💰 {b.get('title','(无标题)')}\")
print(f\"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\")
print(f\"奖励：{reward:.4f} Credits\")
print(f\"状态：{b.get('status','?')}\")
print(f\"语言：{b.get('language','Python')}\")
print(f\"截止：{b.get('expires_at','?')}\")
print()
print(b.get('description',''))
print()
if b.get('template_code'):
    print('--- 模板代码 ---')
    print(b['template_code'])
print(f\"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\")
print(f\"提交：https://emergence.science/bounties/{b.get('id','?')}\")
"
  exit 0
fi

# 列出悬赏
curl -sf "${BASE_URL}/bounties?status=${STATUS}&limit=${LIMIT}" \
  -H "Accept: application/json" | \
  python3 -c "
import json, sys
bounties = json.load(sys.stdin)
if not bounties:
    print(f'暂无 {\"$STATUS\"} 状态的悬赏任务')
    sys.exit(0)
print(f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
print(f'💰 涌现科学 · 悬赏任务 [{\"$STATUS\".upper()}]')
print(f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
for i, b in enumerate(bounties, 1):
    reward = b.get('reward', 0) / 1_000_000
    print(f'#{i}  {b.get(\"title\", \"(无标题)\")}')
    print(f'    奖励：{reward:.4f} Credits | 语言：{b.get(\"language\",\"Python\")}')
    print(f'    ID：{b.get(\"id\",\"?\")[:8]}...')
    print(f'    👉 https://emergence.science/bounties/{b.get(\"id\",\"?\")}')
    print()
print(f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
print(f'全部任务：https://emergence.science/bounties')
"

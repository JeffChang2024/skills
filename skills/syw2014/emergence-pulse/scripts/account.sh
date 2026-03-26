#!/usr/bin/env bash
# account.sh — 查询账户余额和交易记录
# 用法:
#   ./account.sh --balance               # 查看 Credits 余额
#   ./account.sh --transactions          # 查看交易历史
#   ./account.sh --profile               # 查看账户信息
#
# 需要 EMERGENCE_API_KEY

set -euo pipefail

BASE_URL="https://api.emergence.science"

if [[ -z "${EMERGENCE_API_KEY:-}" ]]; then
  echo "❌ 此命令需要 EMERGENCE_API_KEY" >&2
  echo "   获取：登录 https://emergence.science/zh → 个人中心 → API Keys" >&2
  exit 1
fi

case "${1:-}" in
  --balance)
    curl -sf "${BASE_URL}/accounts/balance" \
      -H "Authorization: Bearer ${EMERGENCE_API_KEY}" | \
      python3 -c "
import json, sys
r = json.load(sys.stdin)
balance = r.get('balance', 0) / 1_000_000
print(f'💳 账户余额：{balance:.6f} Credits')
print(f'   微积分（raw）：{r.get(\"balance\", 0):,}')
"
    ;;

  --transactions)
    curl -sf "${BASE_URL}/accounts/transactions" \
      -H "Authorization: Bearer ${EMERGENCE_API_KEY}" | \
      python3 -c "
import json, sys
txns = json.load(sys.stdin)
type_icons = {'transfer':'💸','fee':'💳','refund':'↩️','grant':'🎁'}
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
print('📋 交易记录')
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
for t in txns[:20]:
    icon = type_icons.get(t.get('type',''), '❓')
    amt = t.get('amount', 0) / 1_000_000
    sign = '+' if amt > 0 else ''
    print(f\"{icon} {sign}{amt:.6f} Credits | {t.get('type','?')} | {t.get('created_at','?')[:10]}\")
"
    ;;

  --profile)
    curl -sf "${BASE_URL}/accounts/me" \
      -H "Authorization: Bearer ${EMERGENCE_API_KEY}" | \
      python3 -c "
import json, sys
u = json.load(sys.stdin)
print(f'👤 {u.get(\"username\",\"?\")}')
print(f'   邮箱：{u.get(\"email\",\"?\")}')
print(f'   角色：{u.get(\"role\",\"user\")}')
print(f'   加入：{u.get(\"created_at\",\"?\")[:10]}')
"
    ;;

  *)
    echo "用法:" >&2
    echo "  $0 --balance       查看 Credits 余额" >&2
    echo "  $0 --transactions  查看交易历史" >&2
    echo "  $0 --profile       查看账户信息" >&2
    exit 1
    ;;
esac

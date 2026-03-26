#!/usr/bin/env bash
# preferences.sh — 管理用户订阅偏好（主题、通知时间等）
# 用法:
#   ./preferences.sh --show              # 查看当前偏好
#   ./preferences.sh --set topic=tech_ai,markets
#   ./preferences.sh --set notify_time=08:00
#   ./preferences.sh --set timezone=Asia/Shanghai
#   ./preferences.sh --set bounty_alerts=true
#   ./preferences.sh --reset             # 恢复默认值

set -euo pipefail

PREFS_FILE="${EMERGENCE_PREFS_FILE:-$HOME/.emergence_prefs.json}"
SKILL_PREFS="$(dirname "$0")/../templates/preferences.json"

# 初始化：若不存在则从模板复制
if [[ ! -f "$PREFS_FILE" ]]; then
  if [[ -f "$SKILL_PREFS" ]]; then
    cp "$SKILL_PREFS" "$PREFS_FILE"
  else
    echo '{"subscribed_topics":["all"],"notify_time":"08:00","timezone":"Asia/Shanghai","locale":"zh-CN","bounty_alerts":true}' > "$PREFS_FILE"
  fi
fi

case "${1:-}" in
  --show)
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⚙️  当前偏好设置"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    PREFS_FILE="$PREFS_FILE" python3 - << 'PYEOF'
import json, os
with open(os.environ['PREFS_FILE']) as f:
    p = json.load(f)
topics = ', '.join(p.get('subscribed_topics', ['all']))
print(f'订阅主题：{topics}')
print(f'推送时间：{p.get("notify_time","08:00")} ({p.get("timezone","Asia/Shanghai")})')
print(f'悬赏提醒：{"开启" if p.get("bounty_alerts") else "关闭"}')
print(f'语言：{p.get("locale","zh-CN")}')
PYEOF
    ;;

  --set)
    shift
    # 将每个 key=value 参数写入临时文件，避免 heredoc 里 $@ 展开问题
    ARGS_FILE=$(mktemp)
    printf '%s\n' "$@" > "$ARGS_FILE"
    PREFS_FILE="$PREFS_FILE" ARGS_FILE="$ARGS_FILE" python3 - << 'PYEOF'
import json, os, sys

VALID_TOPICS = {"markets", "finance", "tech_ai", "society", "all"}

prefs_file = os.environ['PREFS_FILE']
args_file  = os.environ['ARGS_FILE']

with open(prefs_file) as f:
    prefs = json.load(f)

with open(args_file) as f:
    args = [line.rstrip('\n') for line in f if '=' in line]

for arg in args:
    key, val = arg.split('=', 1)
    if key == 'topic':
        topics = [t.strip() for t in val.split(',')]
        invalid = [t for t in topics if t not in VALID_TOPICS]
        if invalid:
            print(f"❌ 无效主题：{invalid}，可选：{sorted(VALID_TOPICS)}")
            sys.exit(1)
        prefs['subscribed_topics'] = topics
        print(f"✅ 订阅主题已更新：{topics}")
    elif key == 'notify_time':
        prefs['notify_time'] = val
        print(f"✅ 推送时间已更新：{val}")
    elif key == 'timezone':
        prefs['timezone'] = val
        print(f"✅ 时区已更新：{val}")
    elif key == 'bounty_alerts':
        prefs['bounty_alerts'] = val.lower() in ('true', '1', 'yes')
        print(f"✅ 悬赏提醒：{'开启' if prefs['bounty_alerts'] else '关闭'}")
    elif key == 'locale':
        prefs['locale'] = val
        print(f"✅ 语言已更新：{val}")

with open(prefs_file, 'w') as f:
    json.dump(prefs, f, ensure_ascii=False, indent=2)
PYEOF
    rm -f "$ARGS_FILE"
    ;;

  --reset)
    if [[ -f "$SKILL_PREFS" ]]; then
      cp "$SKILL_PREFS" "$PREFS_FILE"
    else
      echo '{"subscribed_topics":["all"],"notify_time":"08:00","timezone":"Asia/Shanghai","locale":"zh-CN","bounty_alerts":true}' > "$PREFS_FILE"
    fi
    echo "✅ 偏好已重置为默认值"
    ;;

  *)
    echo "用法:"
    echo "  $0 --show"
    echo "  $0 --set topic=tech_ai,markets"
    echo "  $0 --set notify_time=09:00"
    echo "  $0 --set timezone=Asia/Tokyo"
    echo "  $0 --set bounty_alerts=true|false"
    echo "  $0 --reset"
    ;;
esac

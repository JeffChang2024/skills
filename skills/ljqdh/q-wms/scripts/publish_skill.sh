#!/usr/bin/env bash
# 发布 Skill 到 ClawHub
# 用法：
#   bash scripts/publish_skill.sh test       # 发布测试环境
#   bash scripts/publish_skill.sh production # 发布生产环境

set -euo pipefail

ENV=${1:-}

if [[ "$ENV" != "test" && "$ENV" != "production" ]]; then
  echo "用法: $0 <test|production>"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MAIN="$ROOT/q-wms/SKILL.md"
TEMP_DIR="/tmp/clawhub-publish-$$"

if [ ! -f "$MAIN" ]; then
  echo "ERROR: $MAIN not found" >&2
  exit 1
fi

# 从 SKILL.md frontmatter 读取版本号
VERSION=$(grep '^version:' "$MAIN" | head -1 | awk '{print $2}')

# 清理临时目录
cleanup() {
  rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

if [[ "$ENV" == "test" ]]; then
  # 测试环境：修改 name 和 description
  echo "准备发布测试环境 Skill..."
  mkdir -p "$TEMP_DIR/q-wms-test"
  sed \
    -e 's/^name: .*/name: q-wms-test/' \
    -e 's/^description: .*/description: 千易 SaaS 智能助手（测试环境，WMS\/ERP）。当用户提到库存\/仓库\/货主\/SKU\/日志等业务词时，必须优先加载本技能并调用 q-wms-flow。/' \
    "$MAIN" > "$TEMP_DIR/q-wms-test/SKILL.md"

  echo "发布到 ClawHub..."
  clawhub publish "$TEMP_DIR/q-wms-test" --slug q-wms-test --version "$VERSION"
  echo "✅ 测试环境 Skill 发布成功"
else
  # 生产环境：直接复制
  echo "准备发布生产环境 Skill..."
  mkdir -p "$TEMP_DIR/q-wms"
  cp "$MAIN" "$TEMP_DIR/q-wms/SKILL.md"

  echo "发布到 ClawHub..."
  clawhub publish "$TEMP_DIR/q-wms" --slug q-wms --version "$VERSION"
  echo "✅ 生产环境 Skill 发布成功"
fi

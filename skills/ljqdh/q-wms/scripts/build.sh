#!/bin/bash
set -e

ENV=${1:-test}  # 默认测试环境

if [[ "$ENV" != "test" && "$ENV" != "production" ]]; then
  echo "❌ ENV must be 'test' or 'production'"
  exit 1
fi

echo "Building for $ENV environment..."

# 读取环境配置
CONFIG_FILE="config/$ENV.json"
if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "❌ Config file not found: $CONFIG_FILE"
  exit 1
fi

PLUGIN_ID=$(jq -r '.pluginId' "$CONFIG_FILE")
PLUGIN_NAME=$(jq -r '.pluginName' "$CONFIG_FILE")
MANAGED_SKILL_ID=$(jq -r '.managedSkillId' "$CONFIG_FILE")

echo "   Plugin ID: $PLUGIN_ID"
echo "   Plugin Name: $PLUGIN_NAME"
echo "   Skill: $MANAGED_SKILL_ID"

# 创建临时构建目录
BUILD_DIR="/tmp/q-wms-build-$$"
mkdir -p "$BUILD_DIR"

# 复制 Plugin 代码（排除 tgz 和 sha256 文件）
rsync -a --exclude='*.tgz' --exclude='*.sha256' plugin/q-wms-flow/ "$BUILD_DIR/"

# 打包时动态复制 SKILL.md 到 Plugin 内嵌位置
mkdir -p "$BUILD_DIR/skills/q-wms"
if [[ "$ENV" == "test" ]]; then
  sed 's/^name: q-wms$/name: q-wms-test/' SKILL.md > "$BUILD_DIR/skills/q-wms/SKILL.md"
else
  cp SKILL.md "$BUILD_DIR/skills/q-wms/SKILL.md"
fi

# 修改 openclaw.plugin.json
jq --arg id "$PLUGIN_ID" \
   --arg name "$PLUGIN_NAME" \
   --arg skillId "$MANAGED_SKILL_ID" \
   '.id = $id | .name = $name | .managedSkillId = $skillId' \
   "$BUILD_DIR/openclaw.plugin.json" > "$BUILD_DIR/openclaw.plugin.json.tmp"
mv "$BUILD_DIR/openclaw.plugin.json.tmp" "$BUILD_DIR/openclaw.plugin.json"

# 复制运行时配置
cp "$CONFIG_FILE" "$BUILD_DIR/config.runtime.json"

# 打包
mkdir -p dist
if [[ "$ENV" == "test" ]]; then
  PACKAGE_NAME="q-wms-test.tgz"
else
  PACKAGE_NAME="q-wms.tgz"
fi

# 创建 package/ 子目录（openclaw 要求的格式）
PACKAGE_DIR="/tmp/q-wms-package-$$"
mkdir -p "$PACKAGE_DIR/package"
cp -r "$BUILD_DIR"/* "$PACKAGE_DIR/package/"

# 打包
tar -czf "dist/$PACKAGE_NAME" -C "$PACKAGE_DIR" package

# 清理
rm -rf "$PACKAGE_DIR"

# 清理
rm -rf "$BUILD_DIR"

echo "✅ Built: dist/$PACKAGE_NAME"

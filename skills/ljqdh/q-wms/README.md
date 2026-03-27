# Q-WMS 构建与发布指南

## 快速开始

### 发布到 npm

```bash
# 1. 修改版本号
cd plugin/q-wms-flow
npm version patch  # 或 minor/major

# 2. 发布到 npm
npm publish
```

### 发布 Skill 到 ClawHub

```bash
# 测试环境
bash scripts/publish_skill.sh test

# 生产环境
bash scripts/publish_skill.sh production
```

### 本地打包（可选）

```bash
# 打包测试环境
bash scripts/build.sh test

# 打包生产环境
bash scripts/build.sh production
```

---

## 目录结构

```
q-wms/
├── SKILL.md                    # 主 Skill（单一来源）
├── plugin/q-wms-flow/          # Plugin 代码
├── config/                     # 环境配置
│   ├── test.json               # 测试环境
│   └── production.json         # 生产环境
├── dist/                       # 打包产物
│   ├── q-wms-test.tgz
│   └── q-wms.tgz
└── scripts/
    ├── build.sh                # 打包脚本（自动注入 SKILL.md）
    └── publish_skill.sh        # 发布 Skill 到 ClawHub
```

---

## 命名规范

### 测试环境

- **npm 包**: `qianyi-wms-test`
- **Plugin ID**: `q-wms-test`
- **Skill Name**: `q-wms-test`
- **后端地址**: `http://qlink-portal-test.800best.com`

### 生产环境

- **npm 包**: `qianyi-wms` (待发布)
- **Plugin ID**: `q-wms`
- **Skill Name**: `q-wms`
- **后端地址**: `http://qlink-portal.800best.com`

---

## 用户安装指南

### 测试环境

```bash
# 1. 安装 Plugin（从 npm）
openclaw plugins install qianyi-wms-test

# 2. 安装 Skill（从 ClawHub）
clawhub install q-wms-test

# 3. 启用并重启
openclaw plugins enable q-wms-test
openclaw gateway restart
```

### 生产环境

```bash
# 1. 安装 Plugin（从 npm）
openclaw plugins install qianyi-wms

# 2. 安装 Skill（从 ClawHub）
clawhub install q-wms

# 3. 启用并重启
openclaw plugins enable q-wms
openclaw gateway restart
```

---

## 更新指南

### 更新 Plugin

```bash
# 方式 1: 重新安装（推荐）
openclaw plugins uninstall q-wms-test
openclaw plugins install qianyi-wms-test
openclaw gateway restart

# 方式 2: npm 更新
cd ~/.openclaw/extensions/q-wms-test
npm update
openclaw gateway restart
```

### 更新 Skill

```bash
# ClawHub 自动更新（用户开新会话时自动拉取最新版）
clawhub update q-wms-test

# 或手动更新
clawhub install q-wms-test --force
```

---

## 开发流程

### 1. 新增场景

```bash
# 1. 修改主 Skill
vim SKILL.md

# 2. 发布到 ClawHub（测试环境）
bash scripts/publish_skill.sh test
```

### 2. 修改 Plugin 代码

```bash
# 1. 修改代码
vim plugin/q-wms-flow/index.js

# 2. 打包测试版
bash scripts/build.sh test

# 3. 上传到测试服务器
scp dist/q-wms-test.tgz root@test-server:/path/
```

### 3. 发布到生产

```bash
# 1. 测试环境验证通过

# 2. 打包生产版
bash scripts/build.sh production

# 3. 上传到生产服务器
scp dist/q-wms.tgz root@prod-server:/path/

# 4. 发布生产 Skill
bash scripts/publish_skill.sh production
```

---

## 验证

### 验证打包产物

```bash
# 查看包内容
tar -tzf dist/q-wms-test.tgz | head -10

# 验证配置
tar -xzf dist/q-wms-test.tgz -C /tmp/test
cat /tmp/test/config.runtime.json
cat /tmp/test/openclaw.plugin.json | jq '{id, name, managedSkillId}'
```

### 验证安装

```bash
# 安装测试版
openclaw plugins install dist/q-wms-test.tgz

# 查看安装结果
openclaw plugins list
openclaw skills list
```

---

## 注意事项

1. **单一来源原则**：只修改 `SKILL.md`，打包时自动注入
2. **环境隔离**：测试和生产使用不同的 Plugin ID 和 Skill Name
3. **先测试后生产**：所有改动先在测试环境验证，再发布到生产
4. **配置优先级**：用户配置 > 运行时配置 > 默认值

---

## 常用命令

```bash
# 查看当前目录结构
tree -L 3 -I 'node_modules|dist'

# 清理打包产物
rm -rf dist/*

# 查看 Plugin 版本
cat plugin/q-wms-flow/package.json | jq '.version'

# 查看 Skill 版本
head -5 SKILL.md
```

---

## 相关文档

- [10-environment-separation.md](../docs/q-claw/10-environment-separation.md) - 环境分离详细设计
- [09-plugin-skill-backend-architecture.md](../docs/q-claw/09-plugin-skill-backend-architecture.md) - 三层架构规范
- [06-dev-guide.md](../docs/q-claw/06-dev-guide.md) - 开发指南

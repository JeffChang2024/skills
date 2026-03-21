# WorksHub MCP

让 AI Agent 能够雇佣真人工作者完成现实任务。

## 简介

WorksHub MCP 是一个基于 Model Context Protocol 的服务，让 AI Agent（如 Claude、ChatGPT）可以：
- 浏览和搜索真人工作者
- 发布和管理悬赏任务
- 与工作者对话沟通
- 支付并完成任务

**已实现 17 个工具**，覆盖认证管理、技能查询、工作者管理、悬赏任务、对话管理 5 大功能模块。

---

## 安装

### 方式1: 全局安装（推荐）

```bash
npm install -g workshub-mcp
```

### 方式2: 使用 npx（无需安装）

```bash
npx -y workshub-mcp
```

---

## 配置

### 必需环境变量

```bash
export WORKSHUB_API_KEY="your_api_key_here"
```

### 可选环境变量

```bash
export WORKSHUB_API_URL="https://workshub.ai/mcp"  # 默认值
```

### Cursor 配置

编辑 `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "workshub": {
      "command": "npx",
      "args": ["-y", "workshub-mcp"],
      "env": {
        "WORKSHUB_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### Claude Desktop 配置

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "workshub": {
      "command": "npx",
      "args": ["-y", "workshub-mcp"],
      "env": {
        "WORKSHUB_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

---

## 工具列表

### 认证管理（3个工具）

| 工具 | 说明 |
|------|------|
| `send_code` | 发送手机验证码 |
| `login` | 手机号验证码登录（自动创建 API Key） |
| `create_api_key` | 创建 API Key |

### 技能管理（1个工具）

| 工具 | 说明 |
|------|------|
| `get_skills` | 获取技能列表，支持分类和关键词搜索 |

### 工作者管理（3个工具）

| 工具 | 说明 |
|------|------|
| `get_workers` | 获取工作者列表，支持筛选和分页 |
| `get_worker_detail` | 获取工作者详细信息 |
| `get_worker_qrcode` | 获取工作者收款二维码 |

### 悬赏任务管理（6个工具）

| 工具 | 说明 |
|------|------|
| `get_bounties` | 获取悬赏任务列表 |
| `create_bounty` | 创建悬赏任务 |
| `get_bounty_detail` | 获取悬赏任务详情 |
| `cancel_bounty` | 取消悬赏任务 |
| `get_bounty_applications` | 获取任务申请列表 |
| `accept_bounty_application` | 接受工作者申请 |

### 对话管理（4个工具）

| 工具 | 说明 |
|------|------|
| `get_conversations` | 获取所有对话列表 |
| `start_conversation` | 开始与工作者的对话 |
| `get_conversation_messages` | 获取对话消息列表 |
| `send_message` | 发送消息 |

---

## 使用示例

### 发布任务并雇佣工作者

```
1. 创建任务: create_bounty
2. 查看申请: get_bounty_applications
3. 查看申请者: get_worker_detail
4. 接受申请: accept_bounty_application
5. 开始沟通: start_conversation
6. 发送消息: send_message
```

### 搜索并联系工作者

```
1. 搜索工作者: get_workers
2. 查看详情: get_worker_detail
3. 发起对话: start_conversation
4. 发送消息: send_message
```

---

## 许可证

MIT-0

---

## 相关链接

- [WorksHub 官网](https://workshub.ai)
- [GitHub 仓库](https://github.com/workshub/workshub-mcp)
- [MCP 协议文档](https://modelcontextprotocol.io)

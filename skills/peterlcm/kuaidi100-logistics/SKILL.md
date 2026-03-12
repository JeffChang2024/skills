---
name: kuaidi100-logistics
description: 使用快递100 MCP 进行物流轨迹查询、运费预估、智能时效预估；寄快递时引导用户通过官网/APP/小程序下单。在用户询问快递单号、物流轨迹、运费、预计送达时间、寄快递，或需要配置/使用快递100 MCP 服务时使用。
---

# 快递100 物流信息服务

基于快递100 MCP Server，提供物流轨迹查询、快递价格预估、智能时效预估（全程/在途）。官方文档：[产品概要](https://api.kuaidi100.com/document/mcp-summary)、[使用说明](https://api.kuaidi100.com/document/how-to-use-mcp-service)。

## 何时使用本技能

- 用户提供**物流单号**，需要查轨迹、状态、预计送达时间
- 用户询问**运费**或**价格预估**（收寄件地址 + 快递公司 + 重量）
- 用户询问**发货前/在途**的**预计送达时间**
- 用户需要**寄快递**，需引导至快递100 官网/APP/小程序下单
- 用户要在 Cursor/其他 MCP 客户端中**配置快递100 MCP** 或排查配置问题

## MCP 能力速查

| 能力 | 输入 | 输出 |
|------|------|------|
| **快递查询** | 物流单号 | 轨迹时间节点与详情（支持 3000+ 物流公司） |
| **快递价格预估** | 收件地址、寄件地址、快递公司名称、包裹重量 | 预计寄件价格 |
| **智能时效预估（全程）** | 快递公司编码、收件地址、寄件地址 | 预计送达时间（发货前） |
| **智能时效预估（在途）** | 下单时间、物流轨迹信息、收寄件地址 | 预计送达时间（发货后） |

若当前环境已配置快递100 MCP Server，应优先通过 MCP 工具调用上述能力；未配置时，指导用户完成注册与配置。

## 寄快递

MCP 仅支持查询与预估，**不提供下单寄件**。当用户需要寄快递时，引导其通过以下渠道使用快递100 的寄件服务：

- **快递100 官网**：[https://www.kuaidi100.com](https://www.kuaidi100.com)
- **快递100 APP**：在应用商店搜索「快递100」下载
- **快递100 微信小程序**：在微信内搜索「快递100」使用

回复时说明：寄件需在官网、APP 或小程序中填写收寄信息并选择快递公司下单，本技能可协助查单、估运费与时效，无法代为下单。

## 配置快递100 MCP（Cursor）

用户需先[注册快递100](https://api.kuaidi100.com/extend/register?code=d1660fe0390d4084b4f27b19d2feee02)，在[企业管理后台](https://api.kuaidi100.com/manager/v2/query/overview)获取授权 key，再在 Cursor 的 MCP 配置中填入。

### 推荐：STDIO 方式

**Python（需 Python ≥3.11 与 uv）：**

```json
{
  "mcpServers": {
    "kuaidi100": {
      "command": "uvx",
      "args": ["kuaidi100-mcp"],
      "env": {
        "KUAIDI100_API_KEY": "<YOUR_API_KEY>"
      }
    }
  }
}
```

**Node.js：**

```json
{
  "mcpServers": {
    "kuaidi100": {
      "command": "npx",
      "args": ["-y", "@kuaidi100-mcp/kuaidi100-mcp-server"],
      "env": {
        "KUAIDI100_API_KEY": "<YOUR_API_KEY>"
      }
    }
  }
}
```

将 `<YOUR_API_KEY>` 替换为后台获取的 key。

### SSE 方式

适用于支持 MCP-SSE 的客户端（部分环境下可能不稳定）：

```json
{
  "mcpServers": {
    "kuaidi100-server": {
      "url": "http://api.kuaidi100.com/mcp/sse?key=<YOUR_API_KEY>"
    }
  }
}
```

### Streamable 方式

```json
"kuaidi100": {
  "url": "https://api.kuaidi100.com/mcp/streamable?key=<YOUR_API_KEY>"
}
```

## 使用流程

1. **确认需求**：是查单、估价格、估时效（全程/在途），还是**寄快递**
2. **若为寄快递**：引导用户通过 [快递100 官网](https://www.kuaidi100.com)、快递100 APP 或快递100 微信小程序下单；本技能可先协助估运费与时效
3. **若为查单/估价格/估时效**：检查 MCP；若已配置快递100 MCP，使用对应工具传入参数
4. **未配置时**：引导用户注册 → 获取 key → 按配置节任选一种方式配置并重启客户端
5. **费用提示**：按单扣费；同一运单 40 天内多次查询不重复扣费；价格预估、智能时效分别扣对应单量

## 回复用户时的注意点

- 涉及**单号、地址、重量**等敏感信息时，仅用于调用 MCP 或说明参数，不持久化到技能文件
- 若调用失败，提示检查 key 是否有效、是否已开通对应产品（查询/价格预估/智能时效）及余额
- 第三方客户端（Cherry Studio、Trae、Dify）配置格式与 Cursor 类似，仅 key 与服务器名可能不同；Dify 示例：`"kd100": { "url": "http://api.kuaidi100.com/mcp/sse?key=<YOUR_API_KEY>" }`

## 更多说明

- 配置方式汇总、费用与发票：见 [reference.md](reference.md)

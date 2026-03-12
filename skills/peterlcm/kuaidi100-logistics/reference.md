# 快递100 MCP 参考

## 产品与协议

- MCP（Model Context Protocol）为 Anthropic 推出的开放协议，用于 AI 访问与整合外部资源。
- 快递100 提供基于 MCP 的物流信息服务（轨迹查询、价格预估、智能时效等）。

## 能力说明

- **快递查询**：输入物流单号，返回轨迹与时间节点，支持全球 3000+ 物流公司。
- **快递价格预估**：输入收件地址、寄件地址、快递公司名称、包裹重量，返回预计寄件价格。
- **智能时效预估（全程）**：发货前使用；输入快递公司编码、收件地址、寄件地址，返回预计送达时间。
- **智能时效预估（在途）**：发货后使用；输入下单时间、物流轨迹信息、收寄件地址，返回预计送达时间。

## 费用

- **计费**：按单扣费。同一运单 40 天内多次查询不重复扣费。
- **扣量**：快递查询扣查询单量；价格预估扣价格查询单量；智能时效预估扣智能时效预估单量。
- **价格与套餐**：注册后在[企业管理后台](https://api.kuaidi100.com/manager/v2/query/overview)查看并购买相应套餐。
- **发票**：支持增值税发票。后台路径：消费中心 → 支付记录 → 请求开票；可开电子普票或专票，也可通过快递100企业助手小程序开票。

## 第三方客户端配置示例

- **Cherry Studio**：stdio 模式命令 `uvx`，参数 `kuaidi100-mcp`，环境变量 `KUAIDI100_API_KEY=<key>`；SSE 模式 URL：`http://api.kuaidi100.com/mcp/sse?key=<key>`。
- **Trae**：在 MCP 设置中手动配置，格式与 Cursor 的 SSE/stdio 配置一致。
- **Dify**：安装 MCP SSE 插件后，配置示例：`"kd100": { "url": "http://api.kuaidi100.com/mcp/sse?key=<YOUR_API_KEY>" }`。

## 寄快递

MCP 不提供下单寄件。用户寄快递请引导至：

- **官网**：[https://www.kuaidi100.com](https://www.kuaidi100.com)
- **快递100 APP**：应用商店搜索「快递100」
- **快递100 微信小程序**：微信内搜索「快递100」

## 官方链接

- [快递100 官网](https://www.kuaidi100.com)
- [产品概要](https://api.kuaidi100.com/document/mcp-summary)
- [使用说明](https://api.kuaidi100.com/document/how-to-use-mcp-service)
- [注册](https://api.kuaidi100.com/extend/register?code=d1660fe0390d4084b4f27b19d2feee02)
- [Node.js MCP 项目](https://github.com/kuaidi100-api/kuaidi100-MCP-Nodejs)

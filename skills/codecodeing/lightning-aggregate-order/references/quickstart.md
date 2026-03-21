# 汇付聚合支付 — 下单 Skill

基于 dg-lightning-sdk 的聚合支付下单技能，覆盖微信/支付宝/银联全场景。

## 定位

聚合支付下单入口，支持 10 种支付类型（正扫/反扫/JS支付/小程序/APP）。

## 核心内容

- **聚合支付下单**：`v4/trade/payment/create`
- **10 种 trade_type**：T_JSAPI、T_MINIAPP、T_APP、T_MICROPAY、A_JSAPI、A_NATIVE、A_MICROPAY、U_JSAPI、U_NATIVE、U_MICROPAY
- **method_expand 各场景详解**：不同 trade_type 的必填扩展参数
- **前端处理**：二维码生成、JS 调起、付款码扫码

## 参考文件

| 文件 | 内容 |
|-----|------|
| [SKILL.md](SKILL.md) | Skill 定义（Agent 加载入口） |
| [references/aggregate-order.md](references/aggregate-order.md) | 下单接口完整参数 + 各场景代码示例 |

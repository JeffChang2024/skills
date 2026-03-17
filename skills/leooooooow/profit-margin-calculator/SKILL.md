---
name: profit-margin-calculator
description: Calculate true ecommerce profit margin after product cost, shipping, platform fees, discounts, and refund drag. Use when teams need a fast profitability reality check.
---

# Profit Margin Calculator

不要只看毛利，要看最后真正剩下多少。

## 解决的问题

很多团队说“这个产品利润不错”，其实只算了售价减进货价，没把这些算进去：
- 运费和包装；
- 平台手续费；
- 折扣、券、活动补贴；
- 退款和售后损耗；
- 必要时还要分摊基础运营成本。

这个 skill 的目标是：
**把利润率从一个粗数字，变成一张真正能用于经营判断的 margin 拆解。**

## 何时使用

- 对比多个 SKU 利润健康度；
- 定价前确认是否还有空间；
- 发现营收增长但利润不涨时做排查。

## 输入要求

- 售价
- 商品成本
- 运费 / 包装 / 仓储等履约成本
- 平台费 / 支付费 / 渠道费
- 折扣或优惠
- 退款率 / 售后损耗
- 可选：固定成本分摊

## 工作流

1. 计算毛利与毛利率。
2. 扣除履约、渠道、折扣、退款影响。
3. 输出净利润与净利率。
4. 标记利润被侵蚀最严重的环节。

## 输出格式

1. 成本拆解表
2. 毛利 / 净利结果
3. Margin 风险点
4. 优化建议

## 质量标准

- 不混淆 gross margin 和 net margin。
- 清楚指出利润被谁吃掉。
- 结果可用于 SKU 比较或经营复盘。
- 明确哪些数字是估算值。

## 资源

参考 `references/output-template.md`。

---
name: trading-decision-pro-automaton
description: AI-powered trading decision assistant by Automaton. Market sentiment analysis, risk assessment, real-time trade recommendations.
version: 1.0.0
author: Automaton
tags:
  - trading
  - decision-making
  - market-analysis
  - risk-management
  - crypto
  - stocks
  - forex
  - automaton
homepage: https://github.com/openclaw/skills/trading-decision-pro
metadata:
  openclaw:
    emoji: 🧠
    pricing:
      basic: "39 USDC"
      pro: "79 USDC (with advanced signals)"
---

# Trading Decision Pro 🧠

**AI-powered trading decision assistant.**

Market sentiment analysis, risk assessment, and real-time trade recommendations for crypto, stocks, and forex.

---

## 💰 付费服务

**交易决策咨询**:

| 服务 | 价格 | 交付 |
|------|------|------|
| 单次交易分析 | ¥500/次 | 入场点 + 止损 + 目标 |
| 周度策略报告 | ¥2000/周 | 5-10 个交易机会 |
| 月度顾问 | ¥6000/月 | 每日监控 + 每周调整 |
| 定制交易系统 | ¥10000 起 | 完整策略 + 自动化 |

**⚠️ 风险提示**: 交易有风险，不承诺收益。

**联系**: 微信/Telegram 私信，备注"交易决策"

---

## 🎯 What It Solves

Traders struggle with:
- ❌ Emotional decision-making
- ❌ Missing market context
- ❌ Poor risk assessment
- ❌ Information overload
- ❌ No systematic approach

**Trading Decision Pro** provides:
- ✅ Objective AI analysis
- ✅ Real-time sentiment scoring
- ✅ Clear risk/reward ratios
- ✅ Actionable trade setups
- ✅ Position sizing guidance

---

## ✨ Features

### 📊 Market Sentiment Analysis
- Multi-source sentiment aggregation
- Social media sentiment (Twitter, Reddit, Telegram)
- News sentiment analysis
- On-chain metrics (for crypto)
- Fear & Greed Index integration

### 🎯 Trade Signal Generation
- Entry point recommendations
- Stop-loss levels
- Take-profit targets
- Risk/reward ratio calculation
- Confidence scoring (0-100%)

### ⚠️ Risk Assessment
- Position sizing calculator
- Portfolio risk exposure
- Correlation analysis
- Drawdown protection
- Volatility-adjusted stops

### 📈 Technical Analysis
- Multi-timeframe analysis
- Key support/resistance levels
- Trend identification
- Pattern recognition
- Indicator confluence

### 💼 Portfolio Management
- Current position tracking
- P&L monitoring
- Asset allocation suggestions
- Rebalancing alerts
- Performance analytics

### 🔔 Smart Alerts
- Price breakouts
- Sentiment shifts
- Risk threshold breaches
- Take-profit hits
- Stop-loss warnings

---

## 📦 Installation

```bash
clawhub install trading-decision-pro
```

---

## 🚀 Quick Start

### 1. Initialize Decision Engine

```javascript
const { TradingDecisionPro } = require('trading-decision-pro');

const trader = new TradingDecisionPro({
  apiKey: 'your-api-key',
  markets: ['crypto', 'stocks'],  // or 'forex', 'all'
  riskProfile: 'moderate',  // conservative, moderate, aggressive
  maxPositionSize: 0.1  // 10% of portfolio
});
```

### 2. Get Market Sentiment

```javascript
const sentiment = await trader.getSentiment('BTC');
console.log(sentiment);
// {
//   symbol: 'BTC',
//   score: 72,  // 0-100 (bullish)
//   label: 'Bullish',
//   sources: {
//     social: 68,
//     news: 75,
//     technical: 74,
//     onchain: 71
//   },
//   trend: 'improving',
//   confidence: 0.85
// }
```

### 3. Analyze Trade Setup

```javascript
const analysis = await trader.analyzeTrade({
  symbol: 'BTC/USDT',
  direction: 'long',
  entryPrice: 67500,
  stopLoss: 65000,
  takeProfit: 72000
});

console.log(analysis);
// {
//   recommendation: 'ENTER',
//   confidence: 78,
//   riskReward: 1.8,
//   winProbability: 0.65,
//   suggestedSize: 0.08,  // 8% of portfolio
//   reasoning: [
//     'Strong bullish sentiment (72/100)',
//     'Support holding at $65k',
//     'RSI showing bullish divergence',
//     'Volume increasing on up moves'
//   ],
//   warnings: [
//     'High volatility expected in next 4h',
//     'Major resistance at $70k'
//   ]
// }
```

### 4. Get Position Sizing

```javascript
const sizing = await trader.calculatePosition({
  symbol: 'ETH',
  entryPrice: 3500,
  stopLoss: 3300,
  portfolioValue: 10000,
  maxRisk: 0.02  // 2% max loss
});

console.log(sizing);
// {
//   positionSize: 0.57,  // ETH amount
//   positionValue: 1995,  // USD
//   portfolioPercent: 19.95,
//   riskAmount: 114,  // USD at stop
//   riskPercent: 1.14
// }
```

### 5. Monitor Portfolio Risk

```javascript
const risk = await trader.getPortfolioRisk({
  positions: [
    { symbol: 'BTC', size: 0.5, entryPrice: 65000 },
    { symbol: 'ETH', size: 2.0, entryPrice: 3400 }
  ],
  totalValue: 50000
});

console.log(risk);
// {
//   totalExposure: 0.65,  // 65% of portfolio
//   correlationRisk: 'HIGH',
//   maxDrawdown: 0.18,
//   var95: 0.12,
//   recommendations: [
//     'Reduce crypto exposure to <50%',
//     'Add uncorrelated assets',
//     'Consider hedging with stablecoins'
//   ]
// }
```

---

## 💡 Advanced Usage

### Multi-Timeframe Analysis

```javascript
const mtf = await trader.multiTimeframeAnalysis('BTC', {
  timeframes: ['15m', '1h', '4h', '1d'],
  indicators: ['RSI', 'MACD', 'EMA', 'Volume']
});

// Returns confluence score and direction per timeframe
```

### Pattern Recognition

```javascript
const patterns = await trader.detectPatterns('ETH', {
  patterns: ['head-shoulders', 'triangle', 'flag', 'double-top'],
  minReliability: 0.7
});

// Returns detected patterns with reliability scores
```

### News Impact Analysis

```javascript
const impact = await trader.analyzeNewsImpact('BTC', {
  timeRange: '24h',
  sources: ['twitter', 'reddit', 'news', 'telegram']
});

// Returns sentiment impact score and key events
```

### Backtest Strategy

```javascript
const results = await trader.backtest({
  symbol: 'BTC/USDT',
  strategy: 'sentiment-follow',
  startDate: '2025-01-01',
  endDate: '2026-03-19',
  initialCapital: 10000
});

// Returns performance metrics (win rate, Sharpe, max DD, etc.)
```

---

## 🔧 Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `apiKey` | string | required | API key for data sources |
| `markets` | array | ['crypto'] | Markets to analyze |
| `riskProfile` | string | 'moderate' | Risk tolerance |
| `maxPositionSize` | number | 0.1 | Max position as % of portfolio |
| `sentimentSources` | array | all | Which sentiment sources to use |
| `alertChannels` | array | ['console'] | Where to send alerts |

---

## 📊 API Methods

### `getSentiment(symbol)`
Get market sentiment score for a symbol.

### `analyzeTrade(tradeSetup)`
Analyze a specific trade setup with entry, stop, target.

### `calculatePosition(params)`
Calculate optimal position size based on risk.

### `getPortfolioRisk(positions)`
Assess overall portfolio risk exposure.

### `multiTimeframeAnalysis(symbol, options)`
Analyze multiple timeframes for confluence.

### `detectPatterns(symbol, options)`
Detect chart patterns with reliability scoring.

### `analyzeNewsImpact(symbol, options)`
Analyze news and social media impact.

### `backtest(strategy, options)`
Backtest trading strategies.

### `getAlerts()`
Get active alerts and notifications.

### `setAlert(params)`
Create custom price or sentiment alerts.

---

## 📁 File Structure

```
trading-decision-pro/
├── SKILL.md
├── index.js
├── package.json
├── _meta.json
├── README.md
├── src/
│   ├── sentiment.js
│   ├── analysis.js
│   ├── risk.js
│   ├── patterns.js
│   └── alerts.js
└── tests/
    └── trading-decision.test.js
```

---

## 💰 Pricing

| Tier | Price | Features |
|------|-------|----------|
| **Basic** | $39 | Sentiment analysis, trade analysis, position sizing |
| **Pro** | $79 | + Pattern recognition, backtesting, advanced alerts, portfolio risk |

---

## 📝 Changelog

### v1.0.0 (2026-03-19)
- Initial release
- Market sentiment analysis
- Trade setup analyzer
- Position sizing calculator
- Portfolio risk assessment
- Pattern recognition
- Smart alerts
- Backtesting engine

---

## ⚠️ Risk Disclaimer

**Trading involves substantial risk of loss.**

- This tool provides analysis and recommendations, not financial advice
- Past performance does not guarantee future results
- Always do your own research (DYOR)
- Never risk more than you can afford to lose
- Use proper risk management at all times

---

## 📄 License

MIT License - See LICENSE file for details.

---

## 🙏 Support

- GitHub: https://github.com/openclaw/skills/trading-decision-pro
- Discord: OpenClaw Community
- Email: support@openclaw.ai

---

*Built with ❤️ by OpenClaw Agent - Your AI Trading Decision Assistant*

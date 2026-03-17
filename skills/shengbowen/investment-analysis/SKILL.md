---
name: investment-analysis
description: |
  Provides A-share market and stock analysis (index, individual stock trend, buy/sell view) via GF hiAgentChat API. Use when the user asks about 今日大盘、大盘走势、个股走势、某股票怎么样、某股值得买吗、行情分析、股票分析等.
metadata:
  {
    'openclaw':
      {
        'skillKey': 'investment-analysis',
        'requires': { 'env': ['GF_AGENT_COOKIE'] },
        'primaryEnv': 'GF_AGENT_COOKIE',
      },
  }
---

# Investment Analysis (投资分析)

A-share market and stock analysis via GF hiAgentChat API. Use for questions about index, individual stock trend, and simple buy/sell views.

## Quick start

When the user asks about market (大盘), a stock’s trend (走势), or whether a stock is worth buying (值得买吗):

1. Read this skill and ensure `GF_AGENT_COOKIE` is configured.
2. Invoke the script with **only the user’s question** as the argument (no user info, session, or channel context).
3. Use the script stdout as the analysis result to reply or summarize.

## Invocation

**Only pass the user’s question text.** Do not pass user ID, sender, session, or any unrelated context.

```bash
node {baseDir}/scripts/chat.mjs "用户问题"
```

Examples:

```bash
node {baseDir}/scripts/chat.mjs "今日大盘"
node {baseDir}/scripts/chat.mjs "宁德时代走势"
node {baseDir}/scripts/chat.mjs "宁德时代怎么样"
node {baseDir}/scripts/chat.mjs "某股值得买吗"
```

If the question contains spaces, pass it as a single quoted argument.

## Configuration

- **GF_AGENT_COOKIE** (required): Cookie string for hiAgentChat API auth (e.g. `LtpaToken2=...; oauth_token=...`). Set in environment; do not hardcode. Do not commit to repo.
- Node 18+ (for `fetch`).

## Testing

From the skill base dir (or with absolute path to the script):

```bash
# 1. 无 Cookie 时应报错
node scripts/chat.mjs "今日大盘"
# → Missing GF_AGENT_COOKIE (exit 1)

# 2. 配置 Cookie 后请求（把 <your-cookie> 换成真实 Cookie）
GF_AGENT_COOKIE="<your-cookie>" node scripts/chat.mjs "今日大盘"
# → 正常时在 stdout 输出接口返回的 rich_text 拼接结果
```

Cookie 可从浏览器登录 aigctest.gf.com.cn 后，在开发者工具 → Network → 选 hiAgentChat 请求 → Headers → Cookie 复制。

## Ability boundary and skill coordination

- **This skill**: A-share index/individual stock market, trend, and simple buy/sell views (within what the API returns).
- **Not in scope**: Macro reports, futures/forex, or general “search the web for news.” For those, use generic search (e.g. tavily) or other skills.
- **Overlap**: If the user asks both “market view” and “news,” use this skill first for market/trend, then optionally use search for news.

## Output

The script returns the analysis as plain text on stdout. The API is SSE; the script buffers the stream and outputs once. If the platform later supports streaming tools, the script can be adapted to stream.

## When the tool fails (do not retry in a loop)

If the script fails (e.g. **Missing GF_AGENT_COOKIE**, API error, or network error), its output will include a line containing **"Do not retry"**.

- **Do NOT** invoke the tool again for the same user request. Repeating the same failed command will not fix the issue and wastes turns.
- **Do** report the failure to the user once: e.g. "投资分析暂时不可用（可能未配置 Cookie 或接口异常），请稍后再试或检查配置。" and optionally suggest checking `GF_AGENT_COOKIE` or trying again later.
- If you see "Do not retry" in the tool output, treat the request as handled and do not call this skill again in this turn.

## Additional resources

- For API URL, request body, and **response parsing (extendData.section.rich_text)**, see [references/api.md](references/api.md).

---
platform_id: "x-twitter"
platform_name: "X (Twitter)"
auth_methods:
  - type: "cookie_paste"
    priority: 1
    label: "浏览器 Cookie 粘贴（推荐，最稳定）"
  - type: "api_token"
    priority: 2
    label: "X API Bearer Token（需付费 API 套餐）"
capabilities:
  - read_feed
  - read_post
  - search
  - write_reply
  - write_post
  - like
  - send_dm
cookie_guide: "guides/cookie-export-x.md"
session_check:
  method: "browser"
  endpoint: "https://x.com/settings/account"
  success_indicator: "Account information"
estimated_session_duration_days: 30
auto_refresh_supported: true
rate_limits:
  posts_per_day: 50
  replies_per_day: 100
  likes_per_day: 500
  dms_per_day: 50
  requests_per_15min: 75
---

## 认证流程

### Cookie 粘贴认证（推荐）

X/Twitter 对自动化登录有非常严格的反检测机制（TLS 指纹检测、JS 完整性校验、请求载荷混淆），因此 Cookie 粘贴是最可靠的认证方式。

**必要 Cookie 字段**：
- `auth_token`：主认证令牌（40 字符十六进制字符串）
- `ct0`：CSRF 保护令牌

两者必须同时存在，缺一不可。`ct0` 用于所有 POST 请求的 CSRF 验证。

**Cookie 获取步骤**：参见 guides/cookie-export-x.md

**注意事项**：
- 导出 Cookie 后不要在浏览器中退出 X 登录，否则 `auth_token` 会立即失效
- 在其他设备上登录同一账号不会使已有 Cookie 失效
- 启用两步验证可增强账号安全性

### API Token 认证

X API 需要付费套餐才能使用（Free tier 限制非常严格）。

**Free tier 限额**：
- 每月 1,500 条推文读取
- 每月 50 条推文发布
- 不支持搜索 API

**获取步骤**：
1. 访问 https://developer.x.com/en/portal/dashboard
2. 注册开发者账号并选择套餐
3. 创建 Project 和 App
4. 在 App 设置中生成 Bearer Token
5. 将 Bearer Token 提供给 SocialVault

**API Token 验证**：
```
GET https://api.x.com/2/users/me
Authorization: Bearer {bearer_token}
```

成功时返回包含 `data.id` 和 `data.username` 的 JSON。

## 登录态验证

### Cookie 方式（browser 验证）

使用 OpenClaw browser 工具：

1. 注入 `auth_token` 和 `ct0` Cookie 到 `.x.com` 域名
2. 导航至 `https://x.com/settings/account`
3. 等待页面加载

判定逻辑：
- 页面包含 "Account information" → `healthy`
- 重定向到登录页面（URL 包含 `/i/flow/login`）→ `expired`
- 页面显示 "Something went wrong" → `degraded`
- 加载超时 → `unknown`

### API Token 方式

```
GET https://api.x.com/2/users/me
Authorization: Bearer {bearer_token}
```

判定逻辑：
- 响应 200 且包含 `data` → `healthy`
- 响应 401 → `expired`
- 响应 429 → `degraded`（超出频率限制）
- 网络错误 → `unknown`

## 操作指令

所有 browser 操作需先注入 Cookie 并配置浏览器指纹。

### read_feed

**Browser 模式**：
1. 导航至 `https://x.com/home`
2. 等待时间线加载
3. 提取推文列表

**API 模式**（需 Basic 套餐以上）：
```
GET https://api.x.com/2/users/{user_id}/timelines/reverse_chronological
Authorization: Bearer {bearer_token}
```

### read_post

**Browser 模式**：
1. 导航至推文 URL（`https://x.com/{username}/status/{tweet_id}`）
2. 提取推文内容和回复

**API 模式**：
```
GET https://api.x.com/2/tweets/{tweet_id}
Authorization: Bearer {bearer_token}
```

### search

**Browser 模式**：
1. 导航至 `https://x.com/search?q={query}&src=typed_query`
2. 等待搜索结果加载
3. 提取结果列表

**API 模式**（需 Basic 套餐以上）：
```
GET https://api.x.com/2/tweets/search/recent?query={query}
Authorization: Bearer {bearer_token}
```

### write_reply

**Browser 模式**：
1. 导航至目标推文页面
2. 在回复框中输入内容
3. 需在请求头中设置 `x-csrf-token` 为 `ct0` 值
4. 点击发送

### write_post

**Browser 模式**：
1. 导航至 `https://x.com/compose/post` 或点击发推按钮
2. 输入推文内容
3. 点击发送

**API 模式**（Free tier 每月 50 条）：
```
POST https://api.x.com/2/tweets
Authorization: Bearer {bearer_token}
Content-Type: application/json

{"text": "推文内容"}
```

### like

**Browser 模式**：
1. 在推文页面找到点赞按钮
2. 点击操作

### send_dm

**Browser 模式**：
1. 导航至 `https://x.com/messages`
2. 搜索或选择目标用户
3. 输入消息并发送

## 频率控制

| 操作 | 建议频率 | 说明 |
|------|----------|------|
| 浏览页面 | ≤ 30 次/小时 | 过快浏览可能触发"你是机器人吗？"验证 |
| 发推 | ≤ 50 条/天 | 新账号限制更严格 |
| 回复 | ≤ 100 条/天 | 短时间大量回复可能被标记为 spam |
| 点赞 | ≤ 500 次/天 | X 对点赞频率有隐性限制 |
| 私信 | ≤ 50 条/天 | 对未关注你的用户发私信限制更严 |

## 已知问题

1. **TLS 指纹检测**：X 使用先进的 TLS 指纹检测技术，部分自动化浏览器可能被识别。使用 OpenClaw browser 工具时建议配置与导出 Cookie 时一致的浏览器指纹。
2. **CSRF 令牌**：所有 POST 操作（发推、回复、点赞）需在请求头中携带 `x-csrf-token`，值为 `ct0` Cookie 的值。
3. **Cookie 有效期较长**：X 的 `auth_token` 通常有效期约 1-3 个月，但频繁异地访问可能触发安全验证导致提前失效。
4. **新账号限制**：新注册或低活跃度账号发帖和互动有更严格的频率限制。
5. **敏感内容过滤**：含链接或某些关键词的推文可能被自动降权或标记。
6. **API 费用**：X API Free tier 限制极严，实用的自动化操作推荐使用 Cookie + browser 模式。

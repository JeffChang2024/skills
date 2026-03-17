---
platform_id: "reddit"
platform_name: "Reddit"
auth_methods:
  - type: "api_token"
    priority: 1
    label: "Reddit API OAuth（推荐，需提前申请 API 权限）"
  - type: "cookie_paste"
    priority: 2
    label: "浏览器 Cookie 粘贴（适合 browser 操作场景）"
capabilities:
  - read_feed
  - read_post
  - search
  - write_reply
  - write_post
  - like
cookie_guide: "guides/cookie-export-reddit.md"
session_check:
  method: "api"
  endpoint: "https://oauth.reddit.com/api/v1/me"
  success_indicator: "name"
session_check_cookie:
  method: "browser"
  endpoint: "https://www.reddit.com/settings"
  success_indicator: "Account Settings"
estimated_session_duration_days: 14
auto_refresh_supported: true
rate_limits:
  replies_per_day: 30
  posts_per_day: 10
  requests_per_minute: 100
---

## 认证流程

### API Token 认证（推荐）

Reddit 支持 OAuth2 password grant，适合脚本和自动化场景。

**步骤 1：创建 Reddit App 并申请 API 权限**

自 2024 年底起，Reddit 要求所有 API 使用者经过审批流程。

引导用户访问 https://www.reddit.com/prefs/apps 并完成以下操作：

1. 点击页面底部 "create another app..."
2. 填写信息：
   - name: 任意名称（如 "SocialVault"）
   - 选择 "script" 类型
   - redirect uri: `http://localhost:8080`（script 类型不会实际使用）
3. 创建后记录 `client_id`（app 名称下方的字符串）和 `client_secret`
4. **提交 API 使用申请**：说明预期调用量和用途，等待 Reddit 审批（个人项目通常几天内通过）

**步骤 2：获取 Access Token**

使用以下参数发起 POST 请求：

```
POST https://www.reddit.com/api/v1/access_token
Content-Type: application/x-www-form-urlencoded
Authorization: Basic base64(client_id:client_secret)

grant_type=password&username={reddit_username}&password={reddit_password}
```

成功响应：
```json
{
  "access_token": "eyJhbG...",
  "token_type": "bearer",
  "expires_in": 86400,
  "refresh_token": null,
  "scope": "..."
}
```

**注意**：用户密码仅在此步骤使用，获取 token 后立即丢弃，不做任何持久化存储。

**步骤 3：存储凭证**

将 `client_id`、`client_secret`、`access_token` 加密存储。由于 password grant 不返回 refresh_token，token 过期后需重新使用 client_id/client_secret + 用户名密码换取新 token。

### Cookie 粘贴认证

**重要说明**：自 2024 年底起，Reddit 已废弃 Cookie 方式的 API 调用。Cookie 粘贴方式仅适用于通过 browser 工具进行的页面操作（如读取帖子、发表评论等），不能用于直接调用 Reddit API 端点。

**必要 Cookie 字段**：
- `reddit_session`：主会话 Cookie
- `token_v2`：新版认证 Token（JWT 格式）
- `csv`：CSRF 验证相关

至少需要 `reddit_session` 或 `token_v2` 之一。建议同时导出所有 Cookie 以确保兼容性。

**Cookie 验证方式**：Cookie 模式下使用 browser 工具访问 `https://www.reddit.com/settings` 页面，检查是否显示 "Account Settings" 来判断登录态是否有效。

**Cookie 获取步骤**：参见 guides/cookie-export-reddit.md

## 登录态验证

### API Token 方式

发送 GET 请求到 `https://oauth.reddit.com/api/v1/me`，Header 中携带 `Authorization: Bearer {access_token}`。

判定逻辑：
- 响应 200 且 JSON 中包含 `name` 字段 → `healthy`
- 响应 401 → `expired`（token 已失效）
- 响应 403 → `degraded`（可能被限流或封禁）
- 网络错误 → `unknown`

### Cookie 方式（browser 验证）

由于 Reddit 已废弃 Cookie 的 API 调用，Cookie 模式使用 browser 工具验证：

1. 使用 OpenClaw browser 工具打开 `https://www.reddit.com/settings`
2. 注入已存储的 Cookie
3. 等待页面加载完成

判定逻辑：
- 页面标题或内容包含 "Account Settings" → `healthy`
- 页面重定向到登录页面 → `expired`
- 页面加载超时或异常 → `unknown`

## 操作指令

所有 API 操作使用 `https://oauth.reddit.com` 基础 URL（API Token 方式）。

### read_feed

```
GET https://oauth.reddit.com/hot
Authorization: Bearer {access_token}
```

返回首页热门帖子列表。

### read_post

```
GET https://oauth.reddit.com/comments/{post_id}
Authorization: Bearer {access_token}
```

返回指定帖子及其评论。

### search

```
GET https://oauth.reddit.com/search?q={query}&sort=relevance&t=all
Authorization: Bearer {access_token}
```

### write_reply

```
POST https://oauth.reddit.com/api/comment
Authorization: Bearer {access_token}
Content-Type: application/x-www-form-urlencoded

thing_id={parent_fullname}&text={comment_body}
```

`thing_id` 格式为 `t1_xxx`（回复评论）或 `t3_xxx`（回复帖子）。

### write_post

```
POST https://oauth.reddit.com/api/submit
Authorization: Bearer {access_token}
Content-Type: application/x-www-form-urlencoded

sr={subreddit}&kind=self&title={title}&text={body}
```

`kind` 可选 `self`（文本帖）或 `link`（链接帖）。

### like

```
POST https://oauth.reddit.com/api/vote
Authorization: Bearer {access_token}
Content-Type: application/x-www-form-urlencoded

id={thing_fullname}&dir=1
```

`dir`: 1 = 点赞，-1 = 踩，0 = 取消投票。

## 频率控制

| 操作 | 建议频率 | 说明 |
|------|----------|------|
| API 请求 | ≤ 60 次/分钟 | Reddit API 免费档限制 100 次/分钟，建议保守使用 |
| 发帖 | ≤ 10 次/天 | 超频可能触发 spam 过滤 |
| 评论 | ≤ 30 次/天 | 新账号限制更严格 |
| 投票 | ≤ 50 次/天 | 短时间大量投票可能被检测 |

## 已知问题

1. **API 审批要求**：自 2024 年底起，Reddit 取消了自助 API 访问。创建应用后需提交使用说明并等待审批（个人项目通常几天内通过）。
2. **Cookie API 已废弃**：Reddit 已不再支持 Cookie 方式的 API 调用。Cookie 模式仅适用于 browser 操作场景。
3. **新账号限制**：新注册账号（< 30 天或 karma < 10）在某些 subreddit 发帖和评论会被自动拦截。
4. **两步验证**：启用 2FA 的账号使用 password grant 时，密码后需追加 `:TOTP_CODE`。
5. **Token 过期**：password grant 返回的 access_token 有效期为 24 小时，无 refresh_token，需定期使用 client_id/client_secret 重新获取。
6. **rate limit header**：响应中的 `X-Ratelimit-Remaining` 和 `X-Ratelimit-Reset` 可用于动态调整请求频率。
7. **非住宅 IP 限制**：Reddit 对非住宅 IP（如 VPS）有更严格的反爬检测，browser 操作时可能需要使用代理。

# Reddit API Token 获取教程

## 为什么选择 API Token？

API Token 方式比 Cookie 更稳定，支持更细粒度的权限控制，是 Reddit 官方推荐的自动化接入方式。

## 重要提示（2024 年底起的新变化）

自 2024 年底起，Reddit 取消了自助 API 访问。创建应用后需要提交一份使用说明并等待 Reddit 审批。个人和研究项目通常几天内就能通过。

## 第 1 步：创建 Reddit 应用

1. 在浏览器中打开 https://www.reddit.com/prefs/apps
2. 滚动到页面底部，点击 **"create another app..."**
3. 填写应用信息：
   - **name**：给应用起个名字，如 "SocialVault"
   - **App type**：选择 **"script"**（重要！必须选 script 类型）
   - **description**：说明你的用途
   - **about url**：可留空
   - **redirect uri**：填写 `http://localhost:8080`
4. 点击 **"create app"**
5. **提交 API 使用申请**：Reddit 会要求你说明预期的 API 调用量和用途。如实填写即可，个人项目通常几天内审批通过。

## 第 2 步：记录应用凭证

创建成功后，你会看到应用信息页面：

- **client_id**：应用名称正下方的一串字符（如 `a1b2c3d4e5f6g7`）
- **client_secret**：标注为 "secret" 的字段

请将这两个值记录下来，准备告诉 SocialVault Agent。

## 第 3 步：告诉 SocialVault

直接对 SocialVault Agent 说：

> "用 API Token 方式添加 Reddit 账号"

Agent 会依次引导你提供：
1. client_id
2. client_secret
3. Reddit 用户名
4. Reddit 密码（仅用于获取 token，不会存储）

## 安全说明

1. **密码不会被存储**：你的 Reddit 密码仅在获取 API Token 时使用一次，之后立即丢弃。
2. **Token 有效期**：获取的 access_token 有效期为 24 小时。SocialVault 会使用 client_id/client_secret 定期重新获取。
3. **应用类型**：必须选择 "script" 类型。其他类型（web app、installed app）需要不同的认证流程。
4. **两步验证**：如果你的 Reddit 账号开启了两步验证（2FA），在输入密码时需要在密码后面加上 `:TOTP验证码`，例如 `mypassword:123456`。
5. **审批等待**：如果你的 API 申请还在审批中，可以先使用 Cookie 粘贴方式添加账号。

## 常见问题

### Q: 创建应用时没有看到 "create another app" 按钮？
确保你已登录 Reddit，并访问的是 https://www.reddit.com/prefs/apps （不是 new.reddit.com）。

### Q: 获取 Token 时报错 401？
检查 client_id 和 client_secret 是否正确，以及用户名密码是否正确。如果开启了 2FA，密码后需追加验证码。

### Q: Token 突然失效了？
Reddit 的 script 类型应用 Token 有效期为 24 小时。SocialVault 会自动重新获取，如果失败会通知你。

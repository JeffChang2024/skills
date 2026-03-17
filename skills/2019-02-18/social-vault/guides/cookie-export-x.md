# X (Twitter) Cookie 导出教程

## 适用场景

Cookie 是操作 X/Twitter 最推荐的方式。X 的 API 免费档限制非常严格，而 Cookie + 浏览器自动化可以完成几乎所有操作。

## 前置要求

- 一台能打开浏览器的电脑
- Chrome 或 Firefox 浏览器
- 已登录的 X 账号
- 建议：开启两步验证以增强账号安全性

## 方法一：使用 Cookie-Editor 插件（推荐）

### 第 1 步：安装 Cookie-Editor 插件

- Chrome：在 Chrome 应用商店搜索 "Cookie-Editor" 并安装
- Firefox：在 Firefox 附加组件中搜索 "Cookie-Editor" 并安装

### 第 2 步：打开 X 并确认登录

1. 在浏览器中打开 https://x.com
2. 确认已登录（能看到首页时间线）

### 第 3 步：导出 Cookie

1. 点击浏览器工具栏中的 Cookie-Editor 图标
2. 确认显示的是 x.com 的 Cookie
3. 点击 "Export" → 选择 "Export as JSON"
4. Cookie 自动复制到剪贴板

### 第 4 步：粘贴给 SocialVault

将复制的内容粘贴给 SocialVault Agent 即可。

## 方法二：使用开发者工具

### 第 1 步：打开开发者工具

1. 在 x.com 页面按 `F12`
2. 切换到 "Application"（Chrome）或 "Storage"（Firefox）标签

### 第 2 步：找到关键 Cookie

在 Cookies → `https://x.com` 下找到以下两个 Cookie：

| Cookie 名 | 说明 |
|-----------|------|
| `auth_token` | 主认证令牌，40 位十六进制字符串 |
| `ct0` | CSRF 令牌 |

### 第 3 步：复制 Cookie

在 Console 中运行以下代码快速获取：

```
document.cookie
```

复制输出内容粘贴给 SocialVault。

## 注意事项

1. **不要退出登录**：导出 Cookie 后不要在浏览器中退出 X 登录，否则 Cookie 立即失效。
2. **有效期较长**：X 的 `auth_token` 通常有效 1-3 个月，比大多数平台都长。
3. **必要字段**：至少需要 `auth_token` 和 `ct0` 两个 Cookie。
4. **多设备登录**：在其他设备登录同一账号不会使导出的 Cookie 失效。
5. **安全建议**：Cookie 包含你的完整登录权限，请勿分享给他人。SocialVault 会将其加密存储。
6. **异地检测**：如果你的 VPS 和导出 Cookie 的电脑 IP 差异很大，偶尔可能触发安全验证。

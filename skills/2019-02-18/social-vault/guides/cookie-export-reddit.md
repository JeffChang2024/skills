# Reddit Cookie 导出教程

## 适用场景

Cookie 方式适合需要通过浏览器自动化操作 Reddit 的场景（如读取帖子、发表评论等）。如果你的主要需求是 API 调用（如读取数据流、自动发帖），推荐使用 API Token 方式（参见 `api-token-reddit.md`）。

> 注意：自 2024 年底起，Reddit 已废弃 Cookie 方式的 API 调用，Cookie 仅在 browser 操作模式下有效。

## 前置要求

- 一台能打开浏览器的电脑（Windows/Mac/Linux 均可）
- Chrome 或 Firefox 浏览器
- 已登录的 Reddit 账号

## 方法一：使用 Cookie-Editor 插件（推荐）

### 第 1 步：安装 Cookie-Editor 插件

- Chrome 用户：在 Chrome 应用商店搜索 "Cookie-Editor" 并安装
- Firefox 用户：在 Firefox 附加组件中搜索 "Cookie-Editor" 并安装

### 第 2 步：打开 Reddit 并确认登录

1. 在浏览器中打开 https://www.reddit.com
2. 确认页面右上角显示你的用户名，说明已登录
3. 如果未登录，请先完成登录

### 第 3 步：导出 Cookie

1. 点击浏览器工具栏中的 Cookie-Editor 图标
2. 确认左上角显示 "reddit.com"
3. 点击底部的 "Export" 按钮
4. 选择 "Export as JSON" 格式
5. Cookie 内容会自动复制到剪贴板

### 第 4 步：粘贴给 SocialVault

将复制的 Cookie JSON 粘贴给 SocialVault Agent 即可。Agent 会自动识别格式并完成导入。

## 方法二：使用浏览器开发者工具

### 第 1 步：打开开发者工具

1. 在 Reddit 页面按 `F12`（或 `Ctrl+Shift+I` / `Cmd+Option+I`）
2. 切换到 "Application"（Chrome）或 "Storage"（Firefox）标签

### 第 2 步：找到 Cookie

1. 在左侧栏展开 "Cookies"
2. 点击 "https://www.reddit.com"
3. 你会看到所有 Reddit Cookie 的列表

### 第 3 步：复制 Cookie

**简易方式**：在 Console 标签中运行以下代码获取 Cookie header 格式：

```
document.cookie
```

然后复制输出内容粘贴给 SocialVault。

**完整方式**：在 Application 标签中选中所有 Cookie，右键复制。

## 注意事项

1. **Cookie 有效期**：Reddit Cookie 通常有效期约 14 天。过期后需要重新导出。
2. **不要退出登录**：导出 Cookie 后不要在浏览器中退出 Reddit 登录，否则 Cookie 会立即失效。
3. **隐私保护**：Cookie 包含你的登录凭证，请勿分享给他人。SocialVault 会将其加密存储。
4. **必要字段**：Reddit 的关键 Cookie 包括 `reddit_session` 和 `token_v2`，确保导出时包含这些字段。

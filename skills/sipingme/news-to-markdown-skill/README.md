# news-to-markdown-skill

新闻文章转 Markdown，支持三层抓取策略和智能内容提取。

## 安装

```bash
# 安装依赖
npm install

# 可选：安装 Playwright 浏览器（用于动态页面）
npx playwright install chromium
```

## 使用

```bash
# 基本用法
convert-url --url "https://example.com/news/article" --output article.md

# 只要正文，不要元数据
convert-url --url "https://example.com/article" --no-metadata

# 指定内容区域
convert-url --url "https://example.com/article" --selector "article.content"

# 显示详细日志
convert-url --url "https://example.com/article" -v
```

## 三层抓取策略

1. **curl** — 最快（1-3s），用于静态页面
2. **wget** — 备选（2-4s），更好的兼容性
3. **Playwright** — 最慢（5-10s），支持 JavaScript 动态渲染

## 内容提取

- 基于文本密度算法自动识别新闻正文
- 自动提取标题、作者、发布时间
- 自动过滤广告、评论等噪音内容
- 保留图片链接

## 测试

```bash
npm test
```

---
name: news-to-markdown
description: 一键将新闻文章转换为 Markdown，支持双引擎内容提取、智能封面图选择、三层 HTML 抓取策略和多平台专项优化。新增10个平台支持：头条、微信公众号、掘金、简书、CSDN、人人都是产品经理、开源中国、B站专栏、SegmentFault、博客园
version: 2.3.9
author: Ping Si <sipingme@gmail.com>
type: command
requires:
  - node: ">=18.0.0"
  - npm: news-to-markdown@^1.3.9
tags:
  - news
  - markdown
  - converter
  - extractor
  - web-scraping
  - toutiao
  - wechat
  - bilibili
  - csdn
  - cnblogs
  - segmentfault
repository: https://github.com/sipingme/news-to-markdown-skill
core-library: https://github.com/sipingme/news-to-markdown
files:
  - bin/convert-url       # CLI 入口（轻量级包装）
  - package.json
---

# news-to-markdown Skill

## 📋 概述

这是一个专门用于将新闻文章转换为 Markdown 格式的 ClawHub Skill。它结合了智能内容提取和高质量格式转换，能够自动识别新闻正文、过滤噪音内容，并输出格式化的 Markdown 文档。

### 核心特点

1. **双引擎内容提取**：结合 Mozilla Readability + news-extractor-node
   - Readability：完整内容提取，保留图片和多媒体
   - NewsExtractor：元数据提取（标题、作者、时间）
   - 智能选择最佳提取结果
2. **智能封面图选择**：自动提取最佳封面图
   - 优先使用 og:image / twitter:image meta 标签
   - 智能降级到第一张有效图片
   - 完美配合 wechat-md-publisher 等发布工具
3. **三层抓取策略**：curl → wget → Playwright，确保高成功率
4. **多平台支持**：新增10个平台专项优化
   - ✅ 头条
   - ✅ 微信公众号
   - ✅ 掘金
   - ✅ 简书
   - ✅ CSDN
   - ✅ 人人都是产品经理
   - ✅ 开源中国
   - ✅ B站专栏
   - ✅ SegmentFault
   - ✅ 博客园
5. **图片保护**：解决纯图片段落被过滤的问题
6. **高质量输出**：基于 `html-to-markdown-node` 的转换引擎
7. **可扩展架构**：支持自定义平台适配器

这是 [news-to-markdown](https://github.com/sipingme/news-to-markdown) 核心库的轻量级 CLI 包装。

## 🎯 使用场景

### 场景 1：快速保存新闻文章

**用户意图**：
- "帮我保存这篇新闻"
- "把这个链接的文章转成 Markdown"
- "下载这篇文章"

**AI 调用**：
```bash
convert-url --url "https://example.com/news/article" \
            --output "article.md"
```

**输出**：
- 包含元数据的完整 Markdown 文件
- 自动过滤广告和评论
- 收集所有图片链接

### 场景 2：批量采集新闻

**用户意图**：
- "把这些新闻都保存下来"
- "批量下载这个列表的文章"

**AI 调用**：
```bash
# 循环处理多个 URL
for url in "${urls[@]}"; do
  convert-url --url "$url" --output "articles/$(basename $url).md"
done
```

### 场景 3：处理动态网站

**用户意图**：
- "这个网站需要 JavaScript 才能显示内容"
- "页面是动态加载的"

**AI 行为**：
- 自动检测并使用 Playwright
- 等待页面完全加载
- 提取渲染后的内容

### 场景 4：自定义提取

**用户意图**：
- "只要正文，不要其他的"
- "去掉侧边栏和评论"

**AI 调用**：
```bash
convert-url --url "https://example.com/news" \
            --noise ".sidebar,.comments,.ads" \
            --no-metadata
```

## 🔧 命令详解

### convert-url

从 URL 提取新闻并转换为 Markdown。

#### 参数

| 参数 | 类型 | 必需 | 说明 | 示例 |
|------|------|------|------|------|
| `--url` | string | ✅ | 新闻文章的 URL | `https://example.com/news` |
| `--output` | string | ❌ | 输出文件路径 | `article.md` |
| `--selector` | string | ❌ | CSS 选择器，指定提取区域 | `article.content` |
| `--noise` | string | ❌ | 要移除的元素（逗号分隔） | `.ad,.sidebar,.comments` |
| `--no-metadata` | flag | ❌ | 不包含元数据（标题、作者、时间） | - |

#### 返回值

**成功时**：
```json
{
  "success": true,
  "metadata": {
    "title": "文章标题",
    "author": "作者名",
    "publishTime": "2026-03-22 10:30:00",
    "imageCount": 3,
    "contentLength": 1234
  }
}
```

**失败时**：
```json
{
  "success": false,
  "error": "错误信息"
}
```

#### 输出格式

**标准格式**（包含元数据）：
```markdown
# 文章标题

**作者**: 张三  
**发布时间**: 2026-03-22 10:30:00  
**来源**: https://example.com/news/article

---

正文内容...

## 图片列表

- ![](image1.jpg)
- ![](image2.jpg)
```

**简洁格式**（`--no-metadata`）：
```markdown
正文内容...
```

## 🚀 工作流程

### 1. HTML 抓取（三层策略）

```
尝试 curl (最快，1-3秒)
  ↓ 失败
尝试 wget (备选)
  ↓ 失败
使用 Playwright (支持 JS，5-10秒)
  ↓
成功获取 HTML
```

**特点**：
- ✅ 自动选择最快的方式
- ✅ 失败时自动降级
- ✅ 显示当前使用的方法
- ✅ 整体成功率 95%+

### 2. 内容提取

使用 `news-extractor-node` 的文本密度算法：

```javascript
const extractor = new NewsExtractor();
const news = extractor.extract(html, {
  url: url,
  noiseSelectors: ['.ad', '.comment', 'aside']
});
```

**提取内容**：
- 标题（多种策略）
- 作者（正则匹配 + 选择器）
- 发布时间（多种日期格式）
- 正文（文本密度算法）
- 图片（自动收集）

### 3. Markdown 转换

使用 `@siping/html-to-markdown-node`：

```javascript
const markdown = convertString(news.contentHtml, {
  domain: url
});
```

**转换特点**：
- 保留标题层级
- 正确处理列表
- 转换代码块
- 解析相对 URL
- 智能转义

## 📊 性能指标

| 指标 | curl | wget | Playwright |
|------|------|------|------------|
| 速度 | 1-3秒 | 2-4秒 | 5-10秒 |
| 成功率 | 70% | 75% | 95% |
| JS 支持 | ❌ | ❌ | ✅ |
| 资源占用 | 极低 | 低 | 中 |

**整体性能**：
- 平均响应时间：2-5 秒
- 整体成功率：95%+
- 支持网站类型：静态 + SPA

## ⚠️ 注意事项

### 1. 网络要求

- 需要能够访问目标 URL
- 某些网站可能有反爬虫机制
- 建议使用稳定的网络连接

### 2. Playwright 安装

首次使用 Playwright 需要安装浏览器：

```bash
npx playwright install chromium
```

### 3. 网站兼容性

**高兼容性**：
- 主流新闻网站（新浪、网易、腾讯等）
- 技术博客（CSDN、掘金等）
- 官方新闻站

**可能需要调整**：
- 特殊布局的网站（使用 `--selector`）
- 需要登录的网站
- 有严格反爬虫的网站

### 4. 内容准确性

- 文本密度算法对大多数新闻网站准确率高
- 对于特殊布局，可能需要自定义选择器
- 建议检查输出结果

## 🎨 AI 使用指南

### 识别新闻采集需求

**关键词**：
- "保存新闻"、"下载文章"
- "转换为 Markdown"
- "采集内容"、"提取正文"

**URL 特征**：
- 包含 `/news/`、`/article/`
- 新闻网站域名
- 博客文章链接

### 参数选择建议

**默认使用**：
```bash
convert-url --url "$URL" --output "article.md"
```

**用户要求"只要正文"**：
```bash
convert-url --url "$URL" --no-metadata
```

**用户提到"去掉广告/评论"**：
```bash
convert-url --url "$URL" --noise ".ad,.comment,.sidebar"
```

**用户指定"只要某个部分"**：
```bash
convert-url --url "$URL" --selector "article.main-content"
```

### 错误处理

**抓取失败**：
```
建议：
1. 检查 URL 是否正确
2. 尝试在浏览器中打开
3. 检查网络连接
4. 确认 Playwright 已安装
```

**提取失败**：
```
建议：
1. 使用 --selector 指定内容区域
2. 调整 --noise 过滤规则
3. 检查网站是否需要登录
```

## 🔍 常见问题

### Q1: 为什么有些网站抓取失败？

**A**: 可能的原因：
1. 网站需要 JavaScript 渲染（会自动使用 Playwright）
2. 网站有反爬虫机制
3. 需要登录才能访问
4. 网络连接问题

**解决方案**：
- 检查 Playwright 是否已安装
- 尝试在浏览器中打开 URL
- 使用 `--selector` 指定内容区域

### Q2: 提取的内容不准确怎么办？

**A**: 使用自定义选择器：
```bash
convert-url --url "$URL" --selector "article.main-content"
```

### Q3: 如何去除特定元素？

**A**: 使用 `--noise` 参数：
```bash
convert-url --url "$URL" --noise ".ad,.sidebar,.comments"
```

### Q4: 支持哪些网站？

**A**: 
- ✅ 大多数新闻网站（静态 HTML）
- ✅ 技术博客
- ✅ SPA 网站（通过 Playwright）
- ⚠️ 需要登录的网站（不支持）

## 📚 示例对话

### 示例 1: 简单保存

**用户**: "帮我保存这篇新闻 https://example.com/news/ai-breakthrough"

**AI**: 
```
我来帮你保存这篇新闻。

[调用 convert-url --url "https://example.com/news/ai-breakthrough" --output "ai-breakthrough.md"]

✅ 已成功保存到 ai-breakthrough.md

文章信息：
- 标题：AI 技术取得重大突破
- 作者：张三
- 发布时间：2026-03-22
- 图片数量：3 张
```

### 示例 2: 批量处理

**用户**: "把这些新闻都保存下来：[URL1, URL2, URL3]"

**AI**:
```
我来批量保存这些新闻。

正在处理 URL1...
✅ 已保存到 article-1.md

正在处理 URL2...
✅ 已保存到 article-2.md

正在处理 URL3...
✅ 已保存到 article-3.md

全部完成！共保存 3 篇文章。
```

### 示例 3: 自定义提取

**用户**: "只要正文，不要标题和作者信息"

**AI**:
```
好的，我只提取正文内容。

[调用 convert-url --url "$URL" --no-metadata]

✅ 已保存纯正文内容。
```

## 🛠️ 维护说明

### 依赖更新

定期更新依赖以获得最新功能和修复：

```bash
npm update news-extractor-node
npm update @siping/html-to-markdown-node
npm update playwright
```

### 测试

建议定期测试常用网站：

```bash
# 测试主流新闻网站
bash scripts/convert.sh --url "https://news.sina.com.cn/..."
bash scripts/convert.sh --url "https://news.163.com/..."
bash scripts/convert.sh --url "https://tech.qq.com/..."
```

### 日志

脚本会输出详细的执行日志：
- 使用的抓取方式
- 提取的元数据
- 转换结果

## 📞 支持

- GitHub Issues: https://github.com/sipingme/news-to-markdown-skill/issues
- Email: sipingme@gmail.com

---

**版本**: 2.3.9  
**最后更新**: 2026-03-25

## 📝 更新日志

### v2.3.9 (2026-03-25)

#### 修复

- ✅ **封面图重复问题修复**：
  - 修复封面图在正文开头重复出现的问题
  - 自动检测并移除与 frontmatter cover 相同的正文开头图片
  - 比较图片 URL 时忽略查询参数差异
  - 确保推送到微信公众号时不会出现重复图片

#### 依赖更新

- ✅ 升级 `news-to-markdown` 到 v1.3.9

### v2.3.8 (2026-03-24)

#### 新增平台支持（共10个）

- ✅ **头条**（移动端 + PC 端）- v1.2.6
- ✅ **微信公众号** - v1.2.6
- ✅ **掘金** - v1.2.7
- ✅ **简书** - v1.2.8
- ✅ **CSDN** - v1.2.9
- ✅ **人人都是产品经理** - v1.3.0
- ✅ **开源中国** - v1.3.1
- ✅ **B站专栏** - v1.3.2
- ✅ **SegmentFault** - v1.3.3
- ✅ **博客园** - v1.3.4

#### 架构优化

- ✅ **核心库分离**：所有业务逻辑迁移到 `news-to-markdown` 核心库
- ✅ **Skill 精简化**：仅保留 CLI 包装层，专注于 ClawHub 集成
- ✅ **TypeScript 支持**：核心库完全用 TypeScript 重写
- ✅ **平台注册系统**：支持自定义平台适配器注册

#### 依赖优化

- ✅ 依赖数量从 4 个减少到 1 个（仅 `news-to-markdown`）
- ✅ 所有底层依赖由核心库管理
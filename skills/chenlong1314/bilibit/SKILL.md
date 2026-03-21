---
name: bilibit
description: B 站视频下载工具。支持哔哩哔哩视频下载、弹幕下载。用户说"B 站下载"、"哔哩哔哩"、"bilibili"、"下载视频"时使用。无需 API Key。
aliases: [B 站下载，哔哩哔哩下载，bilibili 下载，B 站视频，哔哩哔哩，bilibili,B 站，b 站，视频下载，下载视频，弹幕下载]
homepage: https://github.com/AoturLab/bilibit
metadata:
  openclaw:
    emoji: 🎬
    requires:
      bins: [bbdown, ffmpeg]
---

# 🎬 bilibit - B 站视频下载专家

你的 B 站视频助手！支持下载、搜索、弹幕下载。

---

## 📦 快速安装

```bash
# clawhub
clawhub install bilibit

# npm
npm install -g bilibit
```

---

## 🚀 使用示例

### 下载视频
```bash
bilibit https://b23.tv/BV1xx
```

### 搜索视频
```bash
bilibit search "LOL 集锦"
```

### 下载带弹幕
```bash
bilibit https://b23.tv/BV1xx --danmaku
```

---

## 💬 AI 交互规范（重要！）

### 触发场景

**当用户说这些话时，使用 bilibit**：
- "下载这个 B 站视频" + URL
- "找个 LOL 的 3 分钟视频"
- "B 站下载"
- "哔哩哔哩视频"
- "下载带弹幕的视频"

### 输出格式规范

**搜索结果必须这样展示**：

```
🔍 找到 X 个 B 站视频

1. ⭐ 视频标题
   📺 哔哩哔哩 · 3:25 · UP 主名
   🔗 https://b23.tv/BVxxx
   https://i2.hdslb.com/bfs/archive/xxx.jpg  ← 封面 URL（第 1 个才显示）

2. 视频标题
   📺 哔哩哔哩 · 5:12 · UP 主名
   🔗 https://b23.tv/BVyyy

📌 回复序号下载
```

**禁止行为**：
- ❌ 不要转成表格格式
- ❌ 不要过滤/减少结果
- ❌ 不要重新排序
- ❌ 不要用 `[]()` 包裹 URL

**必须保留**：
- ✅ 封面 URL（单独一行）
- ✅ 原始输出格式
- ✅ 所有搜索结果

---

## 📋 完整命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `bilibit <url>` | 下载视频 | `bilibit https://b23.tv/BV1xx` |
| `bilibit search <关键词>` | 搜索视频 | `bilibit search "LOL"` |
| `bilibit <url> --danmaku` | 下载 + 弹幕 | `bilibit ... --danmaku` |
| `bilibit <url> --quality 4K` | 指定画质 | `bilibit ... --quality 4K` |
| `bilibit history` | 下载历史 | `bilibit history` |

---

## ⚠️ 注意事项

- 仅限个人学习使用
- 大会员画质需要 Cookie
- 弹幕保存为 XML 格式

---

## 🔗 相关链接

- GitHub: https://github.com/chenlong1314/bilibit
- 问题反馈：https://github.com/chenlong1314/bilibit/issues

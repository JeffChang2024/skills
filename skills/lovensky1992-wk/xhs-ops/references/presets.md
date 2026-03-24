# 小红书配图预设（Presets）

预设 = 风格 + 布局 的一键组合。根据内容场景直接选预设，不用分别选风格和布局。

> 预设只是快捷方式。可以用预设后单独覆盖风格或布局。
> 例如：用 `knowledge-card` 但换成科技感风格 → 保留 dense 布局 + 切换风格二。

---

## 预设列表

### 知识/干货类

| 预设 | 风格 | 布局 | 适用场景 | 典型标题 |
|------|------|------|---------|---------|
| `knowledge-card` | 手绘涂鸦 | dense | AI干货、方法论总结、工具合集 | 「5个AI工具让效率翻倍」 |
| `checklist` | 手绘涂鸦 | list | 清单、排行榜、避坑指南 | 「产品经理必备的7个习惯」 |
| `step-guide` | 手绘涂鸦 | flow | 教程、操作流程、工作流 | 「3步搭建你的AI工作流」 |
| `tech-insight` | 科技感 | balanced | AI产品分析、技术趋势、行业观点 | 「ChatGPT为什么改变了PM」 |

### 对比/分析类

| 预设 | 风格 | 布局 | 适用场景 | 典型标题 |
|------|------|------|---------|---------|
| `vs-compare` | 科技感 | comparison | 产品PK、方案选型、before/after | 「传统PM vs AI PM」 |
| `tech-dense` | 科技感 | dense | 技术方案拆解、架构解读 | 「Agent记忆系统全解析」 |

### 叙事/分享类

| 预设 | 风格 | 布局 | 适用场景 | 典型标题 |
|------|------|------|---------|---------|
| `pm-story` | 手绘涂鸦 | balanced | 个人经历、职场故事、成长复盘 | 「从美团到阿里，我学到的3件事」 |
| `cover-hook` | 手绘涂鸦/科技感 | sparse | 封面图、金句卡片、重磅声明 | 「实现在贬值，判断在升值」 |

### 特殊风格类（新增）

| 预设 | 风格 | 布局 | 适用场景 | 典型标题 |
|------|------|------|---------|---------|
| `notion-explainer` | Notion极简线稿（风格三） | balanced / dense | 概念科普、SaaS/效率类、理性调性 | 「一张图看懂Agent记忆系统」 |
| `bold-poster` | 丝网印刷海报（风格四） | sparse | 观点输出、影评书评、重磅声明 | 「AI不会取代PM，但会取代不用AI的PM」 |
| `study-notes` | 手写笔记照片（风格五） | dense | 知识框架整理、学习笔记分享 | 「学霸笔记｜产品经理AI知识体系」 |

---

## 内容信号 → 自动推荐预设

当 Editor Agent 分析内容时，按以下信号自动推荐预设：

| 内容信号关键词 | 推荐预设 | 备选 |
|--------------|---------|------|
| AI工具、效率、方法、技巧、干货、推荐 | `knowledge-card` | `checklist` |
| 排行、Top N、必备、清单、避坑、注意 | `checklist` | `knowledge-card` |
| 步骤、教程、流程、先…再…然后、第一步 | `step-guide` | — |
| AI趋势、产品分析、行业、技术、架构 | `tech-insight` | `tech-dense` |
| vs、对比、区别、优劣、before/after | `vs-compare` | — |
| 拆解、全解析、完全指南、深度 | `tech-dense` | `knowledge-card` |
| 我、经历、故事、复盘、成长、感悟 | `pm-story` | — |
| 金句、一句话、声明、重磅 | `cover-hook` | — |
| 概念、科普、原理、解释、SaaS | `notion-explainer` | `knowledge-card` |
| 观点、影评、书评、海报、声明 | `bold-poster` | `cover-hook` |
| 笔记、框架、知识体系、学霸、考试 | `study-notes` | `knowledge-card` |

**混合信号时**：取第一个匹配的推荐预设。

---

## 预设使用示例

```markdown
## 配图方案

**预设**：knowledge-card（手绘涂鸦 + dense）
**主题**：5个AI产品经理必备工具
**张数**：5 张

| # | 位置 | 布局覆盖 | 内容 |
|---|------|---------|------|
| 1 | Cover | sparse | 标题「5个AI工具让PM效率翻倍」+ 大字冲击 |
| 2 | Content | dense | ChatGPT：4个使用场景 |
| 3 | Content | dense | Cursor + Claude Code：编程提效 |
| 4 | Content | dense | Notion AI + Perplexity：信息整理 |
| 5 | Ending | sparse | 总结 + "你最常用哪个？评论区见" |

注：封面和结尾固定 sparse，中间内容页跟随预设默认布局（dense）。
```

---

## 扩展预设

如需新增预设，在此文件追加一行即可。格式：
`预设名 | 风格 | 布局 | 适用场景 | 典型标题`

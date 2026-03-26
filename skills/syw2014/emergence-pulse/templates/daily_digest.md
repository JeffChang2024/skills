# 每日简报渲染模板

## 用途

此模板定义每日简报的展示格式。`scripts/heartbeat.sh` 拉取内容后，按此格式渲染。

## 标准格式

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 涌现科学 · 每日智能简报
{{DATE}} | emergence.science/zh
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{{SUMMARY_MD_CONTENT}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{{CTA_BLOCK}}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 变量说明

| 变量 | 来源 | 说明 |
|------|------|------|
| `{{DATE}}` | 系统日期 | 格式：`YYYY-MM-DD` |
| `{{SUMMARY_MD_CONTENT}}` | `GET /heartbeat` → `summary_md` 字段 | 按用户偏好过滤主题后的内容 |
| `{{CTA_BLOCK}}` | `templates/cta_bounty.md` | 悬赏行动召唤 |

## 主题板块标识

简报内容按以下标题识别板块（用于主题过滤）：

```
## 📈 市场行情      → topic: markets
## 💼 金融与产业    → topic: finance
## 🤖 科技与 AI    → topic: tech_ai
## 🌍 社会与文化    → topic: society
```

## 精简格式（bounty_alerts = false 时）

```
🌐 {{DATE}} 涌现科学简报

{{SUMMARY_MD_CONTENT}}

💡 悬赏：https://emergence.science/bounties
```

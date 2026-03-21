---
name: media-crawler-local
description: 通过本机 media-agent-crawler HTTP 服务搜集 B站/抖音/YouTube/知乎内容（不依赖 MCP 客户端安装）。当用户要搜集这些平台内容、并已在本机启动应用（默认 http://127.0.0.1:39002）时使用。
---

# media-crawler-local

直接调用本机 HTTP 服务，不走 OpenClaw/Cursor 的 MCP 客户端配置。

## 前置确认

先从用户消息或上下文中提取以下信息，缺少时再询问：

- 操作类型：搜集内容 / 查询归档 / 读取任务数据
- 目标链接或关键词
- 平台（可从链接自动推断）

---

## 工具清单

### B 站系列

| 工具名 | 必填参数 | 说明 |
|---|---|---|
| `crawl_bilibili` | `url` | 视频 URL 或 BV 号 |
| `crawl_bilibili_search` | `keyword` | 按关键词触发搜索结果搜集 |
| `crawl_bilibili_uploader` | `mid` | UP 主纯数字 ID，触发视频列表搜集 |
| `crawl_bilibili_popular` | 无 | 热门视频搜集 |
| `crawl_bilibili_weekly` | 无（可选 `number`） | 每周必看，不传 `number` 则自动取最新一期 |
| `crawl_bilibili_history` | 无（可选 `max/view_at/business/ps/type/page_count`） | 历史记录聚合搜集，不传 `page_count` 时跟随 `dailyRecommendPageCount` |

所有 B 站工具均支持可选 `cookies` 参数（字符串，从浏览器插件获取）。

### 其他平台

| 工具名 | 必填参数 | 说明 |
|---|---|---|
| `crawl_douyin` | `url` | 抖音视频 URL |
| `crawl_youtube` | `url` | YouTube 视频 URL 或视频 ID |
| `crawl_zhihu` | `url` | 知乎问题或回答 URL |

### 归档与数据读取

| 工具名 | 必填参数 | 可选参数 | 说明 |
|---|---|---|---|
| `list_archives` | 无 | `platform` / `keyword` / `limit` / `sort_by` / `created_after` | 列出归档任务，默认返回最多 50 条，按时间倒序 |
| `get_task_data` | `task_id` | `type` | 读取任务目录下的数据文件 |

`list_archives` 参数说明：
- `sort_by`：`date`（默认，创建时间倒序）或 `status`（running → failed → unknown → finished）
- `created_after`：ISO 日期，如 `2026-03-18` 或 `2026-03-18T10:00:00Z`

`get_task_data` 的 `type` 支持以下值（含别名）：

| type 值 | 读取的数据 |
|---|---|
| `comments` / `comment` | 评论数据 |
| `danmaku` | 弹幕数据 |
| `subtitles` / `subtitle` / `caption` / `captions` | 字幕数据 |
| `detail` / `info` | 视频/帖子详情 |
| `all` / `full` | 全量聚合数据 |
| `summary` / `ai_summary` | AI 摘要 |
| 不传 | 返回目录下所有可识别文件 |

---

## HTTP 端点

服务地址默认 `http://127.0.0.1:39002`，可通过环境变量 `BIL_CRAWL_URL` 覆盖。

### 搜集端点（REST）

```
POST /start-crawl/{platform}/{encodedUrl}
Content-Type: application/json

{ "source": "ai" }
```

`encodedUrl` 需要 `encodeURIComponent` 编码；`platform` 取值：`bilibili` / `douyin` / `youtube` / `zhihu`。

### MCP 端点（JSON-RPC 2.0）

```
POST /mcp
Accept: application/json, text/event-stream
Content-Type: application/json
```

请求体格式：
```json
{ "jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": { "name": "<tool>", "arguments": { } } }
```

---

## 脚本用法

所有脚本位于 `skills/media-crawler-local/scripts/`，工作目录为 openclaw workspace 根。

### 1. 快速搜集（REST，`crawl.sh`）

```bash
bash skills/media-crawler-local/scripts/crawl.sh <platform> <url> [base_url]
```

示例：
```bash
bash skills/media-crawler-local/scripts/crawl.sh bilibili "https://www.bilibili.com/video/BV1xx411c7mD"
```

### 2. 通过 MCP 搜集（`crawl_mcp.sh`，仅支持带 url 的工具）

```bash
bash skills/media-crawler-local/scripts/crawl_mcp.sh <tool_name> <target_url> [base_url]
```

示例：
```bash
bash skills/media-crawler-local/scripts/crawl_mcp.sh crawl_bilibili "https://www.bilibili.com/video/BV1xx411c7mD"
```

支持工具：`crawl_bilibili` / `crawl_douyin` / `crawl_youtube` / `crawl_zhihu`

> 其余工具（bilibili_search / bilibili_uploader / bilibili_popular / bilibili_weekly / bilibili_history / list_archives / get_task_data）请用 `mcp_tool.sh`。

### 3. 归档查询（`list_archives_mcp.sh`）

```bash
bash skills/media-crawler-local/scripts/list_archives_mcp.sh [platform] [keyword] [limit] [base_url]
```

示例：
```bash
bash skills/media-crawler-local/scripts/list_archives_mcp.sh bilibili "蛋神" 20
```

### 4. 通用工具调用（`mcp_tool.sh`）

```bash
bash skills/media-crawler-local/scripts/mcp_tool.sh <tool_name> [args_json] [base_url]
```

示例：
```bash
# B 站搜索
bash skills/media-crawler-local/scripts/mcp_tool.sh crawl_bilibili_search '{"keyword":"蛋神"}'

# UP 主视频列表
bash skills/media-crawler-local/scripts/mcp_tool.sh crawl_bilibili_uploader '{"mid":"123456"}'

# 热门视频
bash skills/media-crawler-local/scripts/mcp_tool.sh crawl_bilibili_popular '{}'

# 每周必看（最新一期）
bash skills/media-crawler-local/scripts/mcp_tool.sh crawl_bilibili_weekly '{}'

# 每周必看（指定期数）
bash skills/media-crawler-local/scripts/mcp_tool.sh crawl_bilibili_weekly '{"number":364}'

# 历史记录（默认参数）
bash skills/media-crawler-local/scripts/mcp_tool.sh crawl_bilibili_history '{}'

# 历史记录（指定首屏 cursor）
bash skills/media-crawler-local/scripts/mcp_tool.sh crawl_bilibili_history '{"max":0,"view_at":0,"business":"","ps":20,"type":"all"}'

# 历史记录（指定采集页数）
bash skills/media-crawler-local/scripts/mcp_tool.sh crawl_bilibili_history '{"page_count":2}'

# 读取任务评论数据
bash skills/media-crawler-local/scripts/mcp_tool.sh get_task_data '{"task_id":"BV1xx411c7mD-123456","type":"comments"}'
```

---

## 执行流程

1. **健康检查**：`GET /`（连不上则提醒用户先启动应用）。
2. **发起搜集**：优先用 REST 端点（`crawl.sh`），需要额外工具参数时用 MCP（`mcp_tool.sh`）。
3. **结果处理**：
   - 给用户简要摘要（任务 ID、状态、关键字段）
   - 内容很多时仅展示前几条，说明可通过 `get_task_data` 继续读取或过滤

---

## 故障处理

| 错误 | 处理方式 |
|---|---|
| 连接失败 | 提醒先启动 Electron 应用（`bun run start` / `dev`） |
| 401 / 403 | 提示检查 cookies 是否已在 store 中，或让用户重新从插件导入 |
| 429 | 按返回的 `Retry-After` 退避，不密集重试 |
| 5xx | 最多重试 1 次，返回错误摘要与建议 |
| `task_id` 不存在 | 先用 `list_archives` 查询正确的任务 ID |

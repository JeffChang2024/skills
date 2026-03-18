---
name: aippt-marketing
description: |
  使用小方同学生成营销方案 PPT。

  当用户提到以下意图时使用此技能：
  「生成营销方案」「写营销方案」「营销策划」「做个方案」
  「帮我做PPT」「生成策划案」「写个推广方案」

  支持：文本主题输入、文件/链接解析、多轮交互编辑、风格选择、自动生成 PPT 图片。
metadata:
  openclaw:
    requires:
      browser: true
    baseUrl: https://www.aippt.cn/api/marketing
    homepage: https://www.aippt.cn
---

# 小方同学营销方案生成

## 必读约束

### Base URL

```
https://www.aippt.cn/api/marketing
```

### 认证方式

```
Authorization: Bearer AUTH_TOKEN
```

Token 从浏览器 localStorage 动态获取（key: `login_result_token`），详见 [references/api-details.md](references/api-details.md)。

---

### 首次使用提醒

**首次使用时，必须提醒用户**：

> 使用小方同学营销方案功能需要会员积分。如果您还没有购买，请先前往 [小方同学个人中心](https://www.aippt.cn/personal-center?is_from=marketing) 购买会员积分，然后再开始生成方案。

- 每次会话第一次触发此技能时，都要展示此提醒
- 用户确认已有积分或明确表示继续后，再执行后续流程
- 若 API 返回积分不足相关错误，再次引导用户前往购买

---

### 操作规则

- 首次使用必须先完成登录，获取 AUTH_TOKEN 后才能调用 API
- 每一步都必须检查 `code == 0`，非 0 时展示 `msg` 给用户
- 若 API 返回 `code == 14006`，Token 过期，需重新登录
- **API 报错直接告知用户**，不要自行排查。将错误码和信息原样展示
- **用户输入含文件或链接时，必须先解析内容再调接口**（见第二步）
- `text_task_id`、`thread_id`、`message_seq` 必须从上一步返回中提取，不可编造
- **多轮交互规则**：每轮 interrupt 必须展示给用户并等待反馈，禁止自动发送 accepted/edit
- **超时设置**：普通阶段 `--max-time 300`；生图提示词 `--max-time 900`
- **图片轮询**：间隔 15 秒，直到全部完成

---

## 快速决策

| 用户意图 | 执行步骤 |
|---------|---------|
| 「生成营销方案」（无主题） | 提醒积分 → 询问主题 → 第一步起 |
| 「帮我做XX方案」（有主题） | 提醒积分 → 第一步起 |
| 「根据这个链接做方案」 | 提醒积分 → WebFetch 解析 → 第一步起 |
| 「根据这个文件做方案」 | 提醒积分 → Read 解析 → 第一步起 |
| 用户确认/编辑某阶段 | 发送 accepted/edit → 获取下一阶段 |
| 用户选择风格 | 发送风格 → 获取生图提示词 → 轮询图片 |

---

## 执行流程

### 第一步：登录与获取 Token

用 `browser_navigate` 打开 `https://www.aippt.cn`，用 `browser_evaluate` 检查 localStorage 中的 `login_result_token`。

- 已登录 → 保存 Token，跳到第二步
- 未登录 → 引导微信扫码登录（详见 [references/api-details.md](references/api-details.md#登录与-token-获取)）

验证 Token：
```bash
curl -s 'https://www.aippt.cn/api/user/info' \
  -H 'authorization: Bearer AUTH_TOKEN'
```
`code: 0` 有效；`code: 14006` 过期需重新登录。

---

### 第二步：获取用户输入

如果用户只说"生成营销方案"而没给具体主题，询问：
> 请告诉我营销方案的主题，例如："双十一电商大促方案"、"新品上市推广策略"等。

**解析用户附带的文件或链接**：

| 输入类型 | 处理方式 |
|---------|---------|
| 本地文件（`.pdf`、`.docx`、`.txt`、`.md`） | 用 `Read` 读取，提取关键信息作为 `reference_content` |
| 网络链接（`http://`、`https://`） | 用 `WebFetch` 抓取，提取关键信息作为 `reference_content` |
| 图片文件（`.png`、`.jpg`） | 用 `Read` 读取图片，识别文字信息 |

解析后：主题作为第三步 `title`，内容摘要（≤ 2000 字）填入第四步 `messages`。

---

### 第三步：创建项目

```bash
curl -s -X POST 'https://www.aippt.cn/api/marketing/create' \
  -H 'authorization: Bearer AUTH_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "用户输入的主题",
    "reference_content": "",
    "is_regeneration": false,
    "senior_options": "",
    "type": 25
  }'
```

**提取**：`data.id` → `text_task_id`

---

### 第四步：创建生成任务

```bash
curl -s -X POST 'https://www.aippt.cn/api/marketing/task/create' \
  -H 'authorization: Bearer AUTH_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "messages": [{"role": "user", "content": "用户输入的主题"}],
    "text_task_id": TEXT_TASK_ID,
    "resources": []
  }'
```

**提取**：`data.thread_id` 和 `data.message_seq`

---

### 第五步：多轮交互循环（核心流程）

进入 **"获取结果 → 展示 → 用户确认/编辑"** 的循环。共 6 轮 interrupt，每轮可编辑重复。

详细阶段说明见 [references/api-details.md](references/api-details.md#多轮交互阶段说明)。

#### 获取阶段结果

```bash
curl -s --max-time 300 'https://www.aippt.cn/api/marketing/task/result?thread_id=THREAD_ID&message_seq=MESSAGE_SEQ&include_start_message=false' \
  -H 'authorization: Bearer AUTH_TOKEN'
```

拼接所有 `message_chunk` 的 `content` 得到完整内容。收到 `interrupt` 后展示给用户。

#### 用户确认（accepted）

```bash
curl -s -X POST 'https://www.aippt.cn/api/marketing/task/create' \
  -H 'authorization: Bearer AUTH_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "thread_id": "THREAD_ID",
    "interrupt_feedback": "accepted",
    "messages": [{"role": "user", "content": "", "is_hidden": true}],
    "text_task_id": TEXT_TASK_ID
  }'
```

#### 用户要求修改（edit）

```bash
curl -s -X POST 'https://www.aippt.cn/api/marketing/task/create' \
  -H 'authorization: Bearer AUTH_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "thread_id": "THREAD_ID",
    "interrupt_feedback": "edit",
    "messages": [{"role": "user", "content": "用户的修改意见"}],
    "text_task_id": TEXT_TASK_ID
  }'
```

edit 后用返回的新 `message_seq` 再次获取结果（重复当前阶段），直到用户确认。

循环直到收到 `agent: "marketing_picture_style"` 的 interrupt → 进入第六步。

---

### 第六步：选择美化风格

收到 `marketing_picture_style` interrupt 后，向用户展示风格选项（详见 [references/api-details.md](references/api-details.md#风格选项)）：

- **风格类型**：企业品牌风格 / 行业风格 / 经典风格
- **PPT 页数**：智能页数（默认）/ 10-20 / 21-40 / 41-60 / 自定义

等用户选择后发送：

```bash
curl -s -X POST 'https://www.aippt.cn/api/marketing/task/create' \
  -H 'authorization: Bearer AUTH_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "thread_id": "THREAD_ID",
    "interrupt_feedback": "accepted",
    "messages": [{"role": "user", "content": "用户选择的风格和页数", "is_hidden": true}],
    "text_task_id": TEXT_TASK_ID
  }'
```

---

### 第七步：获取生图提示词与 job_id

```bash
curl -s --max-time 900 'https://www.aippt.cn/api/marketing/task/result?thread_id=THREAD_ID&message_seq=MESSAGE_SEQ&include_start_message=false' \
  -H 'authorization: Bearer AUTH_TOKEN'
```

> 此步骤耗时较长（5-10 分钟），提前告知用户"正在生成图片提示词，请稍候..."。

**关键**：`job_id` 嵌套在 `content` 的 JSON 字符串内，需二次解析。详见 [references/api-details.md](references/api-details.md#job_id-二次解析)。

---

### 第八步：获取生成的图片

```bash
curl -s 'https://www.aippt.cn/api/marketing/image/gen/job/result?job_ids=JOB_IDS&task_id=TEXT_TASK_ID' \
  -H 'authorization: Bearer AUTH_TOKEN'
```

间隔 15 秒轮询，直到 `task_job_status: "done"`。详见 [references/api-details.md](references/api-details.md#图片轮询策略)。

全部完成后，用 Markdown 图片语法逐页展示给用户（直接显示图片，不要只发链接）：

```
![第1页](IMAGE_URL_1)
![第2页](IMAGE_URL_2)
...
```

---

## 参数依赖关系

```
第一步 login → AUTH_TOKEN
         ↓
第三步 create → text_task_id
         ↓
第四步 task/create → thread_id, message_seq
         ↓
第五步 多轮交互循环（6 轮 interrupt，每轮可 edit 重复）
         ↓
第六步 用户选择风格 → accepted + 风格名称
         ↓
第七步 task/result → 提取 job_id（content 内 JSON 二次解析）
         ↓
第八步 image/gen/job/result → 轮询获取图片 URL
```

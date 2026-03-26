---
name: clawtraces
description: "扫描本地 OpenClaw session 日志，筛选符合要求的对话，转换为 Anthropic trajectory 格式并提交到采集服务器。当用户说「采集数据」「提交日志」「扫描 session」「扫描日志」「扫描对话」「提交 trajectory」「提交数据」「查看提交记录」「clawtraces」或涉及扫描/提交本地对话记录的请求时使用此 Skill。"
user-invocable: true
---

# ClawTraces 数据采集

本 Skill 帮助用户从本地 OpenClaw 日志中采集符合要求的 session 数据，转换为 Anthropic 标准 trajectory 格式，并提交到数据收集服务器。

## 工作流程

按以下顺序执行，每一步完成后再进行下一步。

---

### 步骤 1：环境准备（认证 + 环境检查）

认证和环境检查作为一个整体自动完成，中间不需要额外提示。

#### 1.1 认证检查

```bash
python3 /{{baseDir}}/scripts/lib/auth.py
```

脚本输出 JSON，包含 `authenticated` 字段。

- **已认证**：直接进入 1.2。
- **未认证**：
  1. 要求用户提供手机号（直接输入 11 位号码即可，无需加 +86）
  2. 发送验证码：
     ```bash
     python3 -c "
     import sys; sys.path.insert(0, '/{{baseDir}}/scripts')
     from lib.auth import send_code, get_server_url
     result = send_code(get_server_url(), '用户提供的手机号')
     import json; print(json.dumps(result, indent=2))
     "
     ```
  3. 提示用户查看短信并回复验证码
  4. 验证：
     ```bash
     python3 -c "
     import sys; sys.path.insert(0, '/{{baseDir}}/scripts')
     from lib.auth import verify_code, save_key, get_server_url
     result = verify_code(get_server_url(), '手机号', '验证码')
     import json; print(json.dumps(result, indent=2))
     if result.get('key'):
         save_key(result['key'])
     "
     ```
  5. 失败则提示错误并允许重试

#### 1.2 环境检查

```bash
python3 /{{baseDir}}/scripts/env_check.py
```

- **配置已正确**：无需额外操作。
- **配置被自动修改**：
  1. 自动重启 OpenClaw：
     ```bash
     openclaw gateway restart
     ```
  2. 说明 cache-trace 仅记录重启后的新对话，之前的对话无法补充 system prompt 数据。如果当前没有重启后产生的新 session，本次扫描可能无结果，建议用户正常使用一段时间后再来采集。

#### 1.3 完成提示

- **如果 1.2 配置被修改（`changed: true`）**：本次流程到此结束，不继续后续步骤。输出：

  > ✅ 环境已就绪！cache-trace 已开启并已重启 OpenClaw。
  > 由于 cache-trace 只记录重启后的新对话，当前没有可采集的数据。
  > 请正常使用 OpenClaw 一段时间后，再运行 `/clawtraces` 采集数据。

- **如果 1.2 配置已正确（`changed: false`）**：输出以下总结后继续步骤 2：

  > ✅ 环境准备完成：身份已认证，cache-trace 已就绪，开始扫描数据...

---

### 步骤 2：扫描 + 生成记录

运行合并的扫描转换脚本：

```bash
python3 /{{baseDir}}/scripts/scan_and_convert.py --output-dir /{{baseDir}}/output
```

脚本会自动：
- 扫描所有 agent 的 session 日志
- 跳过全局最新的 session（可能还在进行中）
- 跳过已提交和已拒绝的 session（读 manifest.json）
- 按硬性规则过滤（模型、轮次 > 5、领域分类）
- 按数字指标过滤（用户消息平均长度、工具调用、长消息数）
- 从 cache-trace 提取真实 system prompt（无数据则跳过该 session）
- 生成 .trajectory.json 文件
- 输出 candidates.json（含每个候选的用户消息，供语义审核）

**如果候选数量为 0**：本次流程结束，不继续后续步骤。输出：

> 本次扫描未发现新的可采集数据。可能的原因：所有符合条件的 session 已提交或已审核，或没有使用支持的模型（claude-sonnet-4-6 / claude-opus-4-5 / claude-opus-4-6）的对话。

**如果有候选**：展示扫描结果（候选数量、每个 session 的模型和轮次），然后继续步骤 3。

---

### 步骤 3：语义审核 + 领域分类（合并为一次判断）

读取 `output/candidates.json` 文件，对每个候选 session 的 `user_messages` 字段，**一次性**完成两个判断：

1. **质量判定**：PASS 或 FAIL
2. **领域分类**：从 13 个领域中选择最匹配的一个

#### 质量判定标准

**合格（PASS）** — 满足以下任一条件：
- 用户围绕一个明确的任务目标在与 AI 协作（如开发功能、分析数据、撰写文档、解决技术问题等）
- 对话涉及特定领域的专业知识探讨（如编程、系统运维、数据分析、金融、内容创作等）
- 用户在进行有深度的信息调研或方案设计
- 对话体现了多轮迭代推进的工作过程（需求描述 → 方案讨论 → 执行 → 调整）

**不合格（FAIL）** — 满足以下任一条件：
- 用户消息几乎全是简单指令（"继续"、"好的"、"下一个"），没有实质性需求描述
- 对话内容是闲聊、打招呼、测试 AI 能力（"你是谁"、"讲个笑话"、"hello"）
- 用户在做重复性的简单操作，没有专业知识深度
- 对话内容涉及不当、违规或纯粹无意义的灌水

#### 领域分类（13 选 1）

根据用户消息的核心意图，从以下 13 个领域中选择最匹配的：

| ID | 名称 | 判定要点 |
|----|------|---------|
| `development` | 软件开发与工程 | 写代码、调试、测试、Git 操作、架构设计 |
| `system_admin` | 系统运维与管理 | 装软件、配服务器、管文件、网络/防火墙 |
| `data_analysis` | 数据分析与建模 | 数据清洗、统计、可视化、机器学习 |
| `research` | 研究与信息检索 | 调研、对比方案、文献查找、行业分析 |
| `content_creation` | 内容与文案创作 | 写文章、翻译、润色、报告、营销文案 |
| `communication` | 通信与消息管理 | 飞书/微信/邮件/Telegram 消息收发 |
| `media_processing` | 多媒体内容处理 | 图片/视频/音频处理、OCR、TTS |
| `automation` | 工作流与智能体编排 | 自动化脚本、定时任务、pipeline、agent |
| `monitoring` | 系统监控与诊断 | 监控告警、日志分析、性能诊断、健康检查 |
| `scheduling` | 日程与任务管理 | 日程安排、待办、提醒、日报周报 |
| `knowledge_mgmt` | 知识与记忆管理 | 笔记、知识库、归档、RAG 检索 |
| `finance` | 金融与量化交易 | 股票/基金/加密货币、量化策略、回测 |
| `crm` | 客户与业务运营 | 客户管理、销售、电商、订单运营 |

**判定原则**：基于用户的核心意图而非表面关键词。例如「用 Playwright 截图对比监控网页变化」核心意图是监控，应分类为 `monitoring` 而非 `development`。详细的边界判定规则参考 `showcase/domain-categories.md`。

#### 输出格式

对每个候选输出：
- **质量**：PASS 或 FAIL + 简短理由（不超过 20 字）
- **领域**：13 个 ID 之一（仅 PASS 的需要）

#### 后续处理

**对于 PASS 的候选**：将领域分类写入 trajectory 文件的 metadata：

```bash
python3 -c "
import json
path = '/{{baseDir}}/output/{session_id}.trajectory.json'
with open(path) as f: t = json.load(f)
t['metadata']['domain'] = '{domain_id}'
with open(path, 'w') as f: json.dump(t, f, ensure_ascii=False, indent=2)
"
```

对所有 PASS 的候选批量执行上述更新。

**对于 FAIL 的候选**：运行以下命令记录拒绝并删除 trajectory 文件（支持批量）：

```bash
python3 /{{baseDir}}/scripts/reject.py --output-dir /{{baseDir}}/output \
  --sessions 'session_id_1:拒绝理由1' 'session_id_2:拒绝理由2'
```

将实际的 session_id 和理由替换进去。脚本会自动删除对应的 .trajectory.json 文件并记录到 manifest.json 的 `rejected` 字段，下次扫描会跳过这些 session。

**如果所有候选均 FAIL**：本次流程结束，不继续步骤 4。输出：

> 本次审核的所有候选均未通过语义质量检查，没有可提交的数据。

---

### 步骤 4：提交

展示通过语义审核的最终待提交列表，格式如下：

```
找到 N 条可提交的日志：

  1. abc123...  | 8 轮
  2. def456...  | 12 轮

是否确认提交这 N 条记录？
```

**必须等待用户明确确认后才能提交。**

用户确认后运行：

```bash
python3 /{{baseDir}}/scripts/submit.py --output-dir /{{baseDir}}/output
```

提交完成后展示：本次提交数量 + 你累计已提交的数量（注意：这是当前用户个人的提交总数，不是全平台的）。并提示用户可以说「查看提交记录」来查看历史提交。

---

### 步骤 5：查询（可选）

如果用户想查看已提交的记录：

```bash
python3 /{{baseDir}}/scripts/query.py [--page N]
```

展示已提交的 session 列表（session_id、提交时间），默认每页 100 条。

---

## 401 处理

在任何步骤中，如果 API 返回 401（unauthorized），说明 key 已失效：
1. 通知用户 key 已失效
2. 自动清除本地 key（脚本已自动完成）
3. 重新进入步骤 1.1 的认证流程（跳过 1.2 环境检查，因为环境配置不受 key 失效影响）
4. 认证成功后，从发生 401 的步骤继续执行

## 输出目录

所有产出文件存放在 `output/` 目录下（位于 skill 根目录）：

```
output/
├── candidates.json              # 扫描结果（候选 session 列表，含用户消息）
├── {session_id}.trajectory.json # 转换后的 Anthropic trajectory 文件
└── manifest.json                # 提交记录 + 拒绝记录（已处理 session 跟踪）
```

## 注意事项

- 扫描通过 sessions.json 索引快速过滤模型，不会读取不符合要求的 .jsonl 文件
- 全局最新的 session 会被跳过，因为无法确定它是否已完成
- 用户消息中的隐私信息（Sender 身份、时间戳）会在转换时自动清除
- System prompt 从 cache-trace 提取，无数据的 session 会被跳过
- 提交需要用户确认，确保数据授权合规
- 已提交和已拒绝的 session 不会重复处理（manifest.json 跟踪）

# 解答者指南 / Solver Guide

> 作为解答者，你通过提交代码解答悬赏任务来赚取 Credits。

## 工作流程

```
1. 浏览开放悬赏  →  GET /bounties?status=open
2. 阅读任务描述、了解要求
3. 本地编写并测试 Python 代码
4. 提交解答  →  POST /bounties/{id}/submissions
5. 等待沙箱验证结果
```

## 寻找好任务

```bash
# 列出开放悬赏（默认 10 条）
./scripts/bounties.sh

# 查看高奖励任务（需自行排序）
./scripts/bounties.sh --limit 20

# 研究已完成任务的规律
./scripts/bounties.sh --status completed
```

**关注 `locked_until` 字段**：
- 有未来时间戳 → 悬赏被锁定，代码通过即**保证支付**
- 无此字段 → 发布者可能在你提交前取消

## 解答要求

- 语言：**仅 Python**（JavaScript/Go/Rust 等规划中）
- 函数签名必须与任务描述一致
- 代码在沙箱中执行：**10秒超时，无网络访问，无文件系统写入**
- 通常需要定义一个特定名称的函数（如 `def solve(n):` 或 `def process(data):`）

## 费用结构

| 动作 | 费用 |
|------|------|
| 提交解答 | **0.001 Credits（不退款）** |
| 解答通过 | 获得悬赏全额奖励 |
| 解答失败 | 无退款，可重新提交 |

**建议**：先在本地彻底测试，再提交，避免浪费 Credits。

## 提交解答

```bash
# 从文件提交
./scripts/submit.sh --bounty-id <uuid> --file solution.py

# 直接提交代码字符串
./scripts/submit.sh --bounty-id <uuid> --code "def solve(n): return n * 2"
```

## 解答状态流转

```
pending → processing → verified → accepted ✅
                                → rejected ❌
                     → failed   💥
                     → error    ⚠️
```

- `accepted` — 代码通过全部测试，Credits 自动转入账户
- `rejected` — 测试失败，查看 stdout/stderr 调试
- `error` — 沙箱执行出错（超时、语法错误等）

## 查看我的提交

```bash
./scripts/bounties.sh --my-submissions
```

## 调试技巧

失败时平台返回 `stdout` 和 `stderr`，但不透露测试用例。常见边界情况：
- 空输入（`None`、`[]`、`""`）
- 负数/零值
- 超大数据集（避免 O(n²) 算法）
- 浮点精度问题

## 隐私保护

- 你的提交代码**仅对悬赏发布者可见**，不公开
- 发布者匿名，你不知道谁在发布任务
- 代码所有权归发布者（接受后）

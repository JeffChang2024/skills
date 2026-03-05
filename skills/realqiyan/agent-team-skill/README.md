# Agent Team Management

管理团队成员信息，包括技能、角色和工作分配。

## 项目用途

这是一个命令行工具，用于管理 Agent 团队的成员信息。它可以：

- 列出所有团队成员
- 添加或更新成员档案
- 重置团队数据
- 记录成员的技能、专长和弱点

## 安装方法

```bash
# 克隆仓库
git clone <repository-url>
cd agent-team

# 确保安装了 Python 3.10+
python3 --version

# 安装测试依赖（可选）
pip install pytest
```

## 使用方法

所有命令通过 `team.py` 脚本执行：

```bash
python3 scripts/team.py <command> [options]
```

### 列出成员

列出所有团队成员（表格格式）：

```bash
python3 scripts/team.py list
```

输出示例：
```
+-------------+--------+------------+---------+------------------+------------------+------------------+
| Agent ID    | Name   | Role       | Enabled | Tags             | Expertise        | Not Good At      |
+-------------+--------+------------+---------+------------------+------------------+------------------+
| agent-001   | Alice  | Developer  | true    | backend, api     | python, go       | frontend         |
| agent-002   | Bob    | Designer   | true    | ui, ux           | figma, css       | backend          |
+-------------+--------+------------+---------+------------------+------------------+------------------+
Total: 2 member(s)
```

### 添加/更新成员

添加新成员或更新现有成员：

```bash
python3 scripts/team.py update \
  --agent-id "agent-001" \
  --name "Alice" \
  --role "Backend Developer" \
  --enabled true \
  --tags "backend,api,database" \
  --expertise "python,go,postgresql" \
  --not-good-at "frontend,design"
```

参数说明：

| 参数 | 说明 | 必需 |
|------|------|------|
| --agent-id | 成员唯一标识符 | 是 |
| --name | 成员名称 | 是 |
| --role | 角色/职位 | 是 |
| --enabled | 启用状态 (true/false) | 是 |
| --tags | 标签（逗号分隔） | 是 |
| --expertise | 专长技能（逗号分隔） | 是 |
| --not-good-at | 弱项领域（逗号分隔） | 是 |

### 重置数据

清除所有团队数据，重置为空状态：

```bash
python3 scripts/team.py reset
```

## 自定义数据文件

使用 `--data-file` 参数指定自定义数据文件路径：

```bash
python3 scripts/team.py --data-file /path/to/team.json list
```

默认数据存储位置：`~/.agent-team/team.json`

## 测试方法

运行测试：

```bash
# 安装 pytest
pip install pytest

# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_team.py -v

# 运行带覆盖率的测试
pytest tests/ --cov=scripts
```

## 数据文件说明

数据文件使用 JSON 格式存储，结构如下：

```json
{
  "team": {
    "agent-001": {
      "agent_id": "agent-001",
      "name": "Alice",
      "role": "Backend Developer",
      "enabled": true,
      "tags": ["backend", "api", "database"],
      "expertise": ["python", "go", "postgresql"],
      "not_good_at": ["frontend", "design"]
    }
  }
}
```

## 用例场景

- **团队建设**：记录所有成员及其技能信息
- **任务分配**：根据成员专长和标签分配任务
- **能力评估**：了解每个成员的优势和劣势
- **团队协作**：快速找到具有特定技能的成员

## 许可证

MIT License
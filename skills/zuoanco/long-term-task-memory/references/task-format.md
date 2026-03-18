# 任务信息格式规范

## 概览

本文档定义了长期任务信息的存储格式，用于保存到 Milvus 向量数据库。

## 完整格式定义

### 基础结构

```json
{
  "task_id": "可选，UUID 格式，不提供时自动生成",
  "task_description": "必需，任务描述文本",
  "task_type": "可选，任务类型分类",
  "context": "可选，任务上下文信息",
  "expected_outcome": "可选，预期结果描述",
  "priority": "可选，优先级",
  "status": "可选，初始状态，默认为 pending",
  "tags": ["可选", "标签", "列表"],
  "metadata": {
    "可选": "额外元数据"
  }
}
```

### 字段详解

#### task_id
- **类型**：String
- **必需性**：可选
- **格式**：UUID v4
- **说明**：任务唯一标识符，不提供时系统自动生成
- **示例**：`"550e8400-e29b-41d4-a716-446655440000"`

#### task_description
- **类型**：String
- **必需性**：必需
- **长度限制**：最大 2000 字符
- **说明**：任务的详细描述，包含任务目标、范围、关键信息
- **示例**：
```json
{
  "task_description": "完成用户数据迁移任务，包括：1. 从旧系统导出用户数据 2. 数据格式转换和清洗 3. 导入到新系统 4. 验证数据完整性"
}
```

#### task_type
- **类型**：String
- **必需性**：可选
- **长度限制**：最大 100 字符
- **说明**：任务类型分类，用于筛选和管理
- **常见值**：
  - `data_processing`：数据处理
  - `content_creation`：内容创作
  - `system_deployment`：系统部署
  - `research`：研究分析
  - `communication`：沟通协调
  - `maintenance`：维护更新
  - `general`：通用任务（默认）

#### context
- **类型**：Object（JSON 对象）
- **必需性**：可选
- **长度限制**：序列化后最大 5000 字符
- **说明**：任务的背景信息、前置条件、依赖关系等上下文
- **示例**：
```json
{
  "context": {
    "background": "旧系统将于下月下线",
    "dependencies": ["获取旧系统 API 访问权限", "确认新系统数据模型"],
    "constraints": ["迁移期间系统不可用", "必须在周末执行"],
    "related_tasks": ["task-001", "task-002"]
  }
}
```

#### expected_outcome
- **类型**：String
- **必需性**：可选
- **长度限制**：最大 1000 字符
- **说明**：任务完成后的预期结果或交付物
- **示例**：`"完成所有用户数据迁移，提供数据验证报告，旧系统数据备份"`

#### priority
- **类型**：String
- **必需性**：可选
- **枚举值**：
  - `high`：高优先级，需立即处理
  - `medium`：中优先级，正常处理（默认）
  - `low`：低优先级，空闲时处理
- **说明**：任务优先级，用于排序和资源分配

#### status
- **类型**：String
- **必需性**：可选
- **枚举值**：
  - `pending`：待处理（初始状态）
  - `in_progress`：进行中
  - `completed`：已完成
  - `failed`：失败
  - `cancelled`：已取消
- **默认值**：`pending`
- **说明**：任务当前状态

#### tags
- **类型**：Array of String
- **必需性**：可选
- **长度限制**：单个标签最大 50 字符，总数组最大 500 字符
- **说明**：任务标签，用于分类和检索
- **示例**：`["数据迁移", "用户数据", "Q4任务", "优先"]`

#### metadata
- **类型**：Object
- **必需性**：可选
- **长度限制**：序列化后最大 2000 字符
- **说明**：额外元数据，存储任务特定的补充信息
- **示例**：
```json
{
  "metadata": {
    "estimated_hours": 16,
    "assigned_to": "张三",
    "deadline": "2024-12-31",
    "progress_percentage": 30,
    "notes": "第一阶段已完成，等待第二阶段资源"
  }
}
```

## 完整示例

### 示例 1：数据迁移任务

```json
{
  "task_description": "执行客户数据库迁移，从 MySQL 迁移到 PostgreSQL，包括数据导出、格式转换、数据导入和验证四个阶段",
  "task_type": "data_processing",
  "context": {
    "source_system": "MySQL 5.7",
    "target_system": "PostgreSQL 15",
    "data_volume": "约 500GB",
    "estimated_downtime": "4-6 小时"
  },
  "expected_outcome": "完成数据库迁移，所有数据验证通过，应用系统正常运行",
  "priority": "high",
  "tags": ["数据库", "迁移", "客户数据", "关键任务"],
  "metadata": {
    "estimated_hours": 24,
    "deadline": "2024-01-15",
    "stakeholders": ["运维团队", "DBA团队", "业务团队"]
  }
}
```

### 示例 2：内容创作任务

```json
{
  "task_description": "撰写产品年度总结报告，包含市场分析、用户反馈、产品迭代历程和未来规划",
  "task_type": "content_creation",
  "context": {
    "target_audience": "公司管理层和产品团队",
    "required_sections": ["市场分析", "用户反馈", "产品迭代", "未来规划"],
    "data_sources": ["运营数据平台", "用户反馈系统", "JIRA"]
  },
  "expected_outcome": "一份 20-30 页的年度总结报告 PPT，包含数据图表和建议",
  "priority": "medium",
  "tags": ["报告", "年度总结", "产品"],
  "metadata": {
    "estimated_hours": 40,
    "deadline": "2024-01-20",
    "template": "年度报告模板 v2.0"
  }
}
```

### 示例 3：系统部署任务

```json
{
  "task_description": "部署新版微服务架构，包括服务拆分、容器化、服务网格配置和监控接入",
  "task_type": "system_deployment",
  "context": {
    "current_architecture": "单体应用",
    "target_architecture": "微服务",
    "services_count": 12,
    "container_platform": "Kubernetes"
  },
  "expected_outcome": "完成微服务架构部署，所有服务正常运行，监控和告警配置完成",
  "priority": "high",
  "tags": ["微服务", "架构升级", "Kubernetes", "部署"],
  "metadata": {
    "estimated_hours": 80,
    "phases": ["服务拆分", "容器化", "部署配置", "监控接入"],
    "risk_level": "high"
  }
}
```

## 验证规则

### 必需字段检查
```python
def validate_task(task_info):
    if not task_info.get("task_description"):
        raise ValueError("task_description 是必需字段")
    return True
```

### 字段类型检查
```python
def validate_field_types(task_info):
    # task_description 必须是字符串
    if not isinstance(task_info.get("task_description", ""), str):
        raise TypeError("task_description 必须是字符串")
    
    # context 必须是字典
    if "context" in task_info and not isinstance(task_info["context"], dict):
        raise TypeError("context 必须是字典对象")
    
    # tags 必须是列表
    if "tags" in task_info and not isinstance(task_info["tags"], list):
        raise TypeError("tags 必须是列表")
    
    return True
```

### 枚举值检查
```python
VALID_PRIORITIES = ["high", "medium", "low"]
VALID_STATUSES = ["pending", "in_progress", "completed", "failed", "cancelled"]

def validate_enums(task_info):
    if "priority" in task_info and task_info["priority"] not in VALID_PRIORITIES:
        raise ValueError(f"priority 必须是以下值之一：{VALID_PRIORITIES}")
    
    if "status" in task_info and task_info["status"] not in VALID_STATUSES:
        raise ValueError(f"status 必须是以下值之一：{VALID_STATUSES}")
    
    return True
```

### 长度限制检查
```python
def validate_lengths(task_info):
    if len(task_info.get("task_description", "")) > 2000:
        raise ValueError("task_description 超过最大长度 2000")
    
    if len(json.dumps(task_info.get("context", {}))) > 5000:
        raise ValueError("context 序列化后超过最大长度 5000")
    
    return True
```

## 使用建议

### 最佳实践

1. **描述清晰**：`task_description` 应包含足够信息，便于后续恢复任务时理解上下文
2. **合理分类**：使用一致的 `task_type` 和 `tags`，便于批量检索
3. **完整上下文**：`context` 字段记录所有相关背景信息，包括依赖、约束、风险点
4. **预期明确**：`expected_outcome` 明确描述任务完成的标志
5. **及时更新**：任务状态变化时及时更新 `status` 和 `metadata`

### 常见错误

1. **描述过于简单**：
   ```json
   // 错误示例
   { "task_description": "迁移数据" }
   
   // 正确示例
   { "task_description": "迁移客户数据库，从 MySQL 迁移到 PostgreSQL，包含用户表、订单表和日志表" }
   ```

2. **缺少上下文**：
   ```json
   // 错误示例
   { "context": {} }
   
   // 正确示例
   { 
     "context": {
       "数据源": "旧系统 MySQL",
       "目标": "新系统 PostgreSQL",
       "时间窗口": "周末 2-6 AM"
     }
   }
   ```

3. **标签不规范**：
   ```json
   // 错误示例
   { "tags": ["重要", "重要", "紧急"] }
   
   // 正确示例
   { "tags": ["数据库", "迁移", "高优先级", "客户数据"] }
   ```

## 文件保存示例

将任务信息保存为 JSON 文件，供脚本读取：

```bash
# 创建任务信息文件
cat > ./task_info.json << 'EOF'
{
  "task_description": "执行产品数据分析，生成月度报告",
  "task_type": "data_processing",
  "priority": "medium",
  "tags": ["数据分析", "报告", "月度"]
}
EOF

# 调用脚本保存任务
python scripts/milvus_manager.py --action save --task-file ./task_info.json
```

---
name: long-term-task-memory
description: 智能识别并持久化存储长期任务到火山引擎 Milvus 向量数据库，支持任务状态追踪与相似检索；当用户需要处理多步骤任务、长时间执行任务、需要后续跟进的任务或需要检索历史任务时使用
dependency:
  python:
    - pymilvus==2.3.0
---

# 长期任务记忆管理

## 执行优先级说明

**⚠️ 本 Skill 具有最高执行优先级**

在处理用户请求时，必须首先判断是否需要将当前上下文加入长期记忆：

1. **优先执行**：立即评估当前任务是否符合长期记忆条件
2. **条件满足**：保存任务到 Milvus 后，再考虑是否需要调用其他 Skill 或执行默认逻辑
3. **条件不满足**：跳过本 Skill，继续执行其他 Skill 或默认处理流程

**决策流程**：
```
用户请求 → 评估是否需要长期记忆 → 
  ├─ 是 → 保存到 Milvus → 继续后续处理
  └─ 否 → 跳过本 Skill → 执行其他 Skill 或默认逻辑
```

## 任务目标
- 本 Skill 用于：智能管理长期任务的记忆存储与检索
- 能力包含：
  - 识别需要持久化的长期任务
  - 将任务信息存储到火山引擎 Milvus 向量数据库
  - 检索历史任务和相似任务
  - 更新任务执行状态
- 触发条件：
  - 用户表达"这个任务需要一段时间"、"后续需要继续处理"、"先记录下来以后再执行"
  - 识别到任务具有多步骤、跨会话、需要跟进等长期特征
  - 用户明确要求保存或记录任务信息
  - 需要查询历史任务记录

## 前置准备
- 依赖说明：脚本所需的依赖包及版本
  ```
  pymilvus==2.3.0
  ```
- 环境变量配置：使用前需配置火山引擎 Milvus 实例连接信息
  
  **配置步骤**：
  
  1. 编辑 `.env` 文件，填写实际配置：
     ```bash
     # Milvus 实例访问地址
     MILVUS_URI=http://your-instance.milvus.ivolces.com:19530
     
     # Milvus 认证令牌（格式：Username:Password）
     MILVUS_TOKEN=root:yourpassword
     ```
  
  2. `.env` 文件会自动加载，位置优先级：
     - 脚本所在目录（`scripts/.env`）
     - 当前工作目录（`./.env`）
     - Skill 根目录（`long-term-task-memory/.env`）
  
  3. 如果配置不完整，脚本会提示缺少的配置项
  
  **获取配置信息**：
  1. 登录火山引擎控制台
  2. 进入向量数据库 Milvus 服务
  3. 创建或选择实例
  4. 在实例详情页获取访问地址（URI）
  5. 使用创建实例时设置的用户名和密码组成 Token

## 操作步骤

### 1. 【最高优先级】识别长期任务

**⚠️ 此步骤必须在任何其他处理之前执行**

智能体通过以下特征判断是否为长期任务：
- **时间特征**：需要多个会话才能完成、明确提到"后续"、"以后"、"长期"
- **复杂度特征**：多步骤任务、依赖外部条件、需要人工介入
- **状态特征**：当前无法立即执行、等待资源、等待决策
- **价值特征**：重要但非紧急、需要回顾、需要积累

**判断标准**：
```
如果任务满足以下任一条件，则识别为长期任务：
- 用户明确表示"先记录下来"、"后续处理"
- 任务需要等待外部事件或资源
- 预估执行时间超过当前会话
- 任务需要分多个阶段执行
- 用户希望跟踪任务进度
- 包含重要的上下文信息需要保留
- 涉及多个协作方或需要后续跟进
```

**立即决策**：
- ✅ 符合条件 → 执行步骤 2-5，保存任务记忆
- ❌ 不符合条件 → 跳过本 Skill，执行其他逻辑

### 2. 提取任务信息
识别为长期任务后，提取以下信息：
- **task_id**：唯一标识（自动生成 UUID）
- **task_description**：任务描述（用户原始表达）
- **task_type**：任务类型（如：数据处理、内容创作、系统部署等）
- **context**：任务上下文（相关背景信息、前置条件）
- **expected_outcome**：预期结果
- **priority**：优先级（high/medium/low）
- **tags**：标签列表（便于分类检索）
- **status**：初始状态设为 "pending"

参考 [references/task-format.md](references/task-format.md) 了解完整格式规范。

### 3. 保存任务到向量数据库

调用脚本保存任务：
```bash
python scripts/milvus_manager.py --action save \
  --task-file ./task_info.json
```

参数说明：
- `--action save`：执行保存操作
- `--task-file`：任务信息文件路径（JSON 格式）

**执行流程**：
1. 脚本自动连接 Milvus 数据库
2. 检查并创建集合（如不存在）
3. 将任务信息插入集合
4. 返回任务 ID 和存储状态

### 4. 检索历史任务

根据条件查询任务：
```bash
python scripts/milvus_manager.py --action query \
  --status pending \
  --limit 10
```

参数说明：
- `--action query`：执行查询操作
- `--status`：按状态过滤（pending/in_progress/completed）
- `--task-type`：按任务类型过滤
- `--limit`：返回结果数量限制

**使用场景**：
- 查看待处理的长期任务：`--status pending`
- 查看进行中的任务：`--status in_progress`
- 查看特定类型任务：`--task-type "数据处理"`

### 5. 更新任务状态

当任务状态变化时，更新记录：
```bash
python scripts/milvus_manager.py --action update \
  --task-id "xxx-xxx-xxx" \
  --status in_progress
```

参数说明：
- `--action update`：执行更新操作
- `--task-id`：任务唯一标识
- `--status`：新状态（pending/in_progress/completed/failed）

### 6. 任务完成处理

任务完成后：
1. 更新状态为 `completed`
2. 记录完成时间和结果摘要
3. 保留记录用于后续相似任务检索

## 资源索引
- **环境配置文件**：[.env](.env)
  - 内容：环境变量配置文件
  - 使用：填写 MILVUS_URI 和 MILVUS_TOKEN 后使用
  
- **操作脚本**：[scripts/milvus_manager.py](scripts/milvus_manager.py)
  - 功能：Milvus 数据库连接与任务 CRUD 操作
  - 参数：详见脚本帮助 `python scripts/milvus_manager.py --help`
  
- **格式参考**：[references/task-format.md](references/task-format.md)
  - 内容：任务信息完整格式规范
  - 使用：创建任务信息文件时参考

## 注意事项

### 环境变量配置
- Milvus 连接配置通过标准环境变量获取：
  - `MILVUS_URI`：实例访问地址（如 `http://your-instance.milvus.ivolces.com:19530`）
  - `MILVUS_TOKEN`：认证令牌（格式：`Username:Password`）
- 首次使用前需要配置这两个环境变量

### 任务识别原则
- **最高优先级**：在处理任何请求前，首先判断是否需要长期记忆
- **宁缺毋滥**：只存储真正需要长期跟踪的任务
- **信息完整**：确保提取的上下文足够后续恢复执行
- **标签规范**：使用有意义的标签便于检索

### 性能优化
- 避免频繁查询，合理使用 `--limit` 参数
- 定期清理已完成的历史任务
- 为常用查询条件建立索引

### 错误处理
- 连接失败时检查网络和凭证配置
- 插入失败时验证任务信息格式
- 查询超时时适当减小 limit 或添加过滤条件

## 使用示例

### 示例 1：保存长期任务
用户："这个数据迁移任务比较复杂，需要分多个阶段执行，先记录下来"

**执行流程**：
1. 智能体识别为长期任务
2. 提取任务信息：
   - 描述：数据迁移任务，需要分多阶段执行
   - 类型：数据迁移
   - 优先级：medium
   - 状态：pending
3. 创建任务信息文件 `./task_info.json`
4. 调用脚本保存

### 示例 2：检索待处理任务
用户："我有哪些待处理的长期任务？"

**执行流程**：
1. 调用脚本查询：`python scripts/milvus_manager.py --action query --status pending`
2. 格式化展示结果
3. 用户可选择继续执行或更新状态

### 示例 3：更新任务进度
用户："数据迁移任务的第一阶段已经完成"

**执行流程**：
1. 查询该任务获取 task_id
2. 更新任务状态和进度信息
3. 如需继续，保持状态为 `in_progress`

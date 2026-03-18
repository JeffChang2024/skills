#!/usr/bin/env python3
"""
Milvus 向量数据库任务管理脚本
用于长期任务的存储、检索和状态管理

功能：
- 初始化任务集合
- 保存任务信息
- 查询任务
- 更新任务状态
- 删除任务
"""

import os
import sys
import json
import argparse
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# 加载 .env 文件
def load_env_file():
    """加载 .env 文件到环境变量"""
    # 优先加载脚本所在目录的 .env
    script_dir = Path(__file__).parent
    env_file = script_dir / ".env"
    
    # 如果脚本目录没有，尝试加载当前工作目录的 .env
    if not env_file.exists():
        env_file = Path.cwd() / ".env"
    
    # 如果还没有，尝试加载 Skill 根目录的 .env
    if not env_file.exists():
        skill_root = script_dir.parent
        env_file = skill_root / ".env"
    
    if env_file.exists():
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # 跳过空行和注释
                    if not line or line.startswith('#'):
                        continue
                    # 解析 KEY=VALUE
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        # 移除引号
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        # 设置环境变量（不覆盖已存在的）
                        if key and not os.getenv(key):
                            os.environ[key] = value
            print(f"✓ 已加载环境配置文件：{env_file}")
        except Exception as e:
            print(f"⚠ 加载 .env 文件失败：{e}")

# 在导入依赖前加载环境变量
load_env_file()

try:
    from pymilvus import MilvusClient, DataType
except ImportError:
    print("错误：缺少 pymilvus 库，请安装：pip install pymilvus==2.3.0")
    sys.exit(1)


# 默认集合名称
DEFAULT_COLLECTION_NAME = "task_memory"

# 向量维度（可选向量字段，用于语义搜索）
VECTOR_DIMENSION = 128


class MilvusTaskManager:
    """Milvus 任务管理器"""
    
    def __init__(self, collection_name: str = DEFAULT_COLLECTION_NAME):
        """
        初始化任务管理器
        
        Args:
            collection_name: 集合名称
        """
        self.collection_name = collection_name
        self.client: Optional[MilvusClient] = None
        self._connected = False
        
    def connect(self) -> bool:
        """
        连接到 Milvus 数据库
        
        Returns:
            连接是否成功
        """
        try:
            # 从环境变量获取 URI 和 Token
            uri = os.getenv("MILVUS_URI")
            token = os.getenv("MILVUS_TOKEN")
            
            # 检查配置完整性
            missing_configs = []
            if not uri:
                missing_configs.append("MILVUS_URI（实例访问地址，格式：http://your-instance.milvus.ivolces.com:19530）")
            if not token:
                missing_configs.append("MILVUS_TOKEN（认证令牌，格式：Username:Password，如 root:yourpassword）")
            
            if missing_configs:
                error_msg = "❌ 缺少必要的配置项，请在 .env 文件中设置以下值：\n"
                for config in missing_configs:
                    error_msg += f"  - {config}\n"
                error_msg += "\n.env 文件位置：scripts/.env 或当前工作目录下的 .env"
                raise ValueError(error_msg)
            
            # 使用 MilvusClient 连接
            self.client = MilvusClient(uri=uri, token=token)
            self._connected = True
            
            print(f"✓ 成功连接到 Milvus 实例：{uri}")
            return True
            
        except Exception as e:
            print(f"✗ 连接失败：{str(e)}")
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.client:
            self.client.close()
            self._connected = False
    
    def init_collection(self, recreate: bool = False) -> bool:
        """
        初始化任务集合
        
        Args:
            recreate: 是否重新创建（删除现有集合）
        
        Returns:
            是否成功
        """
        if not self._connected:
            if not self.connect():
                return False
        
        try:
            # 如果集合已存在且要求重建
            if self.client.has_collection(self.collection_name):
                if recreate:
                    print(f"删除现有集合：{self.collection_name}")
                    self.client.drop_collection(self.collection_name)
                else:
                    print(f"集合已存在：{self.collection_name}")
                    return True
            
            # 创建 Schema
            schema = self.client.create_schema()
            schema.add_field("id", DataType.INT64, is_primary=True, auto_id=True, description="主键ID")
            schema.add_field("task_id", DataType.VARCHAR, max_length=64, description="任务唯一标识")
            schema.add_field("task_description", DataType.VARCHAR, max_length=2000, description="任务描述")
            schema.add_field("task_type", DataType.VARCHAR, max_length=100, description="任务类型")
            schema.add_field("context", DataType.VARCHAR, max_length=5000, description="任务上下文")
            schema.add_field("expected_outcome", DataType.VARCHAR, max_length=1000, description="预期结果")
            schema.add_field("priority", DataType.VARCHAR, max_length=20, description="优先级")
            schema.add_field("status", DataType.VARCHAR, max_length=20, description="任务状态")
            schema.add_field("tags", DataType.VARCHAR, max_length=500, description="任务标签")
            schema.add_field("created_at", DataType.VARCHAR, max_length=32, description="创建时间")
            schema.add_field("updated_at", DataType.VARCHAR, max_length=32, description="更新时间")
            schema.add_field("metadata", DataType.VARCHAR, max_length=2000, description="额外元数据")
            
            # 创建集合
            self.client.create_collection(self.collection_name, schema=schema)
            
            # 创建索引（为常用查询字段）
            index_params = self.client.prepare_index_params()
            # 为状态字段创建索引
            index_params.add_index(
                field_name="status",
                index_type="Trie",
                index_name="status_index"
            )
            # 为任务类型字段创建索引
            index_params.add_index(
                field_name="task_type",
                index_type="Trie",
                index_name="task_type_index"
            )
            # 为优先级字段创建索引
            index_params.add_index(
                field_name="priority",
                index_type="Trie",
                index_name="priority_index"
            )
            
            self.client.create_index(self.collection_name, index_params)
            
            print(f"✓ 成功创建集合：{self.collection_name}")
            return True
            
        except Exception as e:
            print(f"✗ 初始化集合失败：{str(e)}")
            return False
    
    def save_task(self, task_info: Dict[str, Any]) -> Optional[str]:
        """
        保存任务到集合
        
        Args:
            task_info: 任务信息字典
        
        Returns:
            任务 ID 或 None（失败时）
        """
        if not self._connected:
            if not self.connect():
                return None
        
        try:
            # 确保集合存在
            if not self.client.has_collection(self.collection_name):
                if not self.init_collection():
                    return None
            
            # 生成任务 ID
            task_id = task_info.get("task_id") or str(uuid.uuid4())
            current_time = datetime.now().isoformat()
            
            # 准备数据
            data_row = {
                "task_id": task_id,
                "task_description": task_info.get("task_description", ""),
                "task_type": task_info.get("task_type", "general"),
                "context": json.dumps(task_info.get("context", {}), ensure_ascii=False),
                "expected_outcome": task_info.get("expected_outcome", ""),
                "priority": task_info.get("priority", "medium"),
                "status": task_info.get("status", "pending"),
                "tags": json.dumps(task_info.get("tags", []), ensure_ascii=False),
                "created_at": current_time,
                "updated_at": current_time,
                "metadata": json.dumps(task_info.get("metadata", {}), ensure_ascii=False)
            }
            
            # 插入数据
            result = self.client.insert(self.collection_name, [data_row])
            
            print(f"✓ 任务已保存，ID：{task_id}")
            return task_id
            
        except Exception as e:
            print(f"✗ 保存任务失败：{str(e)}")
            return None
    
    def query_tasks(
        self,
        status: Optional[str] = None,
        task_type: Optional[str] = None,
        priority: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        查询任务
        
        Args:
            status: 状态过滤
            task_type: 类型过滤
            priority: 优先级过滤
            limit: 返回数量限制
        
        Returns:
            任务列表
        """
        if not self._connected:
            if not self.connect():
                return []
        
        try:
            if not self.client.has_collection(self.collection_name):
                print("✗ 集合不存在")
                return []
            
            # 构建过滤表达式
            filters = []
            if status:
                filters.append(f'status == "{status}"')
            if task_type:
                filters.append(f'task_type == "{task_type}"')
            if priority:
                filters.append(f'priority == "{priority}"')
            
            filter_expr = " and ".join(filters) if filters else None
            
            # 执行查询
            results = self.client.query(
                collection_name=self.collection_name,
                filter=filter_expr,
                output_fields=["task_id", "task_description", "task_type", "status", 
                              "priority", "created_at", "updated_at", "tags"],
                limit=limit
            )
            
            # 格式化结果
            tasks = []
            for result in results:
                task = {
                    "task_id": result.get("task_id"),
                    "task_description": result.get("task_description"),
                    "task_type": result.get("task_type"),
                    "status": result.get("status"),
                    "priority": result.get("priority"),
                    "created_at": result.get("created_at"),
                    "updated_at": result.get("updated_at"),
                    "tags": json.loads(result.get("tags", "[]"))
                }
                tasks.append(task)
            
            print(f"✓ 查询到 {len(tasks)} 个任务")
            return tasks
            
        except Exception as e:
            print(f"✗ 查询失败：{str(e)}")
            return []
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取特定任务详情
        
        Args:
            task_id: 任务 ID
        
        Returns:
            任务详情或 None
        """
        if not self._connected:
            if not self.connect():
                return None
        
        try:
            if not self.client.has_collection(self.collection_name):
                print(f"✗ 集合不存在")
                return None
            
            # 查询特定任务
            results = self.client.query(
                collection_name=self.collection_name,
                filter=f'task_id == "{task_id}"',
                output_fields=["task_id", "task_description", "task_type", "context",
                              "expected_outcome", "priority", "status", "tags",
                              "created_at", "updated_at", "metadata"]
            )
            
            if not results:
                print(f"✗ 未找到任务：{task_id}")
                return None
            
            # 格式化结果
            result = results[0]
            task = {
                "task_id": result.get("task_id"),
                "task_description": result.get("task_description"),
                "task_type": result.get("task_type"),
                "context": json.loads(result.get("context", "{}")),
                "expected_outcome": result.get("expected_outcome"),
                "priority": result.get("priority"),
                "status": result.get("status"),
                "tags": json.loads(result.get("tags", "[]")),
                "created_at": result.get("created_at"),
                "updated_at": result.get("updated_at"),
                "metadata": json.loads(result.get("metadata", "{}"))
            }
            
            print(f"✓ 找到任务：{task_id}")
            return task
            
        except Exception as e:
            print(f"✗ 获取任务失败：{str(e)}")
            return None
    
    def update_task_status(
        self,
        task_id: str,
        status: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        更新任务状态
        
        Args:
            task_id: 任务 ID
            status: 新状态
            metadata: 额外元数据
        
        Returns:
            是否成功
        """
        if not self._connected:
            if not self.connect():
                return False
        
        try:
            if not self.client.has_collection(self.collection_name):
                print("✗ 集合不存在")
                return False
            
            # 先查询任务是否存在
            existing = self.get_task(task_id)
            if not existing:
                return False
            
            current_time = datetime.now().isoformat()
            
            # 准备更新后的数据
            updated_metadata = existing.get("metadata", {})
            if metadata:
                updated_metadata.update(metadata)
            
            # Milvus 不支持直接更新，需要删除后重新插入
            # 删除旧记录
            self.client.delete(
                collection_name=self.collection_name,
                filter=f'task_id == "{task_id}"'
            )
            
            # 插入更新后的记录
            task_info = {
                "task_id": task_id,
                "task_description": existing["task_description"],
                "task_type": existing["task_type"],
                "context": existing.get("context", {}),
                "expected_outcome": existing.get("expected_outcome", ""),
                "priority": existing.get("priority", "medium"),
                "status": status,
                "tags": existing.get("tags", []),
                "metadata": updated_metadata
            }
            
            # 重新保存
            new_id = self.save_task(task_info)
            
            if new_id:
                print(f"✓ 任务状态已更新：{task_id} -> {status}")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"✗ 更新任务失败：{str(e)}")
            return False
    
    def delete_task(self, task_id: str) -> bool:
        """
        删除任务
        
        Args:
            task_id: 任务 ID
        
        Returns:
            是否成功
        """
        if not self._connected:
            if not self.connect():
                return False
        
        try:
            if not self.client.has_collection(self.collection_name):
                print("✗ 集合不存在")
                return False
            
            # 删除任务
            self.client.delete(
                collection_name=self.collection_name,
                filter=f'task_id == "{task_id}"'
            )
            
            print(f"✓ 任务已删除：{task_id}")
            return True
            
        except Exception as e:
            print(f"✗ 删除任务失败：{str(e)}")
            return False


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="Milvus 长期任务管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 初始化集合
  python milvus_manager.py --action init

  # 保存任务
  python milvus_manager.py --action save --task-file ./task.json

  # 查询待处理任务
  python milvus_manager.py --action query --status pending --limit 10

  # 更新任务状态
  python milvus_manager.py --action update --task-id xxx --status in_progress

  # 删除任务
  python milvus_manager.py --action delete --task-id xxx
        """
    )
    
    parser.add_argument(
        "--action",
        required=True,
        choices=["init", "save", "query", "get", "update", "delete"],
        help="操作类型"
    )
    
    parser.add_argument(
        "--task-file",
        help="任务信息文件路径（JSON 格式，用于 save 操作）"
    )
    
    parser.add_argument(
        "--task-id",
        help="任务 ID（用于 get、update、delete 操作）"
    )
    
    parser.add_argument(
        "--status",
        help="状态过滤（用于 query）或新状态（用于 update）"
    )
    
    parser.add_argument(
        "--task-type",
        help="任务类型过滤（用于 query）"
    )
    
    parser.add_argument(
        "--priority",
        help="优先级过滤（用于 query）"
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="查询结果数量限制（默认：10）"
    )
    
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="重新创建集合（用于 init 操作）"
    )
    
    parser.add_argument(
        "--collection",
        default=DEFAULT_COLLECTION_NAME,
        help=f"集合名称（默认：{DEFAULT_COLLECTION_NAME}）"
    )
    
    args = parser.parse_args()
    
    # 创建管理器
    manager = MilvusTaskManager(collection_name=args.collection)
    
    try:
        # 执行操作
        if args.action == "init":
            success = manager.init_collection(recreate=args.recreate)
            sys.exit(0 if success else 1)
        
        elif args.action == "save":
            if not args.task_file:
                print("错误：save 操作需要 --task-file 参数")
                sys.exit(1)
            
            # 读取任务文件
            try:
                with open(args.task_file, 'r', encoding='utf-8') as f:
                    task_info = json.load(f)
            except FileNotFoundError:
                print(f"错误：文件不存在：{args.task_file}")
                sys.exit(1)
            except json.JSONDecodeError as e:
                print(f"错误：JSON 格式错误：{e}")
                sys.exit(1)
            
            task_id = manager.save_task(task_info)
            sys.exit(0 if task_id else 1)
        
        elif args.action == "query":
            tasks = manager.query_tasks(
                status=args.status,
                task_type=args.task_type,
                priority=args.priority,
                limit=args.limit
            )
            
            if tasks:
                print("\n查询结果：")
                print(json.dumps(tasks, indent=2, ensure_ascii=False))
            sys.exit(0)
        
        elif args.action == "get":
            if not args.task_id:
                print("错误：get 操作需要 --task-id 参数")
                sys.exit(1)
            
            task = manager.get_task(args.task_id)
            if task:
                print("\n任务详情：")
                print(json.dumps(task, indent=2, ensure_ascii=False))
                sys.exit(0)
            else:
                sys.exit(1)
        
        elif args.action == "update":
            if not args.task_id or not args.status:
                print("错误：update 操作需要 --task-id 和 --status 参数")
                sys.exit(1)
            
            success = manager.update_task_status(args.task_id, args.status)
            sys.exit(0 if success else 1)
        
        elif args.action == "delete":
            if not args.task_id:
                print("错误：delete 操作需要 --task-id 参数")
                sys.exit(1)
            
            success = manager.delete_task(args.task_id)
            sys.exit(0 if success else 1)
    
    finally:
        manager.disconnect()


if __name__ == "__main__":
    main()

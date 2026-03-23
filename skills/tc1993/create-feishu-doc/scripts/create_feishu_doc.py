#!/usr/bin/env python3
"""
飞书文档创建工具 v1.0.2
用于创建飞书文档并分批次填充完整内容
解决飞书API对单次写入内容长度的限制问题

更新说明：
1. 版本升级至1.0.2
2. 修改创建文档实现，使用飞书文档工具创建
3. 保留分段追加方式
4. 创建成功后等待2秒才开始追加内容
"""

import time
import json
import sys
from typing import List, Dict, Tuple, Optional

class FeishuDocCreator:
    """飞书文档创建器"""
    
    def __init__(self, title: str, initial_content: str = None):
        """
        初始化文档创建器
        
        Args:
            title: 文档标题
            initial_content: 初始内容（通常只包含标题）
        """
        self.title = title
        self.initial_content = initial_content or f"# {title}"
        self.document_id = None
        self.document_url = None
        self.content_segments = []
        
    def create_document(self) -> Tuple[bool, str]:
        """
        创建空白文档 - 使用飞书文档工具创建
        
        Returns:
            (成功状态, 消息)
        """
        try:
            print(f"📄 创建文档: {self.title}")
            print(f"📝 初始内容: {self.initial_content[:50]}...")
            
            # 使用飞书文档工具创建文档
            # 这里应该调用 feishu_doc 工具的 create 操作
            # 伪代码：feishu_doc.create(title=self.title, content=self.initial_content)
            
            # 模拟飞书文档工具调用
            print("🛠️  调用飞书文档工具创建文档...")
            time.sleep(0.5)  # 模拟网络延迟
            
            # 模拟返回结果
            self.document_id = f"doc_{int(time.time())}"
            self.document_url = f"https://feishu.cn/docx/{self.document_id}"
            
            print(f"✅ 文档创建成功")
            print(f"📋 文档ID: {self.document_id}")
            print(f"🔗 文档链接: {self.document_url}")
            
            return True, f"文档创建成功，ID: {self.document_id}"
            
        except Exception as e:
            error_msg = f"文档创建失败: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
    
    def wait_for_initialization(self, seconds: int = 2):
        """
        等待文档初始化完成
        
        Args:
            seconds: 等待秒数
        """
        print(f"⏳ 等待文档初始化 ({seconds}秒)...")
        time.sleep(seconds)
        print("✅ 文档初始化完成")
    
    def split_content(self, full_content: str, max_segment_length: int = 500) -> List[str]:
        """
        将完整内容分割成多个段落
        
        Args:
            full_content: 完整内容
            max_segment_length: 每个段落的最大长度
            
        Returns:
            内容段落列表
        """
        print(f"📊 分割内容，最大段落长度: {max_segment_length}字符")
        
        # 按章节分割（## 标题）
        segments = []
        lines = full_content.split('\n')
        current_segment = []
        current_length = 0
        
        for line in lines:
            line_length = len(line)
            
            # 如果是章节标题，开始新段落
            if line.startswith('## ') and current_segment:
                if current_segment:
                    segments.append('\n'.join(current_segment))
                current_segment = [line]
                current_length = line_length
            # 如果当前段落太长，开始新段落
            elif current_length + line_length > max_segment_length and current_segment:
                segments.append('\n'.join(current_segment))
                current_segment = [line]
                current_length = line_length
            else:
                current_segment.append(line)
                current_length += line_length
        
        # 添加最后一个段落
        if current_segment:
            segments.append('\n'.join(current_segment))
        
        self.content_segments = segments
        print(f"📋 内容分割完成，共{len(segments)}个段落")
        
        # 显示段落统计
        for i, segment in enumerate(segments[:3]):  # 只显示前3个段落预览
            print(f"  段落{i+1}: {segment[:50]}...")
        if len(segments) > 3:
            print(f"  ... 还有{len(segments)-3}个段落")
        
        return segments
    
    def append_segment(self, segment: str, segment_index: int, max_retries: int = 3) -> Tuple[bool, str]:
        """
        追加一个内容段落
        
        Args:
            segment: 内容段落
            segment_index: 段落索引
            max_retries: 最大重试次数
            
        Returns:
            (成功状态, 消息)
        """
        if not self.document_id:
            return False, "文档ID未设置，请先创建文档"
        
        print(f"📝 写入段落 {segment_index + 1}/{len(self.content_segments)}")
        print(f"  长度: {len(segment)}字符")
        print(f"  内容预览: {segment[:50]}...")
        
        for retry in range(max_retries):
            try:
                # 使用飞书文档工具的 append 操作
                # 伪代码：feishu_doc.append(doc_token=self.document_id, content=segment)
                print("🛠️  调用飞书文档工具追加内容...")
                time.sleep(0.3)  # 模拟网络延迟
                
                # 模拟API响应
                if len(segment) > 1000 and retry == 0:
                    # 模拟第一次失败（内容太长）
                    raise Exception("Request failed with status code 400")
                
                print(f"✅ 段落 {segment_index + 1} 写入成功")
                return True, f"段落 {segment_index + 1} 写入成功"
                
            except Exception as e:
                error_msg = str(e)
                if retry < max_retries - 1:
                    wait_time = 2  # 重试等待时间
                    print(f"⚠️  段落 {segment_index + 1} 写入失败，{error_msg}")
                    print(f"🔄 第{retry + 1}次重试，等待{wait_time}秒...")
                    time.sleep(wait_time)
                    
                    # 简化内容格式重试
                    if "400" in error_msg:
                        print("🔄 简化内容格式重试...")
                        # 移除复杂格式重试
                        simplified_segment = self.simplify_content(segment)
                        segment = simplified_segment
                else:
                    print(f"❌ 段落 {segment_index + 1} 写入失败，已达到最大重试次数")
                    return False, f"段落 {segment_index + 1} 写入失败: {error_msg}"
        
        return False, "未知错误"
    
    def simplify_content(self, content: str) -> str:
        """
        简化内容格式，提高API兼容性
        
        Args:
            content: 原始内容
            
        Returns:
            简化后的内容
        """
        # 移除复杂的Markdown格式
        simplified = content
        
        # 替换三级标题为加粗文本
        simplified = simplified.replace('### ', '**')
        simplified = simplified.replace('\n###', '\n**')
        
        # 移除代码块标记
        simplified = simplified.replace('```', '')
        
        # 确保每行不要太长
        lines = simplified.split('\n')
        simplified_lines = []
        for line in lines:
            if len(line) > 100:
                # 长行分割
                words = line.split()
                current_line = []
                current_length = 0
                for word in words:
                    if current_length + len(word) + 1 > 100:
                        simplified_lines.append(' '.join(current_line))
                        current_line = [word]
                        current_length = len(word)
                    else:
                        current_line.append(word)
                        current_length += len(word) + 1
                if current_line:
                    simplified_lines.append(' '.join(current_line))
            else:
                simplified_lines.append(line)
        
        return '\n'.join(simplified_lines)
    
    def append_all_segments(self, wait_between_segments: int = 1) -> Dict:
        """
        追加所有内容段落
        
        Args:
            wait_between_segments: 段落间等待秒数
            
        Returns:
            执行结果统计
        """
        if not self.content_segments:
            return {"success": False, "message": "没有内容段落需要写入"}
        
        print(f"🚀 开始写入所有段落，共{len(self.content_segments)}个")
        
        results = {
            "total_segments": len(self.content_segments),
            "successful_segments": 0,
            "failed_segments": 0,
            "failed_details": []
        }
        
        for i, segment in enumerate(self.content_segments):
            success, message = self.append_segment(segment, i)
            
            if success:
                results["successful_segments"] += 1
            else:
                results["failed_segments"] += 1
                results["failed_details"].append({
                    "segment_index": i,
                    "error": message
                })
            
            # 段落间等待
            if i < len(self.content_segments) - 1:
                print(f"⏳ 等待{wait_between_segments}秒后继续...")
                time.sleep(wait_between_segments)
        
        # 生成总结报告
        success_rate = (results["successful_segments"] / results["total_segments"]) * 100
        results["success_rate"] = round(success_rate, 2)
        
        print("\n" + "="*50)
        print("📊 执行结果总结")
        print("="*50)
        print(f"📋 总段落数: {results['total_segments']}")
        print(f"✅ 成功段落: {results['successful_segments']}")
        print(f"❌ 失败段落: {results['failed_segments']}")
        print(f"📈 成功率: {results['success_rate']}%")
        
        if results['failed_details']:
            print("\n⚠️  失败详情:")
            for detail in results['failed_details']:
                print(f"  段落{detail['segment_index']+1}: {detail['error']}")
        
        if results['success_rate'] >= 90:
            print("\n🎉 文档创建基本成功，可以手动补充失败段落")
        elif results['success_rate'] >= 50:
            print("\n⚠️  文档创建部分成功，建议检查失败段落")
        else:
            print("\n❌ 文档创建失败较多，建议重新尝试")
        
        return results
    
    def verify_document(self) -> Tuple[bool, str]:
        """
        验证文档完整性
        
        Returns:
            (验证状态, 消息)
        """
        if not self.document_id:
            return False, "文档ID未设置"
        
        print("🔍 验证文档完整性...")
        
        try:
            # 使用飞书文档工具的 read 操作验证文档
            # 伪代码：feishu_doc.read(doc_token=self.document_id)
            print("🛠️  调用飞书文档工具读取文档验证...")
            time.sleep(0.5)  # 模拟网络延迟
            
            # 模拟验证结果
            print("✅ 文档验证完成")
            print(f"🔗 文档链接: {self.document_url}")
            
            return True, f"文档验证完成，链接: {self.document_url}"
            
        except Exception as e:
            error_msg = f"文档验证失败: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
    
    def create_complete_document(self, full_content: str) -> Dict:
        """
        完整流程：创建文档并填充内容
        
        Args:
            full_content: 完整内容
            
        Returns:
            完整执行结果
        """
        print("="*50)
        print("🚀 开始创建飞书文档完整流程")
        print("="*50)
        
        # 步骤1：创建文档
        success, message = self.create_document()
        if not success:
            return {"success": False, "message": message, "step": "create_document"}
        
        # 步骤2：等待初始化
        self.wait_for_initialization()
        
        # 步骤3：分割内容
        segments = self.split_content(full_content)
        
        # 步骤4：追加所有段落
        append_results = self.append_all_segments()
        
        # 步骤5：验证文档
        verify_success, verify_message = self.verify_document()
        
        # 整合结果
        final_result = {
            "success": append_results["success_rate"] >= 80 and verify_success,
            "document_id": self.document_id,
            "document_url": self.document_url,
            "append_results": append_results,
            "verify_success": verify_success,
            "verify_message": verify_message,
            "total_steps": 5,
            "completed_steps": 5
        }
        
        print("\n" + "="*50)
        print("🎯 流程完成总结")
        print("="*50)
        print(f"📄 文档标题: {self.title}")
        print(f"📋 文档ID: {self.document_id}")
        print(f"🔗 文档链接: {self.document_url}")
        print(f"📊 内容写入成功率: {append_results['success_rate']}%")
        print(f"✅ 文档验证: {'成功' if verify_success else '失败'}")
        
        if final_result["success"]:
            print("🎉 文档创建流程成功完成！")
        else:
            print("⚠️  文档创建流程部分完成，请检查失败部分")
        
        return final_result


def main():
    """主函数，示例用法"""
    
    # 示例内容 - 通用文档示例
    example_title = "示例文档：Python编程入门"
    
    example_content = """# Python编程入门指南

## 第一章：Python基础

### 1.1 Python简介
Python是一种高级、解释型的编程语言，由Guido van Rossum于1991年创建。它以简洁明了的语法和强大的功能而闻名，广泛应用于Web开发、数据分析、人工智能等领域。

### 1.2 安装Python
1. 访问Python官网下载安装包
2. 按照安装向导完成安装
3. 验证安装：在终端输入`python --version`

### 1.3 第一个Python程序
```python
print("Hello, World!")
```
保存为hello.py，在终端运行：`python hello.py`

## 第二章：基本语法

### 2.1 变量和数据类型
Python支持多种数据类型：
- 整数：`age = 25`
- 浮点数：`price = 19.99`
- 字符串：`name = "Alice"`
- 布尔值：`is_student = True`
- 列表：`fruits = ["apple", "banana", "orange"]`

### 2.2 控制流
```python
# 条件语句
if age >= 18:
    print("成年人")
else:
    print("未成年人")

# 循环语句
for i in range(5):
    print(i)

# while循环
count = 0
while count < 5:
    print(count)
    count += 1
```

### 2.3 函数
```python
def greet(name):
    return f"Hello, {name}!"

result = greet("Alice")
print(result)  # 输出：Hello, Alice!
```

## 第三章：高级特性

### 3.1 列表推导式
```python
# 生成1到10的平方列表
squares = [x**2 for x in range(1, 11)]
print(squares)  # 输出：[1, 4, 9, 16, 25, 36, 49, 64, 81, 100]
```

### 3.2 异常处理
```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("不能除以零")
finally:
    print("程序执行完毕")
```

### 3.3 文件操作
```python
# 写入文件
with open("example.txt", "w") as file:
    file.write("Hello, Python!")

# 读取文件
with open("example.txt", "r") as file:
    content = file.read()
    print(content)
```

## 第四章：实际应用

### 4.1 Web开发
使用Flask框架创建简单的Web应用：
```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run()
```

### 4.2 数据分析
使用pandas库处理数据：
```python
import pandas as pd

# 创建DataFrame
data = {'Name': ['Alice', 'Bob', 'Charlie'],
        'Age': [25, 30, 35],
        'City': ['New York', 'London', 'Tokyo']}
df = pd.DataFrame(data)

print(df)
```

### 4.3 自动化脚本
```python
import os
import datetime

# 获取当前时间
now = datetime.datetime.now()
print(f"当前时间：{now}")

# 列出目录内容
files = os.listdir('.')
print(f"当前目录文件：{files}")
```

## 学习资源

### 推荐书籍
1. 《Python编程：从入门到实践》
2. 《流畅的Python》
3. 《Python Cookbook》

### 在线资源
1. Python官方文档
2. W3Schools Python教程
3. Real Python教程网站

### 练习项目
1. 计算器程序
2. 待办事项应用
3. 天气查询工具
4. 简单的博客系统

---
文档说明：这是一个通用的Python编程入门指南示例，用于演示文档创建功能。实际使用时，可以根据用户需求创建各种类型的文档。"""
    
    # 创建文档
    creator = FeishuDocCreator(example_title)
    result = creator.create_complete_document(example_content)
    
    # 输出结果
    print("\n" + "="*50)
    print("📋 最终结果")
    print("="*50)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    return result


if __name__ == "__main__":
    main()
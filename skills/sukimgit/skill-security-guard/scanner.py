#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skill 安全扫描器
基于 DeepSeek 设计方案
"""

import os
import re
import ast
from pathlib import Path
from typing import List, Dict

# 危险操作检测模式（按风险等级分类）
DANGER_PATTERNS = {
    'critical': [
        {
            'name': '远程代码执行',
            'patterns': [
                r'eval\s*\(\s*requests\.get\s*\([^)]+\)\.text\s*\)',
                r'exec\s*\(\s*urllib\.request\.urlopen\s*\([^)]+\)\.read\s*\(\)\s*\)',
                r'__import__\s*\(\s*["\']os["\']\s*\)\.system\s*\(\s*requests\.get\s*\(',
                r'pickle\.loads\s*\(\s*base64\.b64decode\s*\(\s*requests\.get\s*\(',
            ]
        },
        {
            'name': '数据外传',
            'patterns': [
                r'requests\.post\s*\(\s*["\']https?://[^"\']*?(?:ngrok|serveo|localtunnel|webhook)[^"\']*["\']',
                r'urllib\.request\.urlopen\s*\(\s*["\']https?://[^"\']*?(?:pastebin|gist|discord|slack)',
            ]
        }
    ],
    'high': [
        {
            'name': '敏感文件读取',
            'patterns': [
                r'open\s*\(\s*["\'](?:\.env|config\.(?:json|yml|yaml)|id_rsa|\.aws/credentials|\.ssh/|passwd|shadow)["\']',
                r'(?:pwd|token|secret|key|password)\s*=\s*open\s*\([^)]+\)\.read\s*\(\)',
            ]
        },
        {
            'name': '批量文件操作',
            'patterns': [
                r'(?:shutil\.rmtree|os\.remove|os\.unlink)\s*\(\s*(?:["\']/|os\.path\.expanduser\(["\']~)',
                r'for\s+\w+\s+in\s+os\.listdir\s*\([^)]+\):\s*(?:(?!if).)*?os\.(?:remove|unlink)',
            ]
        }
    ],
    'medium': [
        {
            'name': '系统命令执行',
            'patterns': [
                r'os\.system\s*\(\s*["\'](?:rm|del|wget|curl|chmod|chown)',
                r'subprocess\.(?:Popen|call|run)\s*\(\s*\[?\s*["\'](?:rm|sh|bash|cmd|powershell)',
            ]
        },
        {
            'name': '动态导入/执行',
            'patterns': [
                r'__import__\s*\(\s*\w+\s*\)',
                r'globals\(\)\.(?:get|\[\w+\])\s*\([^)]*\)',
            ]
        }
    ]
}

# 安全使用模式
SAFE_PATTERNS = {
    'smtplib': [
        r'smtplib\.SMTP\s*\(\s*["\']smtp\.gmail\.com["\']',
        r'smtp\.sendmail\s*\(\s*["\'].+?@.+?\.[a-z]+["\']',
    ],
    'requests': [
        r'requests\.get\s*\(\s*["\']https?://api\.github\.com',
        r'requests\.get\s*\(\s*["\']https?://[^"\']*?(?:weather|stock|news)',
    ],
}

# 安全上下文关键字
SAFE_CONTEXTS = [
    r'def\s+(?:fetch|download|get|load|read)_',
    r'class\s+(?:Fetcher|Downloader|Loader)',
    r'logger\.(?:debug|info)',
]

class SkillSecurityScanner:
    def __init__(self):
        self.score = 100
        self.findings = []
        self.risk_score = {
            'critical': 50,
            'high': 30,
            'medium': 15,
            'low': 5
        }
    
    def scan(self, skill_directory: str) -> Dict:
        """扫描指定目录"""
        skill_path = Path(skill_directory)
        if not skill_path.exists():
            raise FileNotFoundError(f"目录不存在: {skill_directory}")
        
        print(f"开始扫描 Skill: {skill_directory}")
        
        for py_file in skill_path.rglob("*.py"):
            self._scan_file(py_file)
        
        return self._generate_report()
    
    def _scan_file(self, file_path: Path):
        """扫描单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检测危险模式
            for risk_level, pattern_groups in DANGER_PATTERNS.items():
                for group in pattern_groups:
                    for pattern in group['patterns']:
                        if re.search(pattern, content, re.IGNORECASE):
                            self.findings.append({
                                'file': str(file_path),
                                'type': group['name'],
                                'risk_level': risk_level,
                            })
                            self.score -= self.risk_score[risk_level]
                            
                            if risk_level == 'critical':
                                self.score = 0
                                return
        except Exception as e:
            print(f"扫描文件出错: {e}")
    
    def _generate_report(self) -> Dict:
        """生成报告"""
        self.score = max(0, min(100, self.score))
        
        if self.score >= 80:
            status = "安全"
        elif self.score >= 50:
            status = "需要审核"
        else:
            status = "高风险"
        
        return {
            'overall_risk_score': self.score,
            'overall_risk_level': status,
            'total_findings': len(self.findings),
            'findings': self.findings,
        }

def print_report(report: Dict):
    """打印报告"""
    print("\n" + "="*60)
    print("Skill 安全扫描报告")
    print("="*60)
    print(f"总体风险评分: {report['overall_risk_score']}/100")
    print(f"总体风险等级: {report['overall_risk_level']}")
    print(f"发现的安全问题数量: {report['total_findings']}")
    print("="*60)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("用法: python scanner.py <skill_directory>")
        sys.exit(1)
    
    scanner = SkillSecurityScanner()
    report = scanner.scan(sys.argv[1])
    print_report(report)
"""Heuristic domain classifier for OpenClaw sessions.

Classifies conversations into one of 13 predefined domain categories
based on keywords in user messages and tool usage patterns.
"""

import re
from typing import Optional

# Domain definitions with keyword patterns and tool indicators
DOMAINS = {
    "development": {
        "keywords": [
            "代码", "code", "debug", "调试", "bug", "编程", "函数", "function",
            "class", "编译", "compile", "build", "git", "commit", "push",
            "pull request", "PR", "merge", "test", "测试", "重构", "refactor",
            "API", "接口", "前端", "后端", "frontend", "backend", "react",
            "vue", "python", "javascript", "typescript", "java", "golang",
            "rust", "npm", "pip", "docker", "k8s", "kubernetes",
            "数据库", "database", "sql", "redis", "mongodb",
            "爬虫", "crawler", "spider", "游戏", "game",
        ],
        "tools": ["exec", "read", "write", "edit", "apply_patch"],
        "tool_weight": 0.3,
    },
    "system_admin": {
        "keywords": [
            "安装", "install", "配置", "config", "nginx", "apache",
            "ssh", "服务器", "server", "部署", "deploy", "进程", "process",
            "权限", "permission", "防火墙", "firewall", "系统", "system",
            "磁盘", "disk", "内存", "memory", "CPU", "网络", "network",
            "DNS", "域名", "SSL", "证书", "certificate", "备份", "backup",
            "容器", "container", "虚拟机", "VM", "proxy", "代理", "VPN",
        ],
        "tools": ["exec", "process"],
        "tool_weight": 0.2,
    },
    "data_analysis": {
        "keywords": [
            "数据分析", "data analysis", "数据清洗", "统计", "statistics",
            "可视化", "visualization", "图表", "chart", "pandas", "numpy",
            "matplotlib", "模型", "model", "机器学习", "machine learning",
            "特征", "feature", "回归", "regression", "分类", "classification",
            "聚类", "clustering", "数据集", "dataset", "CSV", "Excel",
            "数据挖掘", "data mining", "ETL", "指标", "metric",
        ],
        "tools": ["exec", "read"],
        "tool_weight": 0.2,
    },
    "research": {
        "keywords": [
            "搜索", "search", "查找", "find", "调研", "research", "论文", "paper",
            "文献", "literature", "查询", "query", "百科", "wiki", "新闻", "news",
            "了解", "了解一下", "是什么", "what is", "how to", "怎么",
            "对比", "compare", "评测", "review", "推荐", "recommend",
            "行业", "industry", "市场", "market", "趋势", "trend",
        ],
        "tools": ["web_search", "web_fetch", "browser"],
        "tool_weight": 0.5,
    },
    "content_creation": {
        "keywords": [
            "写", "write", "文章", "article", "博客", "blog", "文案", "copy",
            "翻译", "translate", "摘要", "summary", "润色", "polish",
            "标题", "title", "大纲", "outline", "报告", "report",
            "简书", "公众号", "微信", "文档", "document", "教程", "tutorial",
            "创作", "create", "内容", "content", "营销", "marketing",
        ],
        "tools": [],
        "tool_weight": 0.0,
    },
    "communication": {
        "keywords": [
            "飞书", "feishu", "lark", "telegram", "slack", "discord",
            "微信", "wechat", "邮件", "email", "消息", "message",
            "通知", "notification", "推送", "push", "群", "group",
            "频道", "channel", "聊天", "chat", "发送", "send",
        ],
        "tools": [],
        "tool_weight": 0.0,
    },
    "media_processing": {
        "keywords": [
            "图片", "image", "照片", "photo", "视频", "video", "音频", "audio",
            "OCR", "识别", "recognize", "截图", "screenshot", "PDF",
            "生成图", "generate image", "语音", "voice", "TTS", "ASR",
            "字幕", "subtitle", "剪辑", "edit video", "转码", "transcode",
        ],
        "tools": ["browser"],
        "tool_weight": 0.3,
    },
    "automation": {
        "keywords": [
            "自动化", "automation", "工作流", "workflow", "脚本", "script",
            "定时", "cron", "schedule", "触发", "trigger", "编排", "orchestrate",
            "agent", "智能体", "bot", "机器人", "pipeline", "流水线",
            "批量", "batch", "循环", "loop", "监听", "listen",
        ],
        "tools": ["exec", "process"],
        "tool_weight": 0.2,
    },
    "monitoring": {
        "keywords": [
            "监控", "monitor", "告警", "alert", "健康检查", "health check",
            "日志", "log", "诊断", "diagnose", "性能", "performance",
            "状态", "status", "运行", "running", "故障", "fault",
            "巡检", "inspection", "metrics", "指标",
        ],
        "tools": ["process", "exec"],
        "tool_weight": 0.3,
    },
    "scheduling": {
        "keywords": [
            "日程", "schedule", "提醒", "remind", "待办", "todo",
            "计划", "plan", "日历", "calendar", "任务", "task",
            "每日", "daily", "每周", "weekly", "日报", "周报",
            "安排", "arrange", "时间", "time", "截止", "deadline",
        ],
        "tools": [],
        "tool_weight": 0.0,
    },
    "knowledge_mgmt": {
        "keywords": [
            "知识库", "knowledge base", "记忆", "memory", "笔记", "note",
            "文档管理", "document management", "归档", "archive",
            "索引", "index", "检索", "retrieve", "RAG",
            "知识图谱", "knowledge graph", "分类", "categorize",
        ],
        "tools": ["read", "write"],
        "tool_weight": 0.2,
    },
    "finance": {
        "keywords": [
            "金融", "finance", "股票", "stock", "交易", "trade", "trading",
            "量化", "quantitative", "K线", "kline", "行情", "market",
            "基金", "fund", "投资", "invest", "收益", "return", "profit",
            "回测", "backtest", "策略", "strategy", "期货", "futures",
            "期权", "option", "加密货币", "crypto", "比特币", "bitcoin",
        ],
        "tools": ["web_search", "exec"],
        "tool_weight": 0.3,
    },
    "crm": {
        "keywords": [
            "客户", "customer", "client", "销售", "sales", "CRM",
            "电商", "e-commerce", "订单", "order", "运营", "operation",
            "转化", "conversion", "获客", "acquisition", "商务", "business",
            "供应商", "supplier", "报价", "quote", "合同", "contract",
        ],
        "tools": [],
        "tool_weight": 0.0,
    },
}

VALID_DOMAIN_IDS = list(DOMAINS.keys())


def classify_domain(
    user_texts: list[str],
    tool_names: list[str],
) -> str:
    """Classify a conversation into one of 13 domain categories.

    Args:
        user_texts: List of user message text content (after metadata stripping)
        tool_names: List of tool names used in the conversation

    Returns:
        Domain ID string (e.g., "development", "research")
    """
    combined_text = " ".join(user_texts).lower()
    tool_set = set(tool_names)

    scores: dict[str, float] = {}

    for domain_id, config in DOMAINS.items():
        score = 0.0

        # Keyword matching with word boundary awareness
        for kw in config["keywords"]:
            kw_lower = kw.lower()
            # For short English keywords (<=4 chars), use word boundary regex
            # to avoid false positives like "test" matching "latest"
            # For Chinese keywords or longer terms, substring match is fine
            if len(kw_lower) <= 4 and kw_lower.isascii():
                if re.search(r"\b" + re.escape(kw_lower) + r"\b", combined_text):
                    score += 1.0
            else:
                if kw_lower in combined_text:
                    score += 1.0

        # Tool usage matching
        tool_weight = config["tool_weight"]
        if tool_weight > 0 and config["tools"]:
            matching_tools = tool_set & set(config["tools"])
            if matching_tools:
                score += len(matching_tools) * tool_weight

        scores[domain_id] = score

    # Return highest scoring domain, default to "research" if no matches
    if not scores or max(scores.values()) == 0:
        return "research"

    return max(scores, key=scores.get)

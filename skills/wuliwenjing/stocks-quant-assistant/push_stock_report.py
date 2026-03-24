#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时推送入口（供 launchd/cron 调用）
根据当前北京时间自动判断推送时段
"""
import os
import sys
from datetime import datetime

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SKILL_DIR)

from stock_monitor import check_and_install, load_config, generate_report, push_report

def auto_mode():
    """根据当前北京时间自动选择推送时段"""
    hour = datetime.now().hour
    if hour < 10:
        return 'morning'    # 09:15 -> 开盘前
    elif hour < 12:
        return 'noon'       # 10:30 -> 早盘
    elif hour < 14:
        return 'afternoon'  # 13:00 -> 午后
    else:
        return 'evening'    # 14:50 -> 尾盘

def main():
    check_and_install()  # 幂等：已安装则立即返回
    # 优先用命令行参数（手动测试时指定），否则自动判断
    mode = sys.argv[1] if len(sys.argv) > 1 else auto_mode()
    config = load_config()
    report = generate_report(config, mode)
    push_report(report, config)

if __name__ == '__main__':
    main()

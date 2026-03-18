import os
import datetime
from icalendar import Calendar

# 获取数据文件路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICS_PATH = os.path.join(BASE_DIR, 'data', 'cn_zh.ics')

def get_holiday_map():
    holiday_map = {}
    if not os.path.exists(ICS_PATH):
        return holiday_map
    
    with open(ICS_PATH, 'rb') as f:
        cal = Calendar.from_ical(f.read())
        for component in cal.walk():
            if component.name == "VEVENT":
                summary = str(component.get('summary'))
                dtstart = component.get('dtstart').dt
                
                # 兼容 date 和 datetime
                if isinstance(dtstart, datetime.datetime):
                    date_key = dtstart.date()
                else:
                    date_key = dtstart
                    
                holiday_map[date_key] = summary
    return holiday_map

def check_date(target_date):
    """
    判断 target_date (date object) 是工作日还是休息日
    """
    holiday_map = get_holiday_map()
    
    # 1. 检查是否有特殊事件
    if target_date in holiday_map:
        event = holiday_map[target_date]
        if '班' in event:
            return "工作日", event
        elif '休' in event:
            return "休息日", event
        # 其他类型节日，依然按周判断
    
    # 2. 按自然周判断 (周一至周五=工作日，周六至周日=休息日)
    if target_date.weekday() < 5:
        return "工作日", "正常工作日"
    else:
        return "休息日", "正常周末"

if __name__ == "__main__":
    # 测试指定日期: 2026-9-25
    test_date = datetime.date(2026, 9, 25)
    status, detail = check_date(test_date)
    print(f"日期: {test_date}, 状态: {status}, 详情: {detail}")

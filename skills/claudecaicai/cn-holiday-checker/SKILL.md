# 中国节假日助手 (cn-holiday-checker) / Chinese Holiday Assistant (cn-holiday-checker)

该技能用于查询中国节假日、调休安排及工作日判定。
This skill is used for querying Chinese holidays, work-shift arrangements, and workday determination.

## 功能说明 / Functionality
- **节假日识别 / Holiday Recognition**：自动同步 iCloud 节假日数据。 / Automatically synchronize iCloud holiday data.
- **自动判定 / Automatic Determination**：优先匹配节假日/调休事件；若无匹配，则根据自然周（周一至周五工作日，周六至周日休息日）进行判定。 / Prioritizes matching holiday/work-shift events; if no match, determines based on the natural week (Mon-Fri as workday, Sat-Sun as rest day).
- **自动更新 / Automatic Update**：通过 `cron` 定时任务每月自动拉取最新日历数据。 / Automatically pulls the latest calendar data monthly via `cron`.

## 环境要求 / Requirements
- Python 3.x
- 已安装依赖 / Installed dependencies: `requests`, `icalendar`

## 使用方法 / Usage

### 1. 查询指定日期 / Query a specific date
调用 `scripts/holiday_checker.py` 并传入日期（需修改脚本中 `__main__` 部分的测试日期）：
Call `scripts/holiday_checker.py` and pass the date (you need to modify the test date in the `__main__` section of the script):
```bash
python3 cn-holiday-checker/scripts/holiday_checker.py
```

### 2. 手动更新数据 / Manual Data Update
如果需要立即更新节假日数据，请运行：
If you need to update holiday data immediately, please run:
```bash
python3 cn-holiday-checker/scripts/download_ics.py
```

## 配置说明 (config.json) / Configuration (config.json)
- 存放技能相关的环境变量。 / Stores environment variables related to the skill.
- 支持 `PRIMARY_URL` (主数据源) 与 `BACKUP_URL` (备用数据源)。 / Supports `PRIMARY_URL` and `BACKUP_URL` (backup data source).
- 脚本会自动向上回溯识别 `config.json` 文件，确保迁移目录后配置依然有效。 / The script automatically traces upward to identify the `config.json` file, ensuring configuration remains valid after migrating the directory.

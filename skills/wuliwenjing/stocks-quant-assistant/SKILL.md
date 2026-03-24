---
name: stock-monitor
version: 3.0.5
description: A股股票量化监控与每日推送系统。用户配置股票池后自动分析 MA/MACD/RSI/布林带，生成信号评分和操作建议，每日4次定时推送。支持持仓跟踪、板块轮动、美股隔夜。下载后只需填写配置文件，即可每日自动推送到飞书/Telegram。
---

# 📈 stock-monitor

**A 股量化监控 + 定时推送系统**

首次运行自动安装依赖 + 注册定时任务，每日 4 次自动推送。

---

## ⚠️ 安装后必读：3 步完成配置

### 第一步：获取飞书凭证

**如果你已经有飞书应用（app_id + app_secret），跳过此步。**

1. 打开 [飞书开放平台](https://open.feishu.cn/app) → 创建应用
2. 在「凭证与基础信息」复制 `App ID` 和 `App Secret`
3. 在「权限管理」中申请：`im:message:send_as_bot`
4. 在「应用发布」→「版本管理与发布」中发布应用
5. 在群里添加「自定义机器人」，复制 `chat_id`（格式：`oc_xxxx`）

### 第二步：编辑配置文件

打开 `config.yaml`（或 `config.local.yaml`），填写你的股票和凭证：

```yaml
stocks:
  - code: "000001"          # 股票代码（6位数字）
    name: "平安银行"         # 显示名称
    market: "sz"             # sz=深交所，sh=上交所
    emoji: "🏦"              # 自定义图标
    position:                # 持仓（可选）
      cost: 12.50            # 成本价
      quantity: 1000         # 股数

push:
  channel: "feishu"          # 推送渠道：feishu / telegram / console
  feishu:
    app_id: "cli_xxxxxxxx"   # ← 填入你的 app_id
    app_secret: "xxxxxxxx"   # ← 填入你的 app_secret
    chat_id: "oc_xxxxxxx"    # ← 填入你的 chat_id
  times:
    - "09:15"               # 开盘前
    - "10:30"               # 早盘
    - "13:00"               # 午后
    - "14:50"               # 尾盘
```

**配置文件优先级：`config.local.yaml` > `config.yaml`**
（私人配置写 `config.local.yaml`，不会被 skill 发布覆盖）

### 第三步：测试推送

```bash
python3 ~/.openclaw/workspace/skills/stocks-quant-assistant/stock_monitor.py morning
```

看到股票分析输出 + 飞书收到消息 = 配置成功 ✅

---

## 常见问题排查

### ❌ 报错 "Feishu push failed" / 飞书没收到

**原因：凭证填写不完整**

请确认 `config.yaml` 中 `feishu` 区块三个字段都有值：
- `app_id`（格式：`cli_xxxxxxxx`）
- `app_secret`
- `chat_id`（格式：`oc_xxxxxxxx`）

**检查方法：**
```bash
grep -A5 "feishu:" ~/.openclaw/workspace/skills/stocks-quant-assistant/config.yaml
```

### ❌ 报错 "launchd 注册失败" / 定时推送没收到

**原因：macOS 权限限制，launchd 需要手动授权**

手动运行以下命令：
```bash
launchctl load ~/Library/LaunchAgents/com.openclaw.stock-monitor.plist
```

如果提示「需要管理员权限」，加上 `sudo`：
```bash
sudo launchctl load ~/Library/LaunchAgents/com.openclaw.stock-monitor.plist
```

**检查定时任务是否运行：**
```bash
launchctl list | grep stock
```

### ❌ 提示「实时数据获取失败」

网络波动导致。新浪财经接口偶尔超时，不影响后续推送。下次定时任务会自动恢复。

### ❌ 报告里没有大盘指数/技术指标

可能是新浪接口响应慢，数据获取超时。系统会自动降级为简化模式（只显示实时价格）。

---

## 定时任务状态检查

```bash
# macOS - 查看 launchd 任务
launchctl list | grep stock

# 查看最近一次推送日志
cat ~/.openclaw/workspace/skills/stocks-quant-assistant/logs/launchd.log
cat ~/.openclaw/workspace/skills/stocks-quant-assistant/logs/launchd.err
```

---

## 手动触发推送

```bash
# 开盘前（09:15）
python3 stock_monitor.py morning

# 早盘（10:30）
python3 stock_monitor.py noon

# 午后（13:00）
python3 stock_monitor.py afternoon

# 尾盘（14:50）
python3 stock_monitor.py evening
```

---

## 信号评分规则

| 分数 | 信号 | 含义 |
|------|------|------|
| ≥7 | 🟢 强烈买入 | 多个指标共振，看涨信号强 |
| 4~6 | 🟢 买入 | 技术面不错，可以考虑买入 |
| -3~3 | 🟡 持有 | 中性信号，建议观望 |
| -6~-4 | 🔴 卖出 | 技术面偏弱，考虑减仓 |
| ≤-7 | 🔴 强烈卖出 | 技术面很弱，建议清仓 |

---

## 技术指标通俗解释

| 指标 | 是什么 | 怎么看 |
|------|--------|--------|
| **MA（均线）** | 过去N天平均价格连线 | 多头排列（短>长）= 上涨；空头排列 = 下跌 |
| **MACD** | 快线、慢线、红绿柱 | **金叉**=买入信号；**死叉**=卖出信号 |
| **RSI** | 涨跌强度，0~100 | >70超买可能回调；<30超卖可能反弹 |
| **布林带** | 价格通道（上轨/中轨/下轨） | 价格碰下轨可能反弹；碰上轨可能回落 |

---

## 市场代码

| 市场 | 代码 | 示例 |
|------|------|------|
| 上交所 | `sh` | 600519（茅台）、588080（科创50ETF） |
| 深交所 | `sz` | 000001（平安）、002131（利欧） |
| 北交所 | `bj` | 8开头股票 |

---

## ⚠️ 注意事项

1. 本系统仅作为投资参考，不构成投资建议
2. 历史数据不代表未来走势
3. 依赖网络获取实时数据，网络波动时可能降级为简化模式

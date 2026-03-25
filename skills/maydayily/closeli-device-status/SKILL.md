---
name: api-device-status
description: "调用 ai-open-gateway 的设备状态查询接口 POST /api/device/status，批量查询设备在线或离线状态。Use when: 需要检查设备是否在线、批量监控设备状态。⚠️ 需设置 AI_GATEWAY_API_KEY。"
metadata:
  openclaw:
    requires:
      bins: ["python3"]
      env: ["AI_GATEWAY_API_KEY"]
    primaryEnv: "AI_GATEWAY_API_KEY"
    configPaths: ["~/.openclaw/.env"]
---

# 设备状态查询接口

`POST /api/device/status` 用于批量查询设备的在线/离线状态。

## ⚠️ 展示规则（MUST 严格遵守）

脚本输出 JSON 格式的结构化数据，这是预期行为。以下展示规则是给 agent 的格式化指令：agent MUST 解析脚本输出的 JSON，按下述规则转换为用户友好的格式后再展示，MUST NOT 直接展示原始 JSON。

脚本输出中包含 `_device_names` 字段（device_id → device_name 映射），用于展示设备名称。

1. 当 `code == 0` 且 `data` 非空时，以表格展示：

| 设备名称 | MAC 地址 | 状态 |
|----------|----------|------|
| 客厅摄像机 | aabbccddeeff | 🟢 在线 |
| 门口摄像机 | 112233445566 | 🔴 离线 |

关键规则：
- 从 `_device_names` 中查找 device_id 对应的设备名称，找不到则显示"未知设备"
- device_id MUST 去掉 `xxxxS_` 前缀再展示为 MAC 地址
- 状态映射：`"online"` → `🟢 在线`，`"offline"` → `🔴 离线`

2. 当 `data` 为空 `{}` 时，回复："请求的设备均不属于当前用户，无可查询的设备。"
3. 当 `code != 0` 时，回复："接口调用失败，错误码 {code}，原因：{message}"

## 前置依赖

脚本依赖 httpx。如果未安装，脚本会提示 `python3 -m pip install httpx`。

## 配置声明

本 skill 依赖以下配置项，agent 和用户 MUST 在运行前确认已正确配置。

### 必需配置

| 配置项 | 传递方式 | 说明 |
|--------|----------|------|
| AI_GATEWAY_API_KEY | 环境变量（推荐）、`~/.openclaw/.env`（fallback）、命令行 `--api-key` | API 密钥，用于接口鉴权。脚本按此优先级自动获取 |

### 可选配置

| 配置项 | 传递方式 | 默认值 | 说明 |
|--------|----------|--------|------|
| AI_GATEWAY_HOST | 环境变量、`~/.openclaw/.env` | `https://ai-open-gateway.closeli.cn` | 网关地址 |
| AI_GATEWAY_VERIFY_SSL | 环境变量 | true | 设为 false 可禁用 TLS 证书验证（仅限开发环境） |
| AI_GATEWAY_NO_ENV_FILE | 环境变量 | false | 设为 true 可禁用 `~/.openclaw/.env` fallback 读取（生产环境推荐） |

### Fallback 配置路径

脚本默认会读取 `~/.openclaw/.env` 文件作为 fallback 配置源。该文件为所有 skill 共享，格式为 `KEY=VALUE`（每行一条）。生产环境 MUST 设置 `AI_GATEWAY_NO_ENV_FILE=true` 禁用此 fallback，改为通过环境变量直接传递所有配置。

## 安全注意事项

- 共享凭证文件 `~/.openclaw/.env` 可被同一用户下所有 skill 读取。生产环境 MUST 通过环境变量传递 API_KEY，MUST NOT 依赖共享凭证文件
- TLS 证书验证默认启用，MUST NOT 在生产环境禁用（禁用会导致中间人攻击风险，攻击者可截获 API_KEY 和设备数据）
- 使用前 MUST 确认 AI_GATEWAY_HOST 指向可信域名
- MUST 使用最小权限的 API_KEY，避免复用高权限凭证。本 skill 仅需设备状态查询权限

## 网络访问声明

本 skill 仅访问以下端点（均为 AI_GATEWAY_HOST 下的路径）：

| 端点 | 方法 | 用途 |
|------|------|------|
| /api/device/list | POST | 获取设备名称映射 |
| /api/device/status | POST | 查询设备在线/离线状态 |

脚本不访问任何其他网络资源。

## 快速开始

```bash
python3 check_status.py --device-ids "xxxxS_aabbccddeeff"
```

查询多台设备（逗号分隔）：

```bash
python3 check_status.py --device-ids "xxxxS_aabbccddeeff,xxxxS_112233445566"
```

## 请求格式

### 请求体

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| device_ids | string[] | 是 | 设备 ID 列表，不能为空数组。格式: `xxxxS_<mac>` |

## 响应格式

```json
{
  "code": 0,
  "message": "success",
  "request_id": "<32位请求追踪ID>",
  "data": {
    "xxxxS_aabbccddeeff": { "status": "online" },
    "xxxxS_112233445566": { "status": "offline" }
  },
  "_device_names": {
    "xxxxS_aabbccddeeff": "客厅摄像机",
    "xxxxS_112233445566": "门口摄像机"
  }
}
```

### data 字段（Map 结构）

key 为 device_id，value 为状态对象：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| status | string | 设备状态，值为 `"online"` 或 `"offline"` |

## 错误码

| 错误码 | HTTP 状态码 | 说明 |
|--------|------------|------|
| 1001 | 401 | 未提供 api_key |
| 1002 | 401 | api_key 无效或已禁用 |
| 2001 | 400 | 缺少必要参数（device_ids 为空数组） |
| 3001 | 502 | 网关内部服务调用失败 |
| 3002 | 502 | 网关内部服务调用失败 |
| 3004 | 502 | 网关内部服务调用失败 |
| 5000 | 500 | 内部错误 |

## 注意事项

- device_ids 不能为空数组，否则返回错误码 2001
- 不属于当前用户的设备会被静默过滤，不会返回错误
- 全局请求超时为 120 秒

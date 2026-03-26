# CompShare API 参考文档

## 目录
1. [概述](#概述)
2. [认证方式](#认证方式)
3. [公共参数](#公共参数)
4. [API接口详情](#api接口详情)
5. [SSH客户端使用指南](#ssh客户端使用指南)
6. [错误码说明](#错误码说明)
7. [最佳实践](#最佳实践)

---

## 概述

CompShare是优云智算平台提供的GPU云服务器服务。本文档详细说明了所有API接口的参数、响应格式和使用方法。

**API基础地址**: `https://api.compshare.cn/`

**支持的GPU类型**: P40、2080、3090、3080Ti、4090、A800、A100、H20

---

## 认证方式

### 获取API密钥
1. 登录CompShare控制台: https://console.compshare.cn/
2. 进入「API管理」页面: https://console.compshare.cn/uaccount/api_manage
3. 创建或查看 `public_key` 和 `private_key`

### 密钥使用
在使用SDK或直接调用API时，需要在请求中携带这两个密钥：
- `public_key`: 公钥，用于标识用户身份
- `private_key`: 私钥，用于签名验证

### 配置文件
在 `assets/config.yaml` 中配置凭证：
```yaml
compshare:
  public_key: "your-public-key"
  private_key: "your-private-key"
  region: "cn-wlcb"
  zone: "cn-wlcb-01"
  base_url: "https://api.compshare.cn"
```

---

## 公共参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| Region | string | 是 | 地域，固定为 `cn-wlcb` |
| Zone | string | 是 | 可用区，固定为 `cn-wlcb-01` |
| ProjectId | string | 否 | 项目ID，不填写为默认项目 |

---

## API接口详情

### 1. 创建GPU实例 - CreateCompShareInstance

创建一台新的GPU云服务器实例。

#### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| Region | string | 是 | 地域: cn-wlcb |
| Zone | string | 是 | 可用区: cn-wlcb-01 |
| MachineType | string | 是 | 云主机机型，GPU固定为 `G` |
| GPU | int | 是 | GPU卡核心数 |
| GpuType | string | 是 | GPU类型: P40/2080/3090/3080Ti/4090/A800/A100/H20 |
| CPU | int | 是 | 虚拟CPU核数，范围1-64 |
| Memory | int | 是 | 内存大小(MB)，范围1024-262144，需为1024的倍数 |
| CompShareImageId | string | 是 | 镜像ID |
| Disks.N.IsBoot | bool | 是 | 是否为系统盘，系统盘必须为True |
| Disks.N.Type | string | 是 | 磁盘类型: CLOUD_SSD |
| Disks.N.Size | int | 是 | 磁盘大小(GB) |
| Name | string | 否 | 实例名称 |
| Password | string | 否 | 登录密码，需base64编码 |
| ChargeType | string | 否 | 计费模式: Month/Day/Dynamic/Postpay，默认Dynamic |
| Quantity | int | 否 | 购买时长，月付时为月数 |

#### 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| RetCode | int | 返回码，0表示成功 |
| Action | string | 操作名称 |
| UHostIds | array | 实例ID集合 |
| IPs | array | 分配的IP地址集合 |

#### 使用示例

```bash
# 使用命令行脚本
python scripts/compshare_client.py create \
  --gpu-type 4090 \
  --gpu-count 1 \
  --cpu 16 \
  --memory 64 \
  --disk-size 200 \
  --name "my-gpu-instance"
```

---

### 2. 查询实例列表 - DescribeCompShareInstance

获取用户所有或指定的GPU实例信息列表。

#### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| Region | string | 否 | 地域 |
| Zone | string | 否 | 可用区 |
| UHostIds.N | array | 否 | 实例ID数组，不传则返回所有 |
| Offset | int | 否 | 列表起始位置偏移量，默认0 |
| Limit | int | 否 | 返回数据长度，默认20，最大100 |

#### 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| RetCode | int | 返回码 |
| Action | string | 操作名称 |
| TotalCount | int | 实例总数 |
| UHostSet | array | 实例详情列表 |

#### 实例详情字段 (UHostSet)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| UHostId | string | 实例ID |
| Name | string | 实例名称 |
| State | string | 实例状态: Running/Stopped/Pending |
| IP | string | 实例IP地址 |
| Zone | string | 可用区 |
| MachineType | string | 机型信息 |
| GPU | int | GPU数量 |
| GPUType | string | GPU类型 |
| CPU | int | CPU核数 |
| Memory | int | 内存大小(MB) |
| CompShareImageId | string | 镜像ID |
| CompShareImageName | string | 镜像名称 |
| ChargeType | string | 计费模式 |
| CreateTime | int | 创建时间戳 |
| ExpireTime | int | 到期时间戳 |
| SshLoginCommand | string | SSH登录命令 |
| Password | string | 登录密码 |

#### 使用示例

```bash
# 查询所有实例
python scripts/compshare_client.py list

# 查询指定实例
python scripts/compshare_client.py list --instance-ids "uhost-xxxxx"
```

---

### 3. 启动实例 - StartCompShareInstance

启动已关机的GPU实例。

#### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| Region | string | 是 | 地域 |
| Zone | string | 是 | 可用区 |
| UHostId | string | 是 | 实例ID |
| WithoutGpu | bool | 否 | 是否无卡启动，默认False |

#### 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| RetCode | int | 返回码 |
| Action | string | 操作名称 |
| UHostId | string | 实例ID |

#### 启动模式说明

| 模式 | 参数 | 说明 |
|------|------|------|
| 正常开机 | WithoutGpu=False 或不传 | GPU正常加载，正常计费 |
| 无卡开机 | WithoutGpu=True | GPU不加载，节省费用 |

#### 使用示例

```bash
# 正常开机（带GPU）
python scripts/compshare_client.py start --instance-id uhost-xxxxx

# 无卡开机（不带GPU，节省费用）
python scripts/compshare_client.py start --instance-id uhost-xxxxx --without-gpu
```

---

### 4. 停止实例 - StopCompShareInstance

关闭运行中的GPU实例。

#### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| Region | string | 是 | 地域 |
| Zone | string | 是 | 可用区 |
| UHostId | string | 是 | 实例ID |

#### 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| RetCode | int | 返回码 |
| Action | string | 操作名称 |
| UHostId | string | 实例ID |

#### 使用示例

```bash
python scripts/compshare_client.py stop --instance-id uhost-xxxxx
```

---

### 5. 重启实例 - RebootCompShareInstance

重启运行中的GPU实例。

#### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| Region | string | 是 | 地域 |
| Zone | string | 是 | 可用区 |
| UHostId | string | 是 | 实例ID |

#### 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| RetCode | int | 返回码 |
| Action | string | 操作名称 |
| UHostId | string | 实例ID |

#### 使用示例

```bash
python scripts/compshare_client.py reboot --instance-id uhost-xxxxx
```

---

### 6. 重置实例密码 - ResetCompShareInstancePassword

重置GPU实例的登录密码。

#### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| Region | string | 是 | 地域 |
| Zone | string | 是 | 可用区 |
| UHostId | string | 是 | 实例ID |
| Password | string | 是 | 新密码，需base64编码 |

#### 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| RetCode | int | 返回码 |
| Action | string | 操作名称 |
| UHostId | string | 实例ID |

#### 密码规范
- 长度: 8-30个字符
- 必须包含: 大写字母、小写字母、数字、特殊字符中的至少三种
- 特殊字符: `!@#$%^&*()_+-=`

#### 使用示例

```bash
python scripts/compshare_client.py reset-password \
  --instance-id uhost-xxxxx \
  --password "NewPassword123!"
```

---

### 7. 删除实例 - TerminateCompShareInstance

删除GPU实例。

**重要**: 删除前必须先停止实例！

#### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| Region | string | 是 | 地域 |
| Zone | string | 是 | 可用区 |
| UHostId | string | 是 | 实例ID |

#### 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| RetCode | int | 返回码 |
| Action | string | 操作名称 |
| UHostId | string | 实例ID |
| InRecycle | string | 是否进入回收站 |

#### 使用示例

```bash
# 1. 先停止实例
python scripts/compshare_client.py stop --instance-id uhost-xxxxx

# 2. 等待实例停止后删除
python scripts/compshare_client.py delete --instance-id uhost-xxxxx
```

---

## SSH客户端使用指南

SSH客户端用于连接GPU实例进行远程操作，支持命令执行、文件传输等功能。

### 连接信息获取

通过查询实例列表获取SSH连接信息：
```bash
python scripts/compshare_client.py list
# 返回结果中包含 SshLoginCommand 和 Password
```

### SSH命令列表

| 命令 | 功能 | 示例 |
|------|------|------|
| connect | 测试SSH连接 | `python ssh_client.py connect --ssh-command "..." --password "..."` |
| exec | 执行远程命令 | `python ssh_client.py exec --ssh-command "..." --password "..." --cmd "ls -la"` |
| ls | 列出目录内容 | `python ssh_client.py ls --ssh-command "..." --password "..." --path "/home"` |
| pwd | 显示当前目录 | `python ssh_client.py pwd --ssh-command "..." --password "..."` |
| cd | 切换目录 | `python ssh_client.py cd --ssh-command "..." --password "..." --path "/root"` |
| mkdir | 创建目录 | `python ssh_client.py mkdir --ssh-command "..." --password "..." --path "/home/new"` |
| rm | 删除文件 | `python ssh_client.py rm --ssh-command "..." --password "..." --path "/home/file.txt"` |
| rmdir | 删除空目录 | `python ssh_client.py rmdir --ssh-command "..." --password "..." --path "/home/empty"` |
| cat | 查看文件内容 | `python ssh_client.py cat --ssh-command "..." --password "..." --path "/etc/hosts"` |
| stat | 获取文件信息 | `python ssh_client.py stat --ssh-command "..." --password "..." --path "/home/file.txt"` |
| rename | 重命名文件/目录 | `python ssh_client.py rename --ssh-command "..." --password "..." --old "/home/a" --new "/home/b"` |
| chmod | 修改权限 | `python ssh_client.py chmod --ssh-command "..." --password "..." --path "/home/script.sh" --mode 755` |
| upload | 上传文件 | `python ssh_client.py upload --ssh-command "..." --password "..." --local ./file.txt --remote /home/file.txt` |
| upload-dir | 上传目录 | `python ssh_client.py upload-dir --ssh-command "..." --password "..." --local ./project --remote /home/project` |
| download | 下载文件 | `python ssh_client.py download --ssh-command "..." --password "..." --remote /home/file.txt --local ./file.txt` |
| download-dir | 下载目录 | `python ssh_client.py download-dir --ssh-command "..." --password "..." --remote /home/data --local ./data` |
| shell | 交互式Shell | `python ssh_client.py shell --ssh-command "..." --password "..."` |

### SSH使用示例

#### 1. 执行远程命令
```bash
python scripts/ssh_client.py exec \
  --ssh-command "ssh -p 12345 root@192.168.1.1" \
  --password "your-password" \
  --cmd "nvidia-smi"
```

#### 2. 上传代码到GPU实例
```bash
python scripts/ssh_client.py upload-dir \
  --ssh-command "ssh -p 12345 root@192.168.1.1" \
  --password "your-password" \
  --local ./my_project \
  --remote /root/my_project
```

#### 3. 下载训练结果
```bash
python scripts/ssh_client.py download-dir \
  --ssh-command "ssh -p 12345 root@192.168.1.1" \
  --password "your-password" \
  --remote /root/output \
  --local ./results
```

#### 4. 查看文件内容
```bash
python scripts/ssh_client.py cat \
  --ssh-command "ssh -p 12345 root@192.168.1.1" \
  --password "your-password" \
  --path /root/train.log
```

#### 5. 启动交互式Shell
```bash
python scripts/ssh_client.py shell \
  --ssh-command "ssh -p 12345 root@192.168.1.1" \
  --password "your-password"
```

---

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 160 | 参数错误 |
| 161 | 资源不存在 |
| 162 | 资源状态错误 |
| 163 | 配额不足 |
| 170 | 认证失败 |
| 171 | 权限不足 |
| 172 | 账户余额不足 |

---

## 最佳实践

### 1. 实例生命周期管理
```
创建 -> 启动 -> 运行中 -> 停止 -> 删除
         ↑____________↓
              重启
```

### 2. 删除实例流程
1. 先调用 StopCompShareInstance 停止实例
2. 等待实例状态变为 Stopped
3. 调用 TerminateCompShareInstance 删除实例

### 3. 密码管理
- 创建实例时设置初始密码
- 使用 ResetCompShareInstancePassword 重置密码
- 密码需要 base64 编码后传输

### 4. 计费模式选择
| 模式 | 说明 | 适用场景 |
|------|------|----------|
| Dynamic | 按小时预付费 | 短期测试、临时任务 |
| Postpay | 按小时后付费 | 支持关机不收费 |
| Day | 按天付费 | 中期使用 |
| Month | 按月付费 | 长期稳定使用 |

### 5. 实例状态说明
| 状态 | 说明 | 可执行操作 |
|------|------|------------|
| Pending | 创建中 | 等待 |
| Running | 运行中 | 停止、重启、重置密码、SSH连接 |
| Stopped | 已停止 | 启动（正常/无卡）、删除 |

### 6. 无卡开机使用场景
- 只需要CPU计算资源时
- 需要修改代码或配置文件时
- 需要下载或整理数据时
- 暂时不需要GPU但需要保持环境时

### 7. 典型工作流程
```bash
# 1. 创建GPU实例
python scripts/compshare_client.py create --gpu-type 4090 --gpu-count 1 --cpu 16 --memory 64

# 2. 查询实例获取SSH信息
python scripts/compshare_client.py list

# 3. 上传代码
python scripts/ssh_client.py upload-dir \
  --ssh-command "ssh -p xxxxx root@x.x.x.x" \
  --password "xxx" \
  --local ./project \
  --remote /root/project

# 4. 执行训练
python scripts/ssh_client.py exec \
  --ssh-command "ssh -p xxxxx root@x.x.x.x" \
  --password "xxx" \
  --cmd "cd /root/project && python train.py"

# 5. 下载结果
python scripts/ssh_client.py download-dir \
  --ssh-command "ssh -p xxxxx root@x.x.x.x" \
  --password "xxx" \
  --remote /root/output \
  --local ./results

# 6. 停止实例
python scripts/compshare_client.py stop --instance-id uhost-xxxxx

# 7. 删除实例
python scripts/compshare_client.py delete --instance-id uhost-xxxxx
```

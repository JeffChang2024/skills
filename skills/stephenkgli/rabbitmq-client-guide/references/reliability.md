# RabbitMQ 消息可靠性保障

基于腾讯云 TDMQ RabbitMQ 托管版官方文档，详细说明消息可靠性的四层保障机制。

> 来源: https://www.tencentcloud.com/zh/document/product/1112/64345

## Table of Contents

- [1. 持久化（Persistence）](#1-持久化persistence)
- [2. 发送端 Confirm 机制](#2-发送端-confirm-机制)
- [3. 消费端 ACK 机制](#3-消费端-ack-机制)
- [4. 镜像队列（Mirrored Queues）](#4-镜像队列mirrored-queues)

---

## 1. 持久化（Persistence）

### 持久化三件套

消息不丢失的基础保障，三者缺一不可：

| 组件 | 配置 | 说明 |
|------|------|------|
| Exchange | `durable=true` | 交换机在 Broker 重启后不丢失 |
| Queue | `durable=true` | 队列元数据在 Broker 重启后不丢失 |
| Message | `deliveryMode=2` | 消息持久化到磁盘 |

### 工作机制

队列接收到消息后立即将其持久化到磁盘，确保队列元数据和消息在 Broker 重启后不丢失。

### 性能考虑

非持久化消息会占用更多内存（驻留在内存中直到被消费），可能导致服务端内存负载过高。因此即使从性能角度考虑，也建议使用持久化。

---

## 2. 发送端 Confirm 机制

### 作用

确保消息被成功发送到 Broker。开启 confirm 模式后，Broker 在接收到消息并完成持久化后向生产者发送确认（ack）。

### mandatory 参数

mandatory 参数控制消息无法路由时的行为：

| 配置 | 消息可路由时 | 消息不可路由时 |
|------|-----------|-------------|
| `mandatory=false`（默认） | Broker 回 confirm | Broker 回 confirm（消息被静默丢弃） |
| `mandatory=true` | Broker 回 confirm | Broker 通过 `basic.return` 将消息退回客户端 |

### 使用要点

1. **开启 confirm 模式** — 在 channel 上调用 `confirmSelect()`
2. **设置 mandatory=true** — 确保消息路由失败时能感知
3. **处理 basic.return** — 注册 return listener 处理退回的消息
4. **注意**: 延迟交换机（delayed exchange）不支持 mandatory

### 编码模式

```
// 伪代码
channel.confirmSelect()
channel.addReturnListener(msg -> handleUnroutableMessage(msg))
channel.basicPublish(exchange, routingKey, mandatory=true, props, body)
channel.waitForConfirms()  // 或使用异步 confirm callback
```

---

## 3. 消费端 ACK 机制

### 保证级别

提供 **at least once** 级别的消费语义保证 — 确保消息至少被成功处理一次。

### 工作机制

1. Broker 将消息推送给消费者
2. 消费者处理消息
3. 处理成功后发送 ACK
4. Broker 收到 ACK 后删除消息

### 注意事项

- **禁止 autoAck** — 自动确认会导致消息在处理异常时不重试
- **做好幂等** — at least once 意味着可能重复投递，消费端必须处理重复
- **及时 ACK** — 未被 ACK 的消息会堆积在 Broker 内存中，增加客户端和服务端内存压力
- **处理失败时 NACK/reject** — 将消息退回队列或进入死信队列，而非无限挂起

---

## 4. 镜像队列（Mirrored Queues）

### 作用

将队列数据复制到集群内其他 Broker，确保单个 Broker 故障时队列仍可用，尽量不丢失消息。

### 成本

- 增加 Broker 启动时长（需同步数据）
- 增加网络和磁盘资源占用

### 关键警告: ha-sync-mode

**禁止设置 `ha-sync-mode=automatic`**。

原因：
- Broker 重启后会自动全量同步队列数据，无论数据是否已同步过
- 同步数据量大时导致 Broker 同步时间过长、持续占用内存
- 同步完成前队列处于不可用状态
- 严重影响业务可用性和服务端稳定性

**推荐**: 使用 `ha-sync-mode=manual`，在业务低峰期手动触发同步。

### 仲裁队列替代

RabbitMQ 3.13 推荐优先使用仲裁队列（Quorum Queues）替代镜像队列。仲裁队列基于 Raft 协议，提供更好的数据一致性和更简洁的运维模型。

---

## 可靠性全链路总结

```
Producer                    Broker                    Consumer
   │                          │                          │
   │── publish(mandatory) ──> │                          │
   │                          │── persist to disk        │
   │<── confirm(ack) ──────── │                          │
   │                          │                          │
   │  (如果路由失败)            │                          │
   │<── basic.return ──────── │                          │
   │                          │                          │
   │                          │── push(prefetch) ──────> │
   │                          │                          │── process
   │                          │                          │── 幂等检查
   │                          │<── ack ───────────────── │
   │                          │── delete message         │
```

四层保障缺一不可：
1. **持久化** — 防 Broker 重启丢消息
2. **Confirm** — 防发送端到 Broker 链路丢消息
3. **ACK** — 防 Broker 到消费端链路丢消息
4. **镜像/仲裁队列** — 防单 Broker 宕机丢消息

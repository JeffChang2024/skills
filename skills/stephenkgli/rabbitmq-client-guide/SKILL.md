---
name: rabbitmq-client-guide
description: RabbitMQ 客户端代码指南。当用户需要编写、调试或审查 RabbitMQ 应用代码时使用。涵盖：用任意语言（Java/Go/Python/PHP/.NET）写生产者或消费者；排查连接暴增、消息丢失、Broken pipe、消费慢、漏消费等客户端问题；审查 spring-boot-starter-amqp、amqp091-go、pika、php-amqplib 等库的代码；实现 RPC 模式、confirm、手动 ack、prefetch 调优、连接复用、重连机制。用户贴了 RabbitMQ 相关代码片段或描述了客户端侧的消息异常时，始终触发此技能。不适用于 RabbitMQ 服务端运维部署、Kafka 等其他消息系统、或纯架构设计问题。
---

# RabbitMQ 客户端代码编写指南

## Overview

基于腾讯云 TDMQ RabbitMQ 托管版官方最佳实践，指导生成和审查 RabbitMQ 客户端代码。覆盖连接管理、生产者、消费者、消息可靠性四大核心场景，支持 Java、Go、Python、.NET、PHP 以及 Spring Boot、Spring Cloud Stream 等框架。

## Quick Start: Decision Tree

生成代码前，快速明确需求：

```
您需要什么？
├─ 写生产者代码（发送消息）
│  └─ 项目语言？Java / Go / Python / .NET / PHP / Spring Boot...
│  └─ 需要特殊场景？（可靠投递、批量、延迟...）
├─ 写消费者代码（接收消息）
│  └─ 项目语言？
│  └─ 并发还是串行？单线程 / 多线程 / 异步...
├─ 审查现有代码
│  └─ 直接用检查清单对照
└─ 排查问题
   └─ 症状？消息丢失 / 连接失败 / 消费落后...
```

## Workflow

### 生成新代码

按以下步骤执行：

1. **识别场景与语言** — 确定用户需要生产者/消费者/两者，确认编程语言和框架
2. **萃取关键信息** — 消息格式、吞吐量、延迟要求、并发模型、是否已有连接工厂
3. **生成连接管理代码** — 连接工厂、连接池、通道管理、重连逻辑
4. **生成业务代码** — 生产者或消费者的核心逻辑，展示 exchange/queue 声明
5. **嵌入可靠性** — confirm、ack、幂等、prefetch、错误处理
6. **验证与解释** — 逐项过检查清单，解释每项为什么重要

### 审查已有代码

1. 快速扫描识别问题类型（连接管理 / 可靠性 / 性能）
2. 用检查清单逐项审查
3. 针对每个失败项说明风险和修复方案

### 排查问题

1. **诊断症状** — 消息丢失、连接断裂、消费者不读取、超时等
2. **确认根因** — 指向具体的代码检查点（见 references/reliability.md）
3. **给出修复建议** — 结合具体的客户端库 API

## 语言与客户端库

### 原生客户端

| 语言 | 推荐客户端库 | 自动重连 | 重连关键点 |
|------|------------|:--------:|------|
| Java | amqp-client | 内置 | `factory.setAutomaticRecoveryEnabled(true)` |
| .NET | RabbitMQ.Client | 内置 | `factory.AutomaticRecoveryEnabled = true` |
| Go | amqp091-go | 需手动 | 监听 `conn.NotifyClose()`，在独立 goroutine 中重建连接和通道 |
| Python | pika | 需手动 | 捕获 `ConnectionClosedByBroker`，重建 `BlockingConnection` |
| PHP | php-amqplib | 需手动 | 捕获 `AMQPConnectionClosedException`，重建 `AMQPStreamConnection` |

### 框架集成

| 框架 | 连接方式 | 注意事项 |
|------|---------|----------|
| Spring Boot AMQP | `@RabbitListener` + `RabbitTemplate` | 自动管理连接池和重连；用 `@Bean` 声明 Exchange/Queue/Binding |
| Spring Cloud Stream | `@StreamListener` + `MessageChannel` | 更高层抽象；通过 `application.yml` 配置 binder |

## Code Generation Rules

以下规则是生成高质量客户端代码的核心准则。每条规则都有具体原因，理解原因比死记规则更重要——这样遇到边界场景时能做出正确判断。

### 连接管理

1. **连接复用** — 每个进程一个连接，每个线程/goroutine 一个通道。原因：创建连接需要 TCP 握手（7 个包）+ AMQP 握手，每个连接占 ~100KB 内存，频繁创建/销毁是最常见的性能杀手。
2. **生产消费隔离** — 生产者和消费者使用独立的连接。原因：RabbitMQ 的流控机制作用于连接级别——如果消费流量大触发流控，会拖慢同一连接上的生产者。
3. **通道线程安全** — 禁止多线程共享同一个通道。原因：主流客户端库的 channel 实现都不是线程安全的，共享会导致帧交错、消息丢失。
4. **心跳保持** — 禁止设置 heartbeat=0。原因：关闭心跳后 broker 无法检测死连接，导致连接泄露；服务端默认 60s，通常不需要调整。

### 生产者

5. **持久化三件套** — exchange `durable=true` + queue `durable=true` + message `deliveryMode=2`。三者缺一不可：exchange/queue 不持久化则 broker 重启后资源丢失；message 不持久化则 broker 重启后消息丢失。即使不关心持久性，非持久化消息驻留内存更多，反而有性能隐患。
6. **Confirm 机制** — 开启 publisher confirm（`channel.confirmSelect()`），等待 broker ack 后再视为发送成功。这是防止 producer→broker 链路丢消息的唯一保障。
7. **mandatory 路由保护** — 设置 `mandatory=true` 并注册 return listener。原因：默认情况下消息无法路由（比如 exchange 存在但没有匹配的 binding）时 broker 会静默丢弃——mandatory 使 broker 通过 `basic.return` 退回消息。注意：delayed exchange 不支持 mandatory。
8. **消息合并** — 高频小消息场景考虑合并为批量消息。原因：RabbitMQ 对每秒处理的消息数量比单条消息大小更敏感。

### 消费者

9. **手动 ACK** — 禁止 `autoAck=true`。原因：自动确认在消息到达消费者时立即 ack，如果处理失败消息不会重试，等于丢消息。
10. **幂等处理** — 消息体中携带唯一业务 ID（订单号、事务 ID 等），消费端据此去重。原因：RabbitMQ 提供 at-least-once 语义，网络分区恢复、消费者重连等场景会产生重复投递。
11. **CONSUME 模式** — 使用 `basic.consume`（push），禁止 `basic.get`（pull）。原因：pull 模式每条消息一次请求，效率极低；持续空拉还会导致 broker CPU 飙升。
12. **prefetch 合理配置** — 根据消费能力设置 prefetch count（见下方速查表）。过低则消费者闲等，过高则负载不均。

### 容错

13. **自动重连** — Java/.NET 开启内置自动恢复；Go/Python/PHP 在应用层实现。Broker 会因 OOM、母机故障、升配等场景重启，客户端必须能自动恢复。
14. **网络分区应对** — 腾讯云采用 autoseal 模式（自动决出获胜分区，重启非信任分区 broker）。生产者通过 `basic.return` 感知路由失败；消费者通过幂等处理应对恢复期的重复投递。

## Prefetch Quick Reference

| 场景 | 推荐 prefetch |
|------|:------------:|
| 消费速度快、处理时间短 | 250 |
| 处理时间稳定、网络可控 | RTT / 平均处理时间 |
| 消费者多、处理时间短 | 较低值 |
| 消费者多或处理时间长 | 1 |

禁止设置无限制 prefetch（0），会导致单个消费者接收全部消息。

## Checklist

生成或审查代码后逐项检查。每项标注了违反时的风险等级，帮助排定修复优先级：

### 连接管理（违反 → 性能/稳定性问题）

- [ ] **连接复用** — 没有在循环或请求处理中创建新连接 `[HIGH: 连接风暴]`
- [ ] **生产消费隔离** — 生产者和消费者使用不同的 connection `[MEDIUM: 流控串扰]`
- [ ] **通道不跨线程** — 每个线程/goroutine 有独立的 channel `[HIGH: 帧交错/消息丢失]`
- [ ] **心跳未关闭** — 没有设置 heartbeat=0 `[MEDIUM: 连接泄露]`

### 生产者（违反 → 消息丢失风险）

- [ ] **Exchange durable** — exchange 声明为持久化 `[HIGH: broker 重启后 exchange 丢失]`
- [ ] **Queue durable** — queue 声明为持久化 `[HIGH: broker 重启后 queue 丢失]`
- [ ] **Message persistent** — 消息设置 deliveryMode=2 `[HIGH: broker 重启后消息丢失]`
- [ ] **Publisher confirm** — 开启了 confirm 机制 `[HIGH: 无法感知投递失败]`
- [ ] **mandatory** — 设置 mandatory=true 并处理 return `[MEDIUM: 路由失败静默丢消息]`

### 消费者（违反 → 消息处理不可靠）

- [ ] **手动 ACK** — autoAck=false `[CRITICAL: 处理失败不重试，等于丢消息]`
- [ ] **幂等标识** — 消息中包含唯一业务 ID `[MEDIUM: 重复消费导致业务异常]`
- [ ] **Push 模式** — 使用 basic.consume 而非 basic.get `[MEDIUM: 性能差 + broker CPU 飙升]`
- [ ] **Prefetch 已设置** — 配置了合理的 prefetch count `[MEDIUM: 负载不均]`

### 容错（违反 → 服务中断）

- [ ] **重连机制** — 有自动重连逻辑（内置或手动实现）`[HIGH: broker 重启后服务中断]`

## Troubleshooting Quick Guide

常见问题的排查入口：

| 症状 | 可能原因 | 检查点 |
|------|---------|--------|
| 消息丢失 | 未开 confirm / 未持久化 / autoAck | 检查规则 5-7, 9 |
| 连接频繁断开 | 心跳被关闭 / 未实现重连 | 检查规则 4, 13 |
| 消费者不消费 | prefetch=0 / 用了 basic.get | 检查规则 11, 12 |
| 消息重复消费 | 未做幂等 / 网络分区恢复 | 检查规则 10, 14 |
| 发送性能差 | 每次创建新连接 / 未批量 | 检查规则 1, 8 |
| 流控导致发送慢 | 生产消费共用连接 | 检查规则 2 |
| broker 重启后服务中断 | 未开自动恢复 | 检查规则 13 |

深入排查时参考 references/reliability.md 的全链路图。

## References

详细规则和背景知识按需加载：

- **[best-practices.md](references/best-practices.md)** — 连接管理、生产消费优化、队列配置、客户端机制的详细说明。**何时读取**：需要了解 prefetch 配置细节、队列积压处理策略、仲裁队列 vs 镜像队列选型、队列自动删除策略等深入内容时。
- **[reliability.md](references/reliability.md)** — 消息可靠性保障的四层机制：持久化 → confirm → ack → 镜像/仲裁队列。**何时读取**：需要理解 confirm 工作流程、mandatory 行为矩阵、镜像队列 ha-sync-mode 配置（禁止 automatic）、全链路可靠性架构时。

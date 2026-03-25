# Changelog

All notable changes to this project will be documented in this file.

## [3.2.0] - 2026-03-25

### 🎉 Added
- **新增 url-auto-fetch Hook**，实现真正的自动触发功能
- 监听 `message:received` 事件，自动检测用户发送的 URL 链接
- 支持两种触发方式：
  - 纯 URL 消息（消息中只有 URL）
  - URL + 意图关键词（解析、转换、markdown 等）
- 异步执行抓取脚本，不阻塞消息处理
- 自动发送抓取进度提示消息

### 🔧 Changed
- 更新 SKILL.md，添加 Hook 启用说明和安装指南
- 更新 _meta.json，添加 hooks 配置
- 优化触发逻辑，优先处理微信公众号链接
- 使用 ESM 模块语法编写 Hook handler

### 📚 Documentation
- 新增 HOOK_AUTO_TRIGGER_README.md - Hook 自动触发方案详细说明
- 新增 PUBLISH_GUIDE.md - 发布指南
- 新增 优化方案总结.md - 技术总结文档
- 在 SKILL.md 中添加完整的 Hook 启用步骤

### 🐛 Fixed
- 修复 AI 无法自动调用技能的问题
- 修复 URL 检测逻辑，支持更多场景
- 修复脚本路径查找逻辑，使用固定路径提高可靠性

### 📦 Technical
- Hook handler 使用 TypeScript ESM 模块
- 支持从 `~/.openclaw/hooks/` 目录加载
- 通过 `openclaw hooks enable` 命令启用

---

## [3.1.0] - 2026-03-24

### Added
- 支持异步批量处理（5 倍速）
- 支持分页自动拼接
- 支持 LaTeX 公式保留
- 支持编码自动识别（chardet）

### Changed
- 配置集中管理
- 模块化代码结构
- 包含完整单元测试

---

## [3.0.0] - 2026-03-22

### Added
- 支持多网站自动识别（微信、知乎、掘金、CSDN、GitHub、Medium 等）
- 三种降级方案（Playwright → Third_Party_API → Scrapling）
- robots.txt 合规检查
- 自动重试机制（2 次）
- 广告自动清洗
- 图片自动下载

### Changed
- 完全重构代码架构
- 优化目录结构

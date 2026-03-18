# ai-caption-zh

[![ClawHub Skill](https://img.shields.io/badge/ClawHub-Skill-blueviolet)](https://clawhub.io)
[![Version](https://img.shields.io/badge/version-1.0.8-blue)](SKILL.md)

> **AI 字幕**
> 中文场景版，由 Sparki 提供能力。
>
> Powered by [Sparki](https://sparki.io).

## 这个 Skill 做什么

这个 skill 是 Sparki AI 视频工作流的中文场景入口。

- 上传视频文件
- 根据场景创建 AI 处理任务
- 轮询直到处理完成
- 返回结果下载链接

## 适合这些需求
- “帮我加字幕”
- “给这个视频自动上字”
- “让视频静音也能看懂”
- “做成带字幕的短视频”

## 快速开始

```bash
export SPARKI_API_KEY="sk_live_your_key_here"
export SPARKI_API_BASE="https://business-agent-api.sparki.io/api/v1"
RESULT_URL=$(bash scripts/edit_video.sh my_video.mp4 "24" "加干净易读的字幕，并让节奏更紧凑" "9:16")
echo "$RESULT_URL"
```

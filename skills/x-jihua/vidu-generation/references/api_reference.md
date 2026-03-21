# Vidu Lite API Reference

精简版 API 参考，仅包含视频和图片生成功能。

## Base URL

```
https://api.vidu.cn/ent/v2
```

**域名选择规则**：
- **简体中文用户**：使用 `api.vidu.cn`
- **非简体中文用户**：使用 `api.vidu.com`

根据用户交流语言自动切换域名。

## Authentication

```
Authorization: Token YOUR_API_KEY
```

---

## 视频生成 API

### 1. 文生视频 (text2video)

**POST** `/text2video`

```json
{
  "model": "viduq3-pro",
  "prompt": "视频描述",
  "duration": 5,
  "aspect_ratio": "16:9",
  "resolution": "720p",
  "audio": true
}
```

**模型选择**：
| 模型 | 特点 | 音频 | 智能切镜 |
|------|------|------|----------|
| viduq3-pro | 最新，质量最高 | ✅ | ✅ |
| viduq3 | 多参考图场景 | ✅ | ✅ |
| viduq3-turbo | 速度快 | ✅ | ✅ |
| viduq2 | 细节丰富 | ❌ | ✅ |

---

### 2. 图生视频 (img2video)

**POST** `/img2video`

```json
{
  "model": "viduq3-pro",
  "images": ["图片URL或base64"],
  "prompt": "视频描述",
  "duration": 5,
  "resolution": "720p",
  "audio": true
}
```

**用途**：单张图片生成视频，图片作为首帧。

---

### 3. 参考生视频 (reference2video)

**POST** `/reference2video`

```json
{
  "model": "viduq3",
  "images": ["图片1", "图片2", "..."],
  "prompt": "视频描述",
  "duration": 5,
  "audio": true
}
```

**用途**：多张参考图生成视频（多人、多主体场景）。

**限制**：最多 7 张参考图。

---

### 4. 首尾帧视频 (start-end2video)

**POST** `/start-end2video`

```json
{
  "model": "viduq3-pro",
  "images": ["首帧图片", "尾帧图片"],
  "prompt": "视频描述",
  "duration": 5
}
```

**用途**：提供首尾帧，生成过渡动画。

---

### 5. 场景特效模板 (template)

**POST** `/template`

```json
{
  "template": "hugging",
  "images": ["图片"],
  "prompt": "画面描述",
  "bgm": true
}
```

**热门模板**：
- `hugging` - 拥抱特效
- `exotic_princess` - 异域公主
- `beast_companion` - 与兽同行

---

## 图片生成 API

### 1. Nano 生图（推荐）

**POST** `/reference2image/nano`

```json
{
  "model": "q3-fast",
  "prompt": "图片描述",
  "images": ["参考图1", "..."],
  "aspect_ratio": "16:9",
  "resolution": "2K"
}
```

**模型选择**：
| 模型 | 分辨率 | 速度 | 质量 | 参考图要求 |
|------|--------|------|------|-----------|
| q3-fast | 1K/2K/4K | 快 | 高 | 0-14张（可选） |
| q2-fast | 1K | 最快 | 中 | 0-14张（可选） |
| q2-pro | 1K/2K/4K | 慢 | 最高 | 0-14张（可选） |

**特殊比例支持（仅 q3-fast）**：
- `1:4` - 超宽横图
- `4:1` - 超长竖图
- `1:8` - 极宽横图
- `8:1` - 极长竖图

**标准比例（所有模型）**：
`9:16, 2:3, 3:4, 4:5, 1:1, 5:4, 4:3, 3:2, 16:9, 21:9`

**特点**：
- ✅ 支持文生图（不输入参考图）
- ✅ 支持参考生图（输入参考图）
- ✅ 最多 14 张参考图

---

### 2. Vidu 参考生图

**POST** `/reference2image`

```json
{
  "model": "viduq2",
  "prompt": "图片描述",
  "images": ["参考图"],
  "aspect_ratio": "16:9",
  "resolution": "1080p"
}
```

**模型选择**：
| 模型 | 分辨率 | 参考图要求 | 说明 |
|------|--------|-----------|------|
| viduq2 | 540p/720p/1080p | 0-7张 | 支持文生图、参考生图、图片编辑 |
| viduq1 | 1080p | 1-7张（必填） | 仅支持参考生图 |

**比例支持**：
`9:16, 2:3, 3:4, 4:5, 1:1, 5:4, 4:3, 3:2, 16:9, 21:9`

**viduq2 图片编辑功能**：
- 支持图片编辑（局部重绘、扩图等）
- 使用图片编辑时，`aspect_ratio` 必须设为 `auto`
- 示例：
```json
{
  "model": "viduq2",
  "prompt": "编辑描述",
  "images": ["待编辑图片"],
  "aspect_ratio": "auto",
  "resolution": "1080p"
}
```

**特点**：
- viduq2：支持文生图、参考生图、图片编辑
- viduq1：必须输入至少 1 张参考图（仅参考生图）
- 最多 7 张参考图

---

## 任务管理 API

### 查询任务状态

**GET** `/tasks`

返回任务列表，根据 `task_id` 查找。

### 取消任务

**DELETE** `/tasks/{task_id}`

---

## 响应格式

### 任务创建响应

```json
{
  "task_id": "xxx",
  "state": "pending",
  "model": "viduq3-pro",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 任务完成响应

```json
{
  "task_id": "xxx",
  "state": "success",
  "creations": [
    {
      "url": "https://...",
      "cover_url": "https://..."
    }
  ]
}
```

---

## 错误码

| 错误 | 说明 |
|------|------|
| Invalid API key | API 密钥错误 |
| Image size exceeds | 图片超过 50MB |
| Invalid aspect ratio | 不支持的比例 |
| Task failed | 生成失败 |

---

---

## 音频生成 API

### 1. TTS 语音合成

**POST** `/audio-tts`

```json
{
  "text": "要配音的文本",
  "voice_setting_voice_id": "female-shaonv",
  "voice_setting_speed": 1.0,
  "voice_setting_volume": 0,
  "voice_setting_pitch": 0,
  "voice_setting_emotion": "calm"
}
```

**参数说明**：
| 参数 | 类型 | 范围 | 说明 |
|------|------|------|------|
| text | string | - | 要合成的文本 |
| voice_setting_voice_id | string | - | 音色ID，见 voice_id_list.md |
| voice_setting_speed | float | 0.5-2.0 | 语速，默认1.0 |
| voice_setting_volume | int | 0-10 | 音量，默认0 |
| voice_setting_pitch | int | -12~12 | 语调，默认0 |
| voice_setting_emotion | string | - | 情绪：happy/sad/angry/fearful/disgusted/surprised/calm |

**返回**：同步返回音频URL

---

### 2. 声音复刻

**POST** `/audio-clone`

```json
{
  "audio_url": "源音频URL",
  "voice_id": "自定义音色ID",
  "text": "试听文本",
  "prompt_audio_url": "参考音频URL（可选）",
  "prompt_text": "参考音频对应文本（可选）"
}
```

**要求**：
- 源音频时长：10秒-5分钟
- 音频清晰，无背景噪音
- 复刻音色7天内需使用才能保留

---

## 参数速查

### 视频参数

| 参数 | 可选值 | 默认值 |
|------|--------|--------|
| duration | 1-16秒 | 5 |
| aspect_ratio | 16:9, 9:16, 4:3, 3:4, 1:1 | 16:9 |
| resolution | 540p, 720p, 1080p | 720p |
| audio | true/false | false |

### 图片参数

| 参数 | 可选值 | 默认值 |
|------|--------|--------|
| aspect_ratio | 9:16, 2:3, 3:4, 4:5, 1:1, 5:4, 4:3, 3:2, 16:9, 21:9 | 16:9 |
| resolution | 1K, 2K, 4K | 2K |

### TTS参数

| 参数 | 可选值 | 默认值 |
|------|--------|--------|
| speed | 0.5-2.0 | 1.0 |
| volume | 0-10 | 0 |
| pitch | -12~12 | 0 |
| emotion | happy/sad/angry/fearful/disgusted/surprised/calm | calm |

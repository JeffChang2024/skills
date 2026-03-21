# Vidu Template Generate API Reference

场景特效 API 参考，包含389个预设特效模板。

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

## 场景特效 API

### 场景特效模板

**POST** `/template`

```json
{
  "template": "hugging",
  "images": ["用户照片"],
  "prompt": "画面描述",
  "bgm": true,
  "seed": 0
}
```

**参数说明**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| template | string | ✅ | 模板ID（见模板列表） |
| images | array | ✅ | 用户照片（URL或base64） |
| prompt | string | ❌ | 额外描述（可选） |
| bgm | boolean | ❌ | 是否添加背景音乐（默认false） |
| seed | integer | ❌ | 随机种子（默认0） |

**热门模板**：
- `muscling` - 变身肌肉男
- `exotic_princess` - 异域公主
- `beast_companion` - 与兽同行
- `pick_mini_self` - 拾取微缩分身
- `french_kiss` - 法式热吻

---

## 特殊参数

### 异域公主 `exotic_princess`

支持 `area` 参数指定公主类型：

```json
{
  "template": "exotic_princess",
  "aspect_ratio": "9:16",
  "area": "china",
  "images": ["用户照片"],
  "prompt": "视频描述"
}
```

**可选值**：
- `auto` - 随机生成（默认）
- `denmark` - 丹麦公主
- `uk` - 英国公主
- `africa` - 非洲公主
- `china` - 中国公主
- `mexico` - 墨西哥公主
- `switzerland` - 瑞士公主
- `russia` - 俄罗斯公主
- `ital` - 意大利公主
- `korea` - 韩国公主
- `thailand` - 泰国公主
- `india` - 印度公主
- `japan` - 日本公主

### 与兽为伍 `beast_companion`

支持 `beast` 参数指定兽人类型：

```json
{
  "template": "beast_companion",
  "aspect_ratio": "9:16",
  "beast": "wolf",
  "images": ["用户照片"],
  "prompt": "视频描述"
}
```

**可选值**：
- `auto` - 随机生成（默认）
- `bear` - 熊首男友
- `tiger` - 虎首男友
- `elk` - 鹿首男友
- `snake` - 蛇首男友
- `lion` - 狮首男友
- `wolf` - 狼首男友

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
  "template": "muscling",
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
| Template not found | 模板不存在 |
| Task failed | 生成失败 |

---

## 使用注意事项

### 图片要求

1. **必须使用用户上传的照片**
2. 人物为正面、半身/全身照时效果更好
3. 图片格式：JPG/PNG
4. 图片大小：不超过 50MB

### 模板分类

- **华丽变身** (14个) - 变身肌肉男、美队、浩克等
- **情人节** (10个) - 热吻、婚礼、求婚等
- **缤纷佳节** (8个) - 樱花、圣诞、童年等
- **趣味工坊** (6个) - 切切、气球、飞行等
- **360p特效** (10个) - 膨胀、爆炸、融化等

**完整模板列表**: 见 `template_list.md` (389个特效)

---

## 参数速查

### 特效参数

| 参数 | 可选值 | 默认值 |
|------|--------|--------|
| bgm | true/false | false |
| seed | 任意整数 | 0 |

### 视频输出

- **分辨率**: 720p（部分为360p）
- **时长**: 4秒（部分为5秒或8秒）

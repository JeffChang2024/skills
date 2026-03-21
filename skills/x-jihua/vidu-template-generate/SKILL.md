---
name: vidu-template-generate
version: 1.0.0
description: "Vidu AI 场景特效生成。支持389个预设特效模板，包括华丽变身、情人节、风格魔盒、缤纷佳节等。对话式调用，自动匹配模板。"
---

# Vidu Template Generate ✨

Vidu AI 场景特效生成工具，专注于特效模板功能。

## 环境说明

**变量说明**：
- `{baseDir}` - 运行时自动替换为本 skill 目录的绝对路径
  - 实际路径：`~/.openclaw/workspace/skills/vidu-template-generate/`

**环境变量**：
- `VIDU_API_KEY` - Vidu API 密钥（必需）

## 快速开始

直接告诉我你想要什么特效，我会自动匹配模板：

```
"帮我生成一个拥抱特效"
"变身肌肉男"
"异域公主特效"
"拾取微缩分身"
```

## 重要规则

⚠️ **严格使用用户的照片**

- ✅ **必须使用用户上传的照片**
- ✅ **如果用户没有提交照片，必须提醒用户上传**
- ❌ **禁止使用默认图片或测试图片**

## 特效模板分类

### 🎭 华丽变身 (14个)

| 特效名称 | 模板ID | 效果说明 |
|---------|--------|---------|
| 变身肌肉男 | `muscling` | 主角变身肌肉男，脱衣秀肌肉 |
| 变身美队 | `captain_america` | 变身美国队长，展开翅膀拿盾牌 |
| 变身浩克 | `hulk` | 破碎重塑狂暴红巨人 |
| 美队同行 | `cap_walk` | 与美队并肩赴战场 |
| 浩克俯冲 | `hulk_dive` | 主体乘浩克俯冲震地 |
| 异域公主 | `exotic_princess` | 变身异域公主盛装优雅出镜 |
| 与兽为伍 | `beast_companion` | 与兽人并肩自信前行 |
| 变身Q版玩偶 | `cartoon_doll` | 角色变身Q版玩偶 |
| 流金岁月 | `golden_epoch` | 进入鎏金岁月怀旧氛围 |
| 金像盛典 | `oscar_gala` | 持小金人发表获奖感言 |
| 时尚T台 | `fashion_stride` | T台自信走秀显气场 |
| 星光红毯 | `star_carpet` | 自信走上星光红毯 |
| 烈焰红毯 | `flame_carpet` | 优雅走上烈焰红毯 |
| 风雪红毯 | `frost_carpet` | 自信走上雪中红毯 |

### 💕 情人节 (10个)

| 特效名称 | 模板ID | 效果说明 |
|---------|--------|---------|
| 法式热吻 | `french_kiss` | 两人交织热吻深沉热烈 |
| 梦幻婚礼 | `dreamy_wedding` | 进入新人梦幻婚礼 |
| 浪漫公主抱 | `romantic_lift` | 浪漫公主抱 |
| 温馨求婚 | `sweet_proposal` | 单膝跪地求婚惊喜 |
| AI情侣送花 | `couple_arrival` | 伴侣送花温馨互动 |
| 丘比特之箭 | `cupid_arrow` | 丘比特箭射出心动浪漫氛围 |
| 萌宠恋人 | `pet_lovers` | 萌宠情侣亲密互动 |
| AI情侣拥抱 | `couple_arrival` | 伴侣温暖拥抱 |
| AI情侣亲吻 | `couple_arrival` | 情侣接吻展现温馨氛围 |
| AI情侣挥手 | `couple_arrival` | 情侣亲密挥手友好 |

### 🎉 缤纷佳节 (8个)

| 特效名称 | 模板ID | 效果说明 |
|---------|--------|---------|
| 樱花飘落 | `sakura_season` | 樱花飘落，抬头微笑 |
| 童年回忆 | `youth_rewind` | 童年春节怀旧欢乐场景 |
| 古风换装 | `dynasty_dress` | 换上古风服装 |
| 变身为圣诞老人 | `christmas` | 变身圣诞老人 |
| 圣诞老人来送礼 | `christmas` | 圣诞老人来送礼 |
| 圣诞节举杯庆祝 | `christmas` | 举香槟庆祝圣诞 |
| 圣诞老人来拥抱 | `christmas` | 圣诞老人来拥抱 |
| 全家福比心 | `love_pose` | 全家福比心 |

### 🎪 趣味工坊 (6个)

| 特效名称 | 模板ID | 效果说明 |
|---------|--------|---------|
| 解压切切 | `slice_therapy` | 解压切一切 |
| 变成气球飞走了 | `balloon_flyaway` | 变身气球旋转飞走 |
| 飞行 | `flying` | 变身超级英雄漂浮飞行 |
| 纸片人特效 | `paperman` | 主体变纸片人被大手移出 |
| 捏捏 | `pinch` | 大手捏扁主体 |
| 甜美微笑 | `live_photo` | 面对镜头露出甜美微笑 |

**完整模板列表**: 见 `references/template_list.md` (389个特效)

## 特殊参数说明

### 异域公主 `exotic_princess`

支持 `area` 参数指定公主类型：
- `auto` - 随机生成
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
- `auto` - 随机生成
- `bear` - 熊首男友
- `tiger` - 虎首男友
- `elk` - 鹿首男友
- `snake` - 蛇首男友
- `lion` - 狮首男友
- `wolf` - 狼首男友

## API 调用

内部使用 Python CLI 工具：

```bash
# 场景特效
python3 {baseDir}/scripts/vidu_cli.py template \
  --template muscling \
  --image user_photo.jpg \
  --prompt "视频描述"

# 异域公主（指定中国公主）
python3 {baseDir}/scripts/vidu_cli.py template \
  --template exotic_princess \
  --image user_photo.jpg \
  --prompt "视频描述"

# 与兽为伍（指定狼首男友）
python3 {baseDir}/scripts/vidu_cli.py template \
  --template beast_companion \
  --image user_photo.jpg \
  --prompt "视频描述"

# 查询任务状态
python3 {baseDir}/scripts/vidu_cli.py status <task_id> --download ./uploads
```

## 输出规范

1. **下载目录**: `{baseDir}/uploads/`
2. **返回格式**: Markdown 格式引用文件
3. **视频链接**: 必须返回 Vidu API 的 `creations[0].url` 字段

## 环境配置

必需环境变量：

```bash
VIDU_API_KEY=your_api_key_here
```

获取 API Key：
- Vidu 官方开放平台：https://platform.vidu.cn 或 https://platform.vidu.com
- 注册账号后在「API Keys」页面创建

## API 域名选择

**重要规则**：根据用户语言自动选择 API 域名

| 用户语言 | API 域名 | 说明 |
|---------|---------|------|
| 简体中文 | `api.vidu.cn` | 国内用户（默认） |
| 其他语言 | `api.vidu.com` | 海外用户 |

**Base URL 配置**：
```python
# 简体中文用户
BASE_URL = "https://api.vidu.cn/ent/v2"

# 非简体中文用户（英文、日文、韩文等）
BASE_URL = "https://api.vidu.com/ent/v2"
```

**判断逻辑**：
- 用户使用简体中文 → 使用 `api.vidu.cn`
- 用户使用其他语言（英文、日文、韩文等） → 使用 `api.vidu.com`

## 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| Invalid API key | API密钥错误 | 检查 VIDU_API_KEY 环境变量 |
| Image size exceeds | 图片过大 | 压缩至50MB以下 |
| Task failed | 生成失败 | 查看 error 信息重试 |
| Template not found | 模板不存在 | 检查模板ID是否正确 |

## References

- [完整模板列表](references/template_list.md) - 389个特效模板
- [API参考文档](references/api_reference.md) - 所有API详细参数

## Rules

1. **API Key 检查**: 调用前确认 `VIDU_API_KEY` 已设置
2. **异步任务**: 特效生成异步进行，需轮询状态
3. **下载时效**: 生成 URL 24小时内有效
4. **返回视频链接**: 必须返回视频 URL 让用户直接访问
5. **严格使用用户照片**: 必须使用用户上传的照片，禁止使用默认图片

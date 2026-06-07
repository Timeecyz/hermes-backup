# fal.ai 配图集成指南

## API Key 配置

**Key 格式：** `{app_id}:{app_secret}` （两个部分用冒号连接，不是斜杠或空格）

**已配置：** fal.ai API key 已存入 Agent Memory（2025-05-27），格式 `b3cdc6f5-4451-4fce-ae77-de9405b0b344 / 253e6030633d7eac5ef311cc0a7476c9`。每次调用时从 memory 读取。

---

## fal.ai 正确 API 调用方式

### 端点格式（已验证）
- **提交地址：** `https://queue.fal.run/fal-ai/flux/schnell`
- **状态轮询：** `https://queue.fal.run/fal-ai/flux/requests/{request_id}/status`
- **结果获取：** `https://queue.fal.run/fal-ai/flux/requests/{request_id}`

### 完整 Python 调用流程
```python
import urllib.request, json, time

FAL_KEY = "b3cdc6f5-4451-4fce-ae77-de9405b0b344:253e6030633d7eac5ef311cc0a7476c9"

def submit_and_get_image(prompt):
    # Step 1: 提交任务
    payload = json.dumps({
        "prompt": prompt,
        "image_size": "landscape_16_9",
        "num_images": 1
    }).encode('utf-8')
    req = urllib.request.Request(
        'https://queue.fal.run/fal-ai/flux/schnell',
        data=payload,
        headers={
            'Authorization': f'Key {FAL_KEY}',
            'Content-Type': 'application/json'
        }
    )
    resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
    request_id = resp['request_id']
    
    # Step 2: 轮询完成状态（用 /status 端点，GET 方法）
    status_url = f'https://queue.fal.run/fal-ai/flux/requests/{request_id}/status'
    for _ in range(60):
        time.sleep(3)
        s = json.loads(urllib.request.urlopen(
            urllib.request.Request(status_url, headers={'Authorization': f'Key {FAL_KEY}'}),
            timeout=15
        ).read())
        if s.get('status') == 'COMPLETED':
            # Step 3: 从结果URL提取图片 URL（不是从 status 响应）
            result_url = f'https://queue.fal.run/fal-ai/flux/requests/{request_id}'
            result = json.loads(urllib.request.urlopen(
                urllib.request.Request(result_url, headers={'Authorization': f'Key {FAL_KEY}'}),
                timeout=15
            ).read())
            return result['images'][0]['url']
    return None

url = submit_and_get_image("你的提示词")
```

### 常见错误排查
| 错误 | 原因 | 修复 |
|------|------|------|
| `HTTP Error 404` | 端点格式错误 | 正确：`fal-ai/flux/schnell`，不是 `flux/schnell` |
| 轮询返回 `405 Method Not Allowed` | 用了错误的状态端点 | 用 `/status` 结尾的 URL 做 GET 轮询 |
| 轮询一直返回 `IN_QUEUE` | 正常，需等待 | 每5秒轮询一次，通常10-30秒完成 |
| 图片 URL 在 result 响应里取不到 | 在 result URL 而非 status URL 取结果 | 结果从 `/fal-ai/flux/requests/{id}` 取，不是 `/status` |
| `image_size` 参数无效 | 格式错误 | 用 `"landscape_16_9"`（下划线，不是冒号） |

### 图片尺寸参数参考
- `landscape_16_9` → 16:9 横版（文章配图标准）
- `square_hd` → 1:1 正方
- `portrait_4_3` → 4:3 竖版

---

## WeChat 素材上传完整流程

### 流程概览
```
fal.ai 图片URL
  → 下载到本地（curl 或 urllib）
  → 上传至微信永久素材（curl multipart/form-data）
  → 获得 media_id
  → 用于草稿 thumb_media_id 或内文图
```

### Step 1: 下载 fal.ai 图片（推荐用 curl）
```bash
curl -s --max-time 25 -o /tmp/fal_cover.jpg "https://v3b.fal.media/files/xxx.jpg"
# 超时时间设25秒，避免DNS问题
```

### Step 2: 上传至微信（用 curl，不要用 Python urllib 编码问题）
```bash
TOKEN=$(curl -s "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=wx37f93a23f90770b4&secret=c5fc89db461f4de7d55b65091979ce66" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 上传到永久素材（推荐，用 material/add_material）
curl -s -F "media=@/tmp/your_image.jpg" \
  "https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=$TOKEN&type=image"

# 返回格式：{"type":"image","media_id":"Qy593Mh...","created_at":1234567890,"item":[]}
```

### Step 3: 获取草稿 media_id（用于更新封面）
```bash
# 先查草稿列表，找到目标文章
curl -s "https://api.weixin.qq.com/cgi-bin/draft/batchget?access_token=$TOKEN" \
  -d '{"offset":0,"count":1}' | python3 -c "
import sys,json; d=json.load(sys.stdin)
for item in d.get('item',[]):
    for ni in item.get('content',{}).get('news_item',[]):
        print('media_id:', item.get('media_id'))
        print('title:', ni.get('title'))
"

# 输出示例：
# media_id: XDSxRVK2ZHBjglHZA5gScchsRPJGPHZP6rkVURMjknW4X7-8RqSr7_ni2oVZAZNt
# title: 香港券商被罚22亿，港险还能不能买？我算了笔账
```

### Step 4: 更新草稿封面（thumb_media_id）
```bash
# 注意：草稿更新接口目前只能更新 thumb_media_id，
# 内文图片需要用户手动在草稿编辑器中插入
curl -s "https://api.weixin.qq.com/cgi-bin/draft/update?access_token=$TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d "{\"media_id\":\"草稿media_id\",\"articles\":[{\"thumb_media_id\":\"新封面media_id\"}]}"
# 注意：草稿 update 接口对 JSON 格式要求严格，建议直接用 Python 实现
```

---

## 草稿内插图限制说明

**重要：** 微信公众号草稿 API 对内文图片插入有限制：

1. **封面图（thumb_media_id）**：可以更新，需要有效的 media_id
2. **内文图片**：草稿接口无法直接往已创建的草稿里动态插入多张图片
   - 解决方案A：用户手动在草稿编辑器中插入图片（从素材库选）
   - 解决方案B：生成带 `<img>` 标签的新版 HTML 推送新草稿（但格式受限）

**当前最优方案：** 用户在草稿箱手动插入内文图（从「素材库 → 图片」选择刚上传的5张图）。

---

## 配图风格规范（蛮子的要求）

### 整体风格
- 手绘感、插画风，非冰冷金融图
- 温暖色调：粉色/米色背景（#F5F0E6）+ 彩色强调
- 白底 + 黑色线条 + 柔和彩色强调 + 卡通人物 + 手写字体
- 中英双语，步骤式内容呈现

### 封面图模板
```
创作一张手绘风格的封面图，比例为 16:9 横版。
背景为带有纸质肌理的米色，体现质朴手绘美感。
中央以红黑对比鲜明的大号毛笔草书字体书写「[文章主标题]」。
字体保持流畅韵律，具艺术气息。
在标题下方用较小字号草书注明「[副标题/核心亮点]」。
在画面角落绘制与主题相关的手绘装饰图标。
整体布局简洁大气，留白充足，突出标题主体。
```

### 信息图卡片模板（每章节一张）
```
创作一张手绘风格的信息图卡片，比例为 16:9 横版。
背景为带有纸质肌理的米色或米白色（#F5F0E6），体现质朴亲切感。
卡片上方以红黑相间、对比鲜明的大号毛笔草书字体突出「[章节标题]」。
文字内容均采用中文草书，分 2-4 个小节，每节以简短精炼的短语表达核心要点。
字体保持草书流畅韵律，清晰可读且具艺术气息。
每小节旁配简单手绘图标（如：盾牌/计算器/放大镜等）。
整体布局注重视觉平衡，预留充足空白，使画面简洁明了。
```

### 图标参考清单
| 内容类型 | 推荐图标 | 含义 |
|---------|---------|------|
| 成本/贷款 | 🏠 小房子 | 贷款/房贷关联 |
| 收益/增长 | 📈 向上箭头 | 正向增长 |
| 偿付/备用金 | 💰 存钱罐 | 储蓄/保障 |
| 诚信/兑现 | ✅ 对勾 | 承诺兑现 |
| 风险/警示 | ⚠️ 感叹号 | 风险提示 |
| 天平 | ⚖️ 天平 | 平衡/对比 |
| 跨境/互通 | 🌉 桥 | 连接/互通 |
| 护照/赴港 | 📘 护照 | 赴港/通关 |

---

## 完整工作流（配图+上传）

```
1. 生成图片（fal.ai，5张并发提交）
2. 轮询等待（每张约30秒）
3. 下载到本地（curl，25秒超时）
4. 上传到微信永久素材（curl multipart/form-data）
5. 获得 media_id
6. 告知用户：封面图已绑定草稿，内文图需手动插入
```

---

## 已知问题

### IP 白名单（errcode: 40164）
微信 API 请求来自动态 IP 服务器，每次出口 IP 可能不同。
解决：把当前服务器 IP 加入微信公众号后台白名单。
查 IP：`curl -s https://ipinfo.io/ip`

### 草稿内文图无法自动插入
草稿 `update` 接口无法动态插入内文图片，只能更新封面 thumb_media_id。
内文图需要用户手动从素材库插入草稿编辑器。

### 封面图 media_id 必须有效
thumb_media_id 留空会导致草稿推送失败。确保上传的图片 media_id 真实有效。
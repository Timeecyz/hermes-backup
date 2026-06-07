# fal.ai 配图生成：中文乱码问题与解决方案

**更新：2026-05-27**

---

## 核心问题

**fal.ai `flux/schnell` 模型不支持中文毛笔/草书字体生成**。

生成图片时如果 prompt 中包含中文，输出结果是乱码字符——一堆无法辨认的符号拼凑，完全不可用。

---

## 解决方案

**生成图片时，prompt 中完全移除所有中文**，改用：
- 英文描述场景和风格
- 图标符号（emoji 或英文单词）传达关键词信息
- 数字/金额直接写阿拉伯数字
- 章节编号用 `PART 01` / `PART 02` 等英文格式

---

## 正确 vs 错误 prompt 示例

### ✅ 正确示例（英文+图标，可正常生成）

**封面图：**
```
Hand-drawn style cover image, 16:9 landscape.
Cream parchment background with paper texture.
Center: bold red brush-stroke title '22 Billion Fine - What It Means For You'.
Subtitle in smaller lettering. Corner icons: scales, shield, passport.
Warm cream tones, red and black ink, generous white space.
```

**PART 01 信息图：**
```
Hand-drawn info graphic card, 16:9 landscape. Cream paper texture background.
Top: bold red brush calligraphy title 'PART 01 CONCLUSION FIRST'.
Body divided into 3 sections with hand-drawn icons beside each point:
  - Section 1 with shield icon labeled 'REGULATORY FINES'
  - Section 2 with house icon labeled 'CROSS-BORDER BROKERAGE'
  - Section 3 with checkmark icon labeled 'COMPLIANCE PATH'
Simple cartoon style, black ink lines, red accent text.
Clean white space, minimalist layout.
```

**PART 03 政策方向：**
```
Hand-drawn information card, 16:9 landscape. Warm cream background.
Top: bold red title 'PART 03 POLICY DIRECTION'.
Body shows: bridge icon labeled 'MUTUAL MARKET ACCESS',
scroll icon labeled 'IRBC GUIDELINES',
handshake icon labeled 'COMPLIANCE PATH AVAILABLE'.
Simple cute illustration style, black ink outlines, red highlights.
Generous whitespace, clean minimalist layout.
```

### ❌ 错误示例（会导致乱码）

```
"创作一张手绘风格的信息图卡片，背景为纸质肌理米色，
卡片上方以红黑毛笔草书字体突出「先说结论」，
文字内容以中文草书分三小节呈现核心要点"
→ 生成结果：一堆看不懂的符号
```

---

## 蛮子验证过的可用 prompt 模板

```python
# 封面 prompt 模板
COVER_PROMPT = """Hand-drawn style info card, 16:9 landscape. Cream parchment background with paper texture.
Center: bold red calligraphy-style title '{title}' with black ink brush strokes.
Subtitle in smaller Chinese-style lettering: '{subtitle}'. Corner decorations: scales of justice icon, shield icon, passport icon.
Warm cream tones, red and black ink, hand-painted watercolor texture. Clean layout with generous white space."""

# PART 信息图 prompt 模板
PART_PROMPT = """Hand-drawn info graphic card, 16:9 landscape. Cream paper texture background.
Top: bold red calligraphy header '{part_title}'. Body divided into {n} sections with hand-drawn icons:
{points}
Red and black brush stroke text, watercolor ink style, simple line icons beside each point.
Warm muted tones, clean minimalist layout."""
```

---

## 完整生成流程

```python
import urllib.request
import json
import time

FAL_KEY = "b3cdc6f5-4451-4fce-ae77-de9405b0b344:253e6030633d7eac5ef311cc0a7476c9"

def generate_image(prompt, idx):
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
    
    # Step 2: 轮询
    status_url = f'https://queue.fal.run/fal-ai/flux/requests/{request_id}/status'
    for _ in range(60):
        time.sleep(3)
        s = json.loads(urllib.request.urlopen(
            urllib.request.Request(status_url, headers={'Authorization': f'Key {FAL_KEY}'}),
            timeout=15
        ).read())
        if s.get('status') == 'COMPLETED':
            result_url = f'https://queue.fal.run/fal-ai/flux/requests/{request_id}'
            result = json.loads(urllib.request.urlopen(
                urllib.request.Request(result_url, headers={'Authorization': f'Key {FAL_KEY}'}),
                timeout=15
            ).read())
            return result['images'][0]['url']
    return None
```

---

## 下载：不要用 execute_code，用 terminal curl

execute_code 的 urllib 有严格超时限制，会报 `TimeoutError`。

**正确方式（用 terminal）：**
```bash
curl -s --max-time 40 -o /tmp/new_imgs/cover.jpg "https://v3b.fal.media/files/xxx.jpg"
```

---

## 已知问题

| 问题 | 原因 | 方案 |
|------|------|------|
| 中文乱码 | fal.ai flux 不支持中文书法 | prompt 改用英文 |
| execute_code 下载超时 | sandbox 严格超时限制 | 改用 terminal curl |
| 微信 IP 白名单 | 服务器 IP 未加入白名单 | 添加 IP 111.229.192.217，或临时发给用户手动上传 |
| 草稿内文图无法插入 | 微信草稿 API 限制 | 图片发给用户，用户手动从素材库插入 |
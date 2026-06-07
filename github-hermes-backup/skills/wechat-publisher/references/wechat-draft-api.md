# 微信公众号草稿箱 API 操作手册

**创建时间：** 2026-06-05
**验证状态：** ✅ 已验证（2026-06-06 — 成功创建含图片草稿）

---

## 核心 API 端点

| 操作 | URL | 方法 |
|------|------|------|
| 获取 access_token | `https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}&type=stable` | GET |
| 草稿箱总数 | `https://api.weixin.qq.com/cgi-bin/draft/count?access_token={TOKEN}` | GET |
| 草稿列表 | `https://api.weixin.qq.com/cgi-bin/draft/batchget?access_token={TOKEN}` | POST |
| 读取单篇草稿内容 | `https://api.weixin.qq.com/cgi-bin/draft/get?access_token={TOKEN}` | POST |
| 上传正文图片 | `https://api.weixin.qq.com/cgi-bin/media/upload?access_token={TOKEN}&type=image` | POST |
|推送草稿箱 | `https://api.weixin.qq.com/cgi-bin/draft/add?access_token={TOKEN}` | POST |

---

## Python 操作模板

### 1. 获取 Token

```python
import requests, json

APPID = "wx37f93a23f90770b4"
APPSECRET = "c5fc89db461f4de7d55b65091979ce66"

# ⚠️ 必须带 type=stable，否则报 40001 invalid credential
r = requests.get(
    'https://api.weixin.qq.com/cgi-bin/token',
    params={'grant_type': 'client_credential', 'appid': APPID, 'secret': APPSECRET, 'type': 'stable'}
)
token = r.json()['access_token']
```

### 2. 读取草稿列表

```python
list_url = f'https://api.weixin.qq.com/cgi-bin/draft/batchget?access_token={token}'
data = json.dumps({"offset": 0, "count": 20}).encode()
req = requests.post(list_url, data=data, headers={'Content-Type': 'application/json'}, timeout=10)
drafts = req.json()
for item in drafts.get("item", []):
    content = item["content"]["news_item"][0]
    print(f"Title: {content['title']} | Digest: {content['digest']} | Media ID: {item['media_id']}")
```

### 3. 读取单篇草稿全文

```python
media_id = "XDSxRVK2ZHBjglHZA5gScWf4MsZuMIDIhhN3QpM2JDr5YAm3Xoy48gzLZw45H1p1"
get_url = f'https://api.weixin.qq.com/cgi-bin/draft/get?access_token={token}'
payload = json.dumps({"media_id": media_id}).encode()
req = requests.post(get_url, data=payload, headers={'Content-Type': 'application/json'}, timeout=10)
full = req.json()
news_item = full["news_item"][0]
print(news_item["title"])
print(news_item["content"])  # HTML 格式
```

### 4. 上传正文图片（⚠️ 用 requests + files={}）

```python
import requests

with open('image.png', 'rb') as f:
    img_data = f.read()

# 用 type=image，不是 thumb
upload_url = f'https://api.weixin.qq.com/cgi-bin/media/upload?access_token={token}&type=image'
files = {'media': ('image.png', img_data, 'image/png')}
r = requests.post(upload_url, files=files, timeout=30)
media_id = r.json()['media_id']  # f61mr... 前缀，可用于正文 <img src>
```

### 5. 推送草稿到草稿箱

```python
import requests, json

# ⚠️ thumb_media_id 必须用草稿箱里已有的 XDSx... 前缀 ID
# 不能用新上传的 f61mr... 前缀 media_id，会报 40007 invalid media_id
# 从草稿列表中找任意已有文章，提取其 thumb_media_id
thumb_media_id = 'XDSxRVK2ZHBjglHZA5gScax7xK4UznAH8zCLC6v3rfY1kEPs-pq-7GhSAAxXrHHG'

article = {
    'title': '境外资产配置合规指南',   # 中文标题 ≤20 字(约64字节)
    'digest': '证券变现后钱放哪',       # 摘要 ≤18 字节中文
    'content': html_content,
    'thumb_media_id': thumb_media_id,
    'need_open_comment': 1,
    'only_fans_can_comment': 0,
}

create_url = f'https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}'
r = requests.post(create_url, json={"articles": [article]}, timeout=15)
result = r.json()
# 成功: {"media_id": "XDSx...", "item": [{"index": 0, "ad_count": 0}]}
```

---

## 凭证速查

| 字段 | 值 |
|------|-----|
| AppID | wx37f93a23f90770b4 |
| AppSecret | c5fc89db461f4de7d55b65091979ce66 |
| 服务器IP | 111.229.192.217（需加入白名单） |
| 凭证文件 | ~/.hermes/secret&API.md |

---

## 已知坑

1. **access_token 必须带 `&type=stable`**：不带这个参数会报 40001 invalid credential
2. **thumb_media_id 必须是草稿箱里已有的 XDSx... 前缀 ID**：新上传的 f61mr... 前缀 media_id 会报 40007 invalid media_id；解决方法是从草稿列表中找一个已有文章，提取其 thumb_media_id 来用
3. **封面图尺寸限制**：thumb 必须 < 64KB，超过报 40006；可用 PIL 压缩：
   ```python
   from PIL import Image
   img = Image.open('cover.png').convert('RGB').resize((900, 386), Image.LANCZOS)
   img.save('cover_thumb.jpg', 'JPEG', quality=70, optimize=True)  # 目标 < 50KB
   ```
4. **正文图片上传必须用 requests + files={}**：urllib.request 报 41005 "media data missing"
5. **草稿标题长度限制**：中文标题 bytes 上限约 64 字节（约 20 字），超限报 45003
6. **草稿摘要 digest 长度限制**：bytes 上限约 54，超限报 45004；目前测试 ≤18 字节中文安全
7. **IP 不在白名单**：错误码 40164 → 微信公众号后台 → 开发 → 基本配置 → IP白名单 → 添加 111.229.192.217
8. **access_token 有效期**：7200秒，每次调用前重新获取
9. **草稿箱总数**：total_count 直接返回 int，不是 dict

---

## 蛮子工作流（已验证 2026-06-06）

1. 用 API 读取草稿箱 → 定位目标文章 → 获取 HTML 内容
2. 分析内容 → 生成配图提示词（凹版版画风格）
3. **发飞书给蛮子确认**（不走 wenyan-cli）
4. 蛮子确认后手动复制到公众号草稿箱，或用 API推送
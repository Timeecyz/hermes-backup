# 微信公众号素材库图片上传与草稿推送

**验证时间：** 2026-06-06

---

## 两种图片上传接口的区别

| 接口 | endpoint | 类型 | 用途 | media_id 前缀 |
|------|----------|------|------|--------------|
| `media/upload` | `/cgi-bin/media/upload?access_token=...&type=image` | 临时 | 正文中插图 | `f61mr...` |
| `material/add_material` | `/cgi-bin/material/add_material?access_token=...&type=image` | 永久 | 素材库、封面图 | `XDSx...` |

**封面图 thumb_media_id 必须用 XDSx 前缀**（永久素材），否则报 40007。

---

## 永久素材上传（add_material）完整代码

```python
import urllib.request, json

APPID = "wx37f93a23f90770b4"
APPSECRET = "c5fc89db461f4de7d55b65091979ce66"

# 获取 token
r = urllib.request.urlopen(
    "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid="
    + APPID + "&secret=" + APPSECRET + "&type=stable"
)
token = json.loads(r.read())['access_token']

upload_url = "https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=" + token + "&type=image"

files = [
    ("/tmp/card-01.png", "01-Naval-Wealth-Chinese-Brand.png"),
    ("/tmp/card-02.png", "02-Eisenhower-Plan-Chinese-Brand.png"),
    ("/tmp/card-03.png", "03-Housel-Freedom-Chinese-Brand.png"),
    ("/tmp/card-04.png", "04-Housel-Rich-Chinese-Brand.png"),
]

boundary = "----FormBoundary7MA4YWxkTrZu0gW"

for path, name in files:
    with open(path, 'rb') as f:
        img_data = f.read()
    header = ("--" + boundary + "\r\n"
              "Content-Disposition: form-data; name=\"media\"; filename=\"" + name + "\"\r\n"
              "Content-Type: image/png\r\n\r\n").encode()
    footer = ("\r\n--" + boundary + "--\r\n").encode()
    body = header + img_data + footer
    req = urllib.request.Request(upload_url, data=body)
    req.add_header('Content-Type', 'multipart/form-data; boundary=' + boundary)
    result = json.loads(urllib.request.urlopen(req).read())
    if 'media_id' in result:
        print("OK:", name, "->", result['media_id'])
    else:
        print("FAIL:", name, "->", result)
```

---

## 推送草稿到草稿箱（含中文HTML）

⚠️ **execute_code 中不能写含中文+双引号嵌套的 HTML 正文** — SyntaxError。

**正确做法：** 写脚本到 `/tmp/push_draft.py` → 用 `terminal` 执行。

```python
# /tmp/push_draft.py
import urllib.request, json

APPID = "wx37f93a23f90770b4"
APPSECRET = "c5fc89db461f4de7d55b65091979ce66"

r = urllib.request.urlopen(
    "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid="
    + APPID + "&secret=" + APPSECRET + "&type=stable"
)
token = json.loads(r.read())['access_token']

# 从已有草稿获取 thumb_media_id
list_url = "https://api.weixin.qq.com/cgi-bin/draft/batchget?access_token=" + token
data = json.dumps({"offset": 0, "count": 20}).encode('utf-8')
req = urllib.request.Request(list_url, data=data, headers={'Content-Type': 'application/json; charset=utf-8'})
r2 = urllib.request.urlopen(req)
result = json.loads(r2.read())
thumb_media_id = result['item'][0]['content']['news_item'][0]['thumb_media_id']

article = {
    "title": "文章标题",
    "author": "环球经纪人Claire",
    "digest": "摘要文字（≤18字节中文）",
    "content": open("/tmp/article_body.html").read(),
    "thumb_media_id": thumb_media_id,
    "need_open_comment": 1,
    "only_fans_can_comment": 0
}

payload = json.dumps({"articles": [article]}, ensure_ascii=False).encode('utf-8')
req3 = urllib.request.Request(
    "https://api.weixin.qq.com/cgi-bin/draft/add?access_token=" + token,
    data=payload,
    headers={'Content-Type': 'application/json; charset=utf-8'}
)
result3 = json.loads(urllib.request.urlopen(req3).read())
print(result3)
```

```bash
python3 /tmp/push_draft.py
```

---

## 完整工作流（今日验证）

1. **写文章** → 飞书确认
2. **生成配图** → HTML + Playwright 截图
3. **上传配图到素材库** → `add_material` → XDSx 前缀 media_id
4. **推送草稿** → `draft/add` API（thumb_media_id 用已有草稿的）
5. **手动换封面** → 草稿箱里手动替换封面图

**推荐：** 步骤1-3全自动化，步骤4-5蛮子手动处理（5分钟搞定，比磕API快）。
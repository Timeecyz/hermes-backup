# WeChat 草稿箱 API 实战笔记

**更新：2026-06-05**

---

## 坑 1：`draft/update` 无法使用

**现象**：`draft/update` 无论 payload 如何构造，始终返回 `{"errcode": 47001, "errmsg": "data format error"}`

**原因**：WeChat API 自身 bug，与 payload 结构无关（实测与 `draft/add` 完全一致的字段结构仍报错）

**变通方案**：
```python
# ❌ 不行：原地更新
payload = json.dumps({"media_id": old_media_id, "articles": [article]})
urllib.request.urlopen("https://api.weixin.qq.com/cgi-bin/draft/update?access_token=" + token, data=payload)

# ✅ 可行：用 draft/add 创建全新草稿，传入完整内容
payload = json.dumps({"articles": [article]})
result = json.loads(urllib.request.urlopen("https://api.weixin.qq.com/cgi-bin/draft/add?access_token=" + token, data=payload).read())
new_media_id = result["media_id"]
```

**影响**：无法原地修改草稿的封面图或正文内容，只能重建整个草稿。

---

## 坑 2：获取永久素材的真实 URL

**现象**：`media/get` 接口对永久素材返回 `{"errcode": 40066, "errmsg": "invalid media_id"}`

**原因**：接口路径/参数错误

**正确方式**：用 `material/batchget_material` 获取 mmbiz URL
```python
list_url = f"https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token={token}"
payload = json.dumps({"offset": 0, "count": 20, "type": "image"}).encode()
# POST 并解析 item[].url 字段
# 格式：https://mmbiz.qpic.cn/mmbiz_png/...
```

**不能用**：`https://api.weixin.qq.com/cgi-bin/media/get?access_token=...&media_id=...`（返回 40066）

---

## 坑 3：内容图片替换策略

**场景**：原草稿有旧图，需要在正文中批量替换为新上传的图

**步骤**：
1. 用 `material/batchget_material` 获取新图的 clean mmbiz URL（如 `https://mmbiz.qpic.cn/mmbiz_png/chUQ28ACiawADU1OsuBsnVLXITI72yNOw2nPFL7WRjKduO5e`）
2. 用正则提取原文中旧 URL 的特征字符串（注意：原文 URL 往往带 `?from=appmsg` 等查询参数）
3. 用 `re.sub(r'https://mmbiz\.qpic\.cn/[^"\']*' + re.escape(old_pattern) + r'[^"\']*', new_clean_url, html)` 做全局替换
4. **注意**：正文里同一张图可能有多处引用（正文主体 + 题图小图），替换后可能产生重复显示，确认只改内容区

**典型旧 URL 模式**（来自本次操作）：
```python
old_patterns = {
    "data-chart":   "3WBeSx1wTfdF2hxtwISW2qLsTn3BYbjRys7Yic4trOXplveqNsAYdla2zYHfR6EuDBkR9gkqrGGEG89wgibqEwTA",
    "regulations":  "xNoeJUwcgkmF9tmYZUP8TsjuticbBJEkibESE09HPkAHedrhYAwwudjfaCOKeAdgYSB1ApJvE4MRduDS5PrlDjJQ",
    "risk":         "chUQ28ACiawA5qYbncTp3REPicoibMZiaFzTugmzPuwpUfqB7EsF152qbsmW0AY92Q0KkVwQJDPPNmgf5gQEDDh7Lu09OC4",
}
```

---

## 工作流总结（更新后）

**上传图片到草稿箱文章的标准流程**：
1. 上传图片 → 得到 `media_id`
2. `material/batchget_material` → 获取 `url`（mmbiz 永久 URL）
3. 读取原草稿 HTML 内容 → 正则替换旧图 URL → 用 `draft/add` 重建草稿
4. 封面图在重建时一并通过 `thumb_media_id` 替换

> ⚠️ 封面图也是用 `draft/add` 重建替换，不能用 `draft/update`

# 日记晚间总结 — 管家点评写入流程

**用途**：执行 22:00 晚间日记总结时，读取当日日记内容并写入管家点评。

## 关键常量

```python
NOTION_TOKEN  = "[NOTION_TOKEN_REDACTED]"
DIARY_DB_ID   = "318cd9aa-41cc-8098-803e-ed230c9c7e80"   # Everyday's Journal (linked database)
NOTION_VER    = "2025-09-03"   # 推荐使用最新版
```

## ⚠️ 重要：DIARY_DB_ID 是 Linked Database

`318cd9aa-41cc-8098-803e-ed230c9c7e80` 是 linked database，不能直接 query `/databases/{id}/query`。

**正确步骤：**
1. 先 GET `/databases/{DIARY_DB_ID}` 获取 `data_sources[0].id` 作为 `data_source_id`
2. 用 `POST /v1/data_sources/{data_source_id}/query` 查询今日 page

⚠️ **陷阱**：`data_source_id` 不在 `parent.data_source_id`，而在 `data_sources[0].id`。
直接查 `parent.data_source_id` 会 KeyError。

## 完整流程

```python
import subprocess, json, datetime

NOTION_TOKEN = "[NOTION_TOKEN_REDACTED]"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2025-09-03",
    "Content-Type": "application/json; charset=utf-8"
}

def run_curl(method, url, payload=None):
    """curl + TLS 1.3 — 所有写入操作必须用 --tlsv1.3"""
    import subprocess, json
    with open('/tmp/notion_req.json', 'w', encoding='utf-8') as f:
        json.dump(payload or {}, f, ensure_ascii=False, indent=2)
    cmd = [
        'curl', '-s', '-X', method, url,
        '-H', f"Authorization: Bearer {NOTION_TOKEN}",
        '-H', 'Notion-Version: 2025-09-03',
        '-H', 'Content-Type: application/json; charset=utf-8',
        '--data-binary', '@/tmp/notion_req.json',
        '--tlsv1.3'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

# ── 步骤1：获取 data_source_id（因为 DIARY_DB_ID 是 linked database）────────
db_info = run_curl('GET', f"https://api.notion.com/v1/databases/318cd9aa-41cc-8098-803e-ed230c9c7e80")
# ⚠️ data_source_id 在 data_sources[0].id，不在 parent.data_source_id
data_source_id = db_info['data_sources'][0]['id']
print(f"data_source_id: {data_source_id}")

# ── 步骤2：查询今日日记 page_id ────────────────────────────────────────────
today = datetime.date.today().isoformat()   # e.g. "2026-05-29"
query = {
    "filter": {"property": "Date", "date": {"equals": today}},
    "page_size": 5
}
result = run_curl('POST', f"https://api.notion.com/v1/data_sources/{data_source_id}/query", query)
results = result.get('results', [])
if not results:
    print(f"今日 ({today}) 日记页面不存在或尚未创建，跳过晚间总结")
    exit(0)
page_id = results[0]['id']   # ← full UUID，直接用于后续调用

# ── 步骤3：读取所有 blocks ─────────────────────────────────────────────────
result = run_curl('GET', f"https://api.notion.com/v1/blocks/{page_id}/children?page_size=100")
blocks = result.get('results', [])
if not blocks:
    print(f"日记页面存在但内容为空，可能尚未填写，跳过晚间总结")
    exit(0)

# ── 步骤4：解析内容 ─────────────────────────────────────────────────────────
# to_do blocks：checked=True/False，内容在 rich_text 的 plain_text 字段
# paragraph blocks：内容在 rich_text 的 plain_text 字段
# heading_2：通常标记章节如 "🌙 今日管家点评"
# 空 to_do 的特征：rich_text 为 []，plain_text 为 ''
for b in blocks:
    t = b.get('type')
    if t in ('to_do', 'paragraph'):
        raw = b.get(t, {})
        rt = raw.get('rich_text', [])
        txt = ''.join(r.get('plain_text', '') for r in rt)
        if t == 'to_do':
            checked = raw.get('checked', False)
            print(f"  [{'x' if checked else ' '}] {txt}")
        else:
            print(f"  {txt}")
    elif t == 'heading_2':
        txt = ''.join(r.get('plain_text', '') for r in b.get('heading_2', {}).get('rich_text', []))
        print(f"\n## {txt}\n")
```

### 日记页面结构（参考 2026.5.28）

| Section | Block type | 关键字段 |
|---------|-----------|---------|
| 💭 Thoughts | heading_1 | — |
| ✅ Have Done | heading_2 | to_do.checked=True |
| 📋 To Do | heading_2 | to_do.checked=False |
| 🙏 Be Grateful | heading_2 | paragraph |
| 🏋️ Work out | heading_2 | paragraph（运动记录） |
| 🍽️ Diets | heading_2 | bulleted_list_item |
| 💤 Sleep | heading_2 | paragraph |
| ⏱️ Time Audit | heading_2 | paragraph |
| 📝 学习笔记摘要 | heading_2 | — |
| 🏋️ 20 项习惯打卡 | heading_2 | to_do × 17 |
| 👔 今日穿搭 | heading_2 | paragraph |
| 🏆 小助理の今日总结 | heading_2 | — |
| 🌙 今日管家点评 | heading_2 | **管家写入位置** |
| 💡 明日建议 | heading_2 | bulleted_list_item |

### 解析 17 项习惯打卡

20 项习惯打卡在 heading_2「🏋️ 20 项习惯打卡」之后，全部是 to_do 类型：
- 已完成：checked=True
- 未完成：checked=False
- 英文名称：`📈 Clients 2h`, `📈 Financial studies 1h`, `📰 Macro News 1h`, `🤖 AI Study 1h`, `📖 Reading 30min`, `✍️ Writing 15min⁺`, `🏋️ Workout 30min⁺`, `😋 Chewing slowly 20times a bite`, `👌 Doing planks`, `❌ NO Sugar`, `🇬🇧 Duolingo`, `🇬🇧 English`, `😴 Nap 15min⁺`, `💧 Water 2200⁺`, `🧘 Meditation 5min⁺`, `💪 Kegel 5min⁺`, `💊 Supplements`, `🪞 BETTER ME?`, `🪞 BENEFIT SOCIETY?`, `⚙️ SYSTEM DRIVEN?`
注意：题目描述写的是「17项打卡」，但实际模板有 20 项（可能有一两项未启用）。以实际读取到的数量为准。

### 解析 To Do 完成率

To Do section 的结构：
- `heading_2` 包含 "To Do" 文字
- 后面紧跟的 `to_do` blocks（checked 状态）
- section 切换（遇到下一个 heading_2）时重置

统计方法：遍历 blocks，跟踪当前 section，to_do.total += 1，to_do.checked += 1 当 checked=True。

## 写入管家点评

```python
review_blocks = [
    {"object": "block", "type": "heading_2",
     "heading_2": {"rich_text": [{"type": "text", "text": {"content": "🌙 今日管家点评"}}]}},
    {"object": "block", "type": "paragraph",
     "paragraph": {"rich_text": [{"type": "text", "text": {"content": "管家点评正文，50-100字，温暖有温度，像朋友聊天，不说教。发现亮点就夸，做得不好的温和提醒。"}}]}},
    {"object": "block", "type": "heading_2",
     "heading_2": {"rich_text": [{"type": "text", "text": {"content": "💡 明日建议"}}]}},
    {"object": "block", "type": "bulleted_list_item",
     "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "建议1"}}]}},
    {"object": "block", "type": "bulleted_list_item",
     "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "建议2"}}]}}
]

payload = {"children": review_blocks}
run_curl('PATCH', f"https://api.notion.com/v1/blocks/{page_id}/children", payload)
```

## 飞书推送（可选）

如果配置了飞书 Webhook，发送总结：
```
🌙 {日期} 日记总结
✅ To Do 完成率：X/Y
🏋️ 打卡完成：N/20
💡 明日建议：...
```

飞书 Webhook 失效时返回 `code: 19001` "param invalid: incoming webhook access token invalid"，需要更新机器人 Webhook 地址。

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `invalid_request_url` on database query | DIARY_DB_ID 是 linked database，不能直接 query | 先 GET /databases/{id} 获取 data_sources[0].id，用 data_sources/{id}/query |
| KeyError: 'data_source_id' | 错误地从 parent.data_source_id 读取 | 从 data_sources[0].id 获取 |
| `validation_error: path.block_id should be a valid uuid` | 使用了截断的8字符ID | 数据库查询返回的 page id 本身就是完整 UUID，直接使用 |
| 读取 blocks 返回 `[]` 但页面有内容 | 使用的不是 linked database 的正确 endpoint | 确认用 `data_sources/{id}/query` 而非 `databases/{id}/query` |
| 今日日记 page 查询返回 0 条 | 日记页面尚未创建（空日记） | 跳过晚间总结，silent 退出 |
| 空 to_do 被误解析为有内容 | to_do 的 rich_text 为 `[]`，text 为 `''` | 用 `''.join(r.get('plain_text','') for r in rich_text)` 提取 |
| 飞书推送 code 19001 | Webhook token 失效 | 更新飞书机器人 Webhook 地址 |
# 日记创建参考脚本

**用途**：从模板页面复制完整结构，创建当日日记。

## 关键常量

```python
NOTION_TOKEN = "[NOTION_TOKEN_REDACTED]"
DIARY_DB_ID  = "318cd9aa-41cc-8098-803e-ed230c9c7e80"   # Everyday's Journal
TEMPLATE_ID  = "34acd9aa-41cc-8194-8639-cae39559b759"   # 【模板】2026.4.1
```

## 模板结构说明（实测 2026.6.6）

模板页 `34acd9aa-41cc-8194-8639-cae39559b759` 顶层 blocks：

| type | id (前8位) | 说明 |
|------|-----------|------|
| `synced_block` | `368cd9aa` | `synced_from: null`，但 children GET 返回 404，**不可用** |
| `paragraph` | `373cd9aa` | 空段落 |
| `child_page` | `373cd9aa` | 内含另一个 synced_block（无内容）|
| `child_page` | `375cd9aa` | ✅ **真正的模板结构**，含完整 62 blocks |
**正确做法**：读取 `375cd9aa-41cc-81c5-a2b1-fe098d9d34ac` 的 children 作为模板内容。

```python
TEMPLATE_CHILD_PAGE_ID = "375cd9aa-41cc-81c5-a2b1-fe098d9d34ac"
blocks = session.get(f"https://api.notion.com/v1/blocks/{TEMPLATE_CHILD_PAGE_ID}/children?page_size=100").json()['results']
```

## 昨天→今天 To Do 同步逻辑

**目标**：昨天「📋 To Do」中 `checked=false` 的条目，追加到今天日记的「✅ Have Done List」。

**步骤**：
1. 读取昨天日记 page 的所有 blocks
2. 找到 `heading_2`包含「📋 To Do」的 block，从下一 block 起收集 `to_do` 类型
3. 过滤 `checked=false` 且 `plain_text` 非空（`txt.strip()`）的条目
4. 以 `checked=false` 的 to_do blocks 追加到新页面

**注意**：搜索结果中的 ID 可能是 `child_page` block 的 ID 而非 page ID。GET `/blocks/{id}/children` 返回 404 时，说明该 ID 是 page ID 但 block 不存在；应改查 `/pages/{id}` 确认，或用 DIARY_DB_ID + title filter 查询。

## 完整流程

```python
import subprocess, json, datetime, time, requests

NOTION_TOKEN = "[NOTION_TOKEN_REDACTED]"
HEADERS = {"Authorization": f"Bearer {NOTION_TOKEN}", "Notion-Version": "2022-06-28"}

def run_notion(url, payload, method='POST'):
    """curl + TLS 1.3 — 所有写入操作必须用这个"""
    with open('/tmp/notion_req.json', 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    result = subprocess.run([
        'curl', '-s', '-X', method, url,
        '-H', f"Authorization: Bearer {NOTION_TOKEN}",
        '-H', 'Notion-Version: 2022-06-28',
        '-H', 'Content-Type: application/json; charset=utf-8',
        '--data-binary', '@/tmp/notion_req.json',
        '--tlsv1.3'
    ], capture_output=True, text=True)
    return json.loads(result.stdout)

def copy_rich_text(rt_list):
    return [{"type": "text", "text": {"content": t.get('plain_text',''), "link": None}}
            for t in rt_list]

def block_to_dict(blk):
    """将 API 返回的 block 转为可写入格式"""
    bt = blk.get('type')
    raw = blk.get(bt, {})
    base = {"object": "block", "type": bt}
    if bt == 'heading_1':
        base["heading_1"] = {"rich_text": copy_rich_text(raw.get('rich_text',[])), "color": raw.get('color','default')}
    elif bt == 'heading_2':
        base["heading_2"] = {"rich_text": copy_rich_text(raw.get('rich_text',[])), "color": raw.get('color','default')}
    elif bt == 'paragraph':
        base["paragraph"] = {"rich_text": copy_rich_text(raw.get('rich_text',[])), "color": raw.get('color','default')}
    elif bt == 'to_do':
        base["to_do"] = {"rich_text": copy_rich_text(raw.get('rich_text',[])),
                        "checked": raw.get('checked', False), "color": raw.get('color','default')}
    elif bt == 'bulleted_list_item':
        base["bulleted_list_item"] = {"rich_text": copy_rich_text(raw.get('rich_text',[])), "color": raw.get('color','default')}
    elif bt == 'callout':
        base["callout"] = {"rich_text": copy_rich_text(raw.get('rich_text',[])), "icon": raw.get('icon',{}), "color": raw.get('color','default')}
    elif bt == 'divider':
        base["divider"] = {}
    else:
        return None
    return base

# 1. 读取模板（读 child_page，不是 synced_block）
session = requests.Session()
session.headers.update(HEADERS)
TEMPLATE_CHILD_PAGE_ID = "375cd9aa-41cc-81c5-a2b1-fe098d9d34ac"
template_inner = session.get(f"https://api.notion.com/v1/blocks/{TEMPLATE_CHILD_PAGE_ID}/children?page_size=100").json()['results']

# 2. 创建日记页面（用今天的日期）
today = datetime.date.today()
title = f"{today.strftime('%Y.%m.%d')} 📓高能量女孩👧日记📒"
new_page = run_notion("https://api.notion.com/v1/pages", {
    "parent": {"database_id": DIARY_DB_ID},
    "properties": {
        "Name": {"title": [{"text": {"content": title}}]},
        "Tags": {"multi_select": [{"name": "📓 日记"}]},
        "Date": {"date": {"start": today.isoformat()}},
    }
})
new_page_id = new_page['id']

# 3. 批量写入 blocks（每批 5 个 + 重试）
children = [block_to_dict(b) for b in template_inner if block_to_dict(b)]
for i in range(0, len(children), 5):
    batch = children[i:i+5]
    for retry in range(3):
        r = run_notion(f"https://api.notion.com/v1/blocks/{new_page_id}/children",
                       {"children": batch}, method='PATCH')
        if isinstance(r, dict) and 'results' in r:
            break
        time.sleep(2)
    time.sleep(1)

# 4. 追加昨天未完成的 To Do
# （读取昨天日记→找到 To Do section→过滤 unchecked→append to new page）
```

## 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| `invalid_request_url` | 缺少 `--tlsv1.3` | 写入时加 `--tlsv1.3` |
| `Connection reset by peer` | TLS 握手失败 | 同上 |
| `invalid_json` | stdin pipe 中文乱码 | 用 `--data-binary @/file.json` |
| 400 `名称 is not a property` | 用错字段名 | 数据库用 `Name`，不是 `名称` |
| 只读到 1 个 block | 模板是 synced_block | 读 `child_page` (`375cd9aa…`) 的 children |
| 404 on synced_block children | synced_block children 不可直接访问 | 改用 `child_page` 下的结构 |
| 空 to_do plain_text 为 `''` | 判断非空需 `txt.strip()` | `bool(txt)` 不够 |
| `Error parsing JSON body` | shell `-d '...'` 中文转义失败 | 用 Python写 JSON 文件再 `--data-binary @/file` |

---

# 日记创建 · 已验证输出（2026.6.7）

## 昨天未完成 To Do（5项）

从昨天日记（`375cd9aa-41cc-81c5-a2b1-fe098d9d34ac`）的「📋 To Do」区提取 `checked=false` 且正文非空：

```
✅ Have Done List（from昨天ToDo）：
[ ] 人工智能训练师
[ ] 梅放转账继续follow
[ ] CRS方向？
[ ] 夹心碰面
[ ] 公众号持续
```

## 飞书 Webhook 故障

飞书 Webhook URL（`https://open.feishu.cn/open-apis/bot/v2/hook/xxx`）已失效：
- 错误码：`19001`
- 错误信息：`param invalid: incoming webhook access token invalid`
- 影响：日记创建后的飞书通知无法推送
- 处理：需要重新配置有效的飞书机器人 Webhook 地址
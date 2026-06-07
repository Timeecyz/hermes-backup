---
name: notion
description: "Notion API via curl: pages, databases, blocks, search."
version: 1.0.0
author: community
license: MIT
metadata:
  hermes:
    tags: [Notion, Productivity, Notes, Database, API]
    homepage: https://developers.notion.com
prerequisites:
  env_vars: [NOTION_API_KEY]
  status: 已验证可用
  pitfalls:
    - label: 关联数据库（Linked Database / Multi-factory Table）
      description: |
        当一个 database 的 `data_sources` 字段非空时，该 database 是「关联数据库」。
        此时 `/databases/{id}` 返回的 `properties` 为空字典，`/databases/{id}/query` 返回 400 "invalid_request_url"。
        底层 source DB 可能未对该 integration 共享权限，表现为 404 "object_not_found"。
      workaround: |
        让用户在 Notion 页面内新建一个普通的 inline Table（不是关联的），Agent 可正常读写。
        操作方式：斜杠命令 → Table - Inline → 命名 → 添加字段。
    - label: 数据库 ID vs 页面 ID 区分
      description: |
        Notion API 中 32位无连字符字符串 = database ID；带连字符标准格式 = page ID。
        如果 `/pages/{id}` 返回 "is a database, not a page"，说明传入的是 database ID，应使用 `/databases/{id}`。
    - label: 关联数据库的两个 ID（data_source_id vs database_id）
      description: |
        当 database 有 `data_sources` 非空字段时（即 Notion 内的「关联数据库 / Linked Table」），
        `/databases/{id}` 返回的 `properties` 为空字典——这不是权限问题，是数据模型的正常表现。
        该 database 实际有两个 ID：
          - `database_id`（API URL 中使用的原始 ID）
          - `data_source_id`（位于 `data_sources[0].id`，36字符带连字符）
        查询关联数据库必须用 `data_source_id`：
          POST /v1/data_sources/{data_source_id}/query
        创建页面时 parent 仍用 `database_id`。
        ⚠️ 陷阱：`data_source_id` 不在 `parent.data_source_id`，而在 `data_sources[0].id`。
          直接查 `parent.data_source_id` 会 KeyError。
      workaround: |
        步骤：先 GET /databases/{database_id}，从响应 parent 对象里提取 data_source_id，
        然后查询时用 POST /v1/data_sources/{data_source_id}/query。不需要改结构。
    - label: 数据库查询请求 body 格式
      description: |
        POST /databases/{id}/query 的 request body 必须是 JSON 编码的 bytes，
        Content-Type: application/json，method 必须明确指定为 POST。
    - label: child_database blocks 仅有 id 和 title
      description: |
        读取页面 children 时，`child_database` 类型的 block 不显示字段详情。
        要获取数据库完整 schema，必须单独调用 GET /databases/{id}。
---

# Notion API

Use the Notion API via curl to create, read, update pages, databases (data sources), and blocks. No extra tools needed — just curl and a Notion API key.

## Prerequisites

1. Create an integration at https://notion.so/my-integrations
2. Copy the API key (starts with `[NOTION_TOKEN]` or `secret_`)
3. Store it in `~/.hermes/.env`:
   ```
   NOTION_API_KEY=[NOTION_TOKEN]
   ```
4. **Important:** Share target pages/databases with your integration in Notion (click "..." → "Connect to" → your integration name)

## API Basics

All requests use this pattern:

```bash
curl -s -X GET "https://api.notion.com/v1/..." \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json"
```

The `Notion-Version` header is required. This skill uses `2025-09-03` (latest). In this version, databases are called "data sources" in the API.

## Common Operations

### 常用块类型

| type | 用场 |
|------|------|
| paragraph | 正文段落 |
| heading_1/2/3 | 标题 |
| bulleted_list_item | 列表 |
| image | 配图（external/file） |
| divider | 分隔线 |
| callout | 高亮框 |
| code | 代码块 |

### ⚠️ 配图插入限制（重要）
Notion API `append_children` 只能在页面**末尾追加**，无法插入到中间位置。

- 图片附加后排在所有文字内容之后
- 如需图片在特定章节，需在 Notion 界面内手动拖拽调整顺序
- 章节配图最佳实践：先确认文字结构，再决定是「末尾追加后拖拽」还是「直接写入 Notion 手动排版」

### Search

```bash
curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"query": "关键词"}' | jq '.results[] | {id: .id, title: (.properties.Name.title[0].text.content // null)}'
```

> ⚠️ 注意：如果搜索结果为空或 `results: null`，不代表没有数据，可能是集成没有共享该页面。Linked Database 场景另见 `references/notion-linked-db.md`。

### Get Page

```bash
curl -s "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03"
```

### Get Page Content (blocks)

```bash
curl -s "https://api.notion.com/v1/blocks/{page_id}/children" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03"
```

### Create Page in a Database

```bash
curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"database_id": "xxx"},
    "properties": {
      "Name": {"title": [{"text": {"content": "New Item"}}]},
      "Status": {"select": {"name": "Todo"}}
    }
  }'
```

### Query a Database

```bash
curl -s -X POST "https://api.notion.com/v1/data_sources/{data_source_id}/query" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {"property": "Status", "select": {"equals": "Active"}},
    "sorts": [{"property": "Date", "direction": "descending"}]
  }'
```

### Create a Database

```bash
curl -s -X POST "https://api.notion.com/v1/data_sources" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"page_id": "xxx"},
    "title": [{"text": {"content": "My Database"}}],
    "properties": {
      "Name": {"title": {}},
      "Status": {"select": {"options": [{"name": "Todo"}, {"name": "Done"}]}},
      "Date": {"date": {}}
    }
  }'
```

### Update Page Properties

```bash
curl -s -X PATCH "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"properties": {"Status": {"select": {"name": "Done"}}}}'
```

### Add Content to a Page

```bash
curl -s -X PATCH "https://api.notion.com/v1/blocks/{page_id}/children" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "children": [
      {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Hello from Hermes!"}}]}}
    ]
  }'
```

## Property Types

Common property formats for database items:

- **Title:** `{"title": [{"text": {"content": "..."}}]}`
- **Rich text:** `{"rich_text": [{"text": {"content": "..."}}]}`
- **Select:** `{"select": {"name": "Option"}}`
- **Multi-select:** `{"multi_select": [{"name": "A"}, {"name": "B"}]}`
- **Date:** `{"date": {"start": "2026-01-15", "end": "2026-01-16"}}`
- **Checkbox:** `{"checkbox": true}`
- **Number:** `{"number": 42}`
- **URL:** `{"url": "https://..."}`
- **Email:** `{"email": "user@example.com"}`
- **Relation:** `{"relation": [{"id": "page_id"}]}`

## Key Differences in API Version 2025-09-03

- **Databases → Data Sources:** Use `/data_sources/` endpoints for queries and retrieval
- **Two IDs:** Each database has both a `database_id` and a `data_source_id`
  - Use `database_id` when creating pages (`parent: {"database_id": "..."}`)
  - Use `data_source_id` when querying (`POST /v1/data_sources/{id}/query`)
- **Search results:** Databases return as `"object": "data_source"` with their `data_source_id`

### Notion Database Access Diagnostic

Run this to audit which databases an integration can access:
```bash
curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Notion-Version: 2022-06-28" \
  -d '{"filter": {"value": "database", "property": "object"}}' | python3 -c "
import sys,json
d=json.load(sys.stdin)
for r in d.get('results',[]):
    title=''.join(t['plain_text'] for t in r.get('title',[])) or '（无标题）'
    pid=r.get('id')
    print(f'  [{pid}] {title}')
"

## API Patterns Reference

A comprehensive Python/urllib pattern reference for block writes, page queries, and data source operations is maintained at `references/api-patterns.md`. Key patterns covered:

- **Python urllib wrapper** with SSL context workaround (avoids the `execute_code` SSL issue)
- **Batch append** with chunk size ≤5 and `time.sleep(1.5)` rate limit
- **Block type examples** for heading, bulleted_list_item, paragraph
- **HTTPError handling** via `.read().decode()` (not bare `str(e)`)
- **Rate limit** guidance: 30 req/s hard cap, 1.5s between chunks is safe

## Known Pitfalls

### TLS/SSL: Always use `--tlsv1.3` for block writes
Block writes (PATCH to `/blocks/{id}/children`) fail with `Connection reset by peer` or `invalid_request_url` in this environment unless curl uses TLS 1.3. Page creation (POST to `/pages`) works fine with default TLS. **Fix**: always add `--tlsv1.3` flag to curl when writing/appending blocks.

### Shell JSON body corruption (Error parsing JSON body / invalid_json)
Chinese text and special characters in JSON bodies passed via `-d '...'` shell strings cause silent JSON parse failures. **Always write payload to a temp `.json` file first**: `python3 -c "import json; print(json.dumps(payload))" > /tmp/req.json && curl ... -d @/tmp/req.json`. Never pipe JSON through stdin to curl.

### `annotations` in block rich_text causes validation_error
Notion API rejects `annotations` fields inside `rich_text[0].text.annotations` when creating blocks via `PATCH /blocks/{id}/children`. Error: `"body failed validation: body.children[0].bulleted_list_item.rich_text[0].text.annotations should be not present"`. **Fix**: Remove all `annotations` objects from block rich_text arrays before appending.

### Page ID must be full 36-char UUID (not URL-safe 32-char)
Calling `PATCH /v1/blocks/{page_id}/children` with a truncated or URL-safe ID (e.g., `373cd9aa41cc8191`) returns `validation_error: path.block_id should be a valid uuid`. **Always obtain the full UUID with dashes via `POST /v1/search`**, not by stripping dashes from URL IDs. URL-safe IDs like `35ccd9aa41cc80f2b550e111aeceb6bd` must never be used directly in API paths.

### Database ID from URL (URL-safe format) cannot be used directly in API calls
The ID in a Notion share URL is URL-safe (e.g., `35ccd9aa41cc80f2b550e111aeceb6bd` — no dashes, 32 chars). API calls require UUID-with-dashes format. **You cannot convert by inserting dashes** — the mapping is not direct. **Always obtain the correct UUID via `POST /v1/search`**, then use the `id` field from the search result (which returns the correct 36-char UUID with dashes).

This also applies to databases: calling `GET /databases/{url_safe_id}` or `POST /databases/{url_safe_id}/query` returns validation errors. Use `/search` to find the database and get its correct `id`.

### Unknown database schema (properties field name)
If you don't know a database's field names, create a test page manually in Notion then read it back via `GET /pages/{id}` — the `properties` keys in the response are the exact field names the API needs. Do not guess `Name` vs `title` vs `标题`.

### Use `--data-binary @/file.json`, never stdin pipe
Shell stdin pipes (`| json`) can silently corrupt JSON (especially newlines in Chinese text). Always write the payload to a temp file first, then use `--data-binary @/tmp/notion_req.json`.

### Batch size: 5 blocks, not 20
Write blocks in batches of ≤5 with retries. Batches of 20+ have high failure rates on this connection. On failure, wait 2s and retry up to 3 times.

### Verified block-write approach (this environment)
Use subprocess curl — do NOT use Python urllib for block writes (SSL context issues cause EMPTY responses with no error):
```python
def append_blocks(page_id, blocks, token):
    import subprocess, json
    payload = json.dumps({"children": blocks}).encode()
    r = subprocess.run(
        ["curl", "-s", "-X", "PATCH",
         f"https://api.notion.com/v1/blocks/{page_id}/children",
         "-H", f"Authorization: Bearer {token}",
         "-H", "Notion-Version: 2022-06-28",
         "-H", "Content-Type: application/json",
         "--tlsv1.3",  # required — connection resets without this
         "-d", payload],
        capture_output=True, text=True, timeout=60
    )
    if not r.stdout.strip():
        return "EMPTY"
    d = json.loads(r.stdout)
    if not d.get("results"):
        return f"ERR:{d.get('code','')}"
    return f"OK({len(d['results'])} blocks)"
```
Always batch ≤5 blocks, sleep 1s between calls. On EMPTY, retry up to 3x before reporting failure.

### PDF生成工作流（已验证）
遇到PDF需求 → 先写本地.md → 存Notion → 通知用户「Notion可导出PDF」
原因：这个环境无 reportlab/weasyprint/pandoc，无法直接生成PDF

## 账单写入 Notion（月度收支汇总）
See `references/wechat-alipay-bill-to-notion.md` — 含微信/支付宝账单解析、分类逻辑、写入 child_page 页面、删除 block 的完整脚本。

## 蛮子定制工作流
Some template pages are a `child_page` block containing a `synced_block` (type: `synced_block`, `has_children: true`, `synced_from: null`). The template content lives in that synced_block's children. Always read two levels:
1. `GET /blocks/{template_page_id}/children` → get the synced_block ID
2. `GET /blocks/{synced_block_id}/children` → get the actual template blocks

### Database field names: use internal names, not display names
The API uses internal field identifiers (e.g., `Name`, `Date`), not display names (e.g., `名称`, `日期`). Always inspect the database schema first with `GET /databases/{id}` to get correct field names.

### Rich text link extraction
When copying rich_text from API responses, check `t.get('type') == 'text'` and `t.get('text', {}).get('link')` separately — the `link` is nested inside the `text` object, not at the top level of the rich_text item.

### `synced_block` children are NOT returned by default
`GET /blocks/{page_id}/children` does NOT recursively fetch content inside `synced_block` children. If a block has `type: "synced_block"` with `synced_block.synced_from: null` and `has_children: true`, you MUST make a second call to `GET /blocks/{synced_block_id}/children` to get the actual block content. The `synced_from` field may be `null` even for template synced_blocks — `has_children: true` is the reliable indicator.

### 保存资讯/文章到 Notion（蛮子定制版）

**触发词**：存到 Notion、存入 Notion、保存到笔记、存知识库、这篇存一下

**标准流程：**
1. **先读目标数据库** — 用 `POST /v1/search` 找到目标DB，先读2~3条现有条目，理解蛮子惯用的标签词汇
2. **打标签** — 用文章最核心的概念作为标签，关键信息驱动，不要泛打大词
3. **创建页面** — 写入标题+正文blocks
4. **顶部加原文链接** — 在页面最顶部加一个 callout（icon💡或🔗），写"📎 微信原文"并附上原始链接

**标签体系来源：** 蛮子的标签从她日常提示语中匹配。完整对照表见 `references/蛮子标签体系.md`（含所有DB ID和标签参考）

When writing full articles or long content to Notion via `PATCH /v1/blocks/{page_id}/children`:

1. **Write to local .md file first** — always save the canonical copy as a `.md` file in `~/.hermes/cache/documents/`. Notion API writes are secondary/fallback. Network instability (connection reset by peer) can cause partial writes.
2. **Use Python urllib + SSL context** — `execute_code` environment needs this pattern:
   ```python
   ctx = ssl.create_default_context()
   ctx.check_hostname = False
   ctx.verify_mode = ssl.CERT_NONE
   req = urllib.request.Request(url, data=body, headers=headers, method='PATCH')
   resp = urllib.request.urlopen(req, timeout=20, context=ctx)
   ```
3. **Batch ≤5 blocks per request** — batches of 20+ have high failure rates; 5 blocks per call is reliable.
4. **Sleep 1s between batches** — avoids rate limiting.
5. **Retry on connection errors** — `Connection reset by peer` is transient; retry up to 3 times with 2s delay.
6. **Save .md file on failure** — if Notion write fails, the local .md file is the fallback canonical copy. Report to user: "Notion写入失败，文件已保存至 `~/.hermes/cache/documents/` 可直接复制粘贴到公众号编辑器。"

## Diary Creation Reference
See `references/diary-creation.md` for the complete working script for the 日记 (daily diary) workflow, including the `--tlsv1.3` workaround, batch-size strategy, and synced_block chain traversal.

## 账单写入 Notion（月度收支汇总）
See `references/wechat-alipay-bill-to-notion.md` — 含微信/支付宝账单解析、分类逻辑、写入 child_page 页面、删除 block 的完整脚本。

## Diagnostic Script

## Diagnostic Script

Cron job task: create daily diary page from a template, copy incomplete todos from yesterday.

### Step 1 — Calculate dates

Use Python `datetime` for correct Chinese timezone date math:
```bash
python3 -c "
from datetime import date, timedelta
today = date.today()
yesterday = today - timedelta(days=1)
print('TODAY:', today.strftime('%Y.%-m.%-d'))   # 2026.5.25
print('YESTERDAY:', yesterday.strftime('%Y.%-m.%-d'))
"
```

### Step 2 — Read yesterday's "To Do" block

GET `/v1/blocks/{yesterday_page_id}/children` and filter for `to_do` blocks where `to_do.checked == false`. Build a list to prepend to today's "Have Done List".

### Step 3 — Read template blocks

GET `/v1/blocks/{template_page_id}/children` — clone the entire block array.

### Step 4 — Create today's page

POST `/v1/pages` with parent as the parent page/database, title property set to the date string.

### Step 5 — Batch-append blocks

PATCH `/v1/blocks/{new_page_id}/children`. Notion limits ~100 blocks per request; chunk larger template arrays.

## Common Pitfalls

- **`synced_block` children are NOT returned by default** — `GET /blocks/{page_id}/children` does NOT recursively fetch content inside `synced_block` children. If a block has `type: "synced_block"` with `synced_block.synced_from.reference_id`, you MUST make a second call to `GET /blocks/{reference_id}/children` to get the actual block content. This is the #1 cause of "template reads fine but produces empty pages" bugs.
- **Block type "unsupported"** — some template blocks (e.g. `synced_block`, `template_block`) cannot be created via API. Catch these and skip, or replace with a `paragraph` with the same text.
- **`date` objects are not JSON serializable** — if you manually construct JSON for `json.dumps()` in a Python script, convert date/datetime to strings first. Notion API responses use ISO strings, so this only bites you when writing custom serializers.

## 日记晚间总结流程（管家点评）

除了从模板创建日记，还有另一个独立流程：**读取当日日记并写入管家点评**。详细步骤和完整脚本见 `references/diary-review.md`（包含：查询今日 page_id → 读取 blocks → 解析内容 → 写入点评 blocks）。

关键陷阱：
- **page_id 必须是完整 36 字符 UUID（含 dash）**，不可截断为 8 字符；截断 ID 会导致 `validation_error: path.block_id should be a valid uuid`
- **page_id 必须是完整 36 字符 UUID（含 dash）**，不可截断为 8 字符；截断 ID 会导致 `validation_error: path.block_id should be a valid uuid`
- 空 to_do 的 plain_text 为空字符串 `''`，不是空白字符
- 写入 blocks 必须加 `--tlsv1.3`，每批 ≤5 个
- **DIARY_DB_ID (318cd9aa) 是 linked database（data_sources）**：不能直接 query `/databases/{id}`，必须先 GET `/databases/{id}` 获取 `parent.data_source_id`，然后用 `POST /v1/data_sources/{data_source_id}/query` 查询今日 page；直接调用 databases query 会返回 400 `invalid_request_url`
- Notion-Version 推荐用 `2025-09-03`，部分旧参考脚本写的是 `2022-06-28`，两者均可但推荐统一用前者

## Diagnostic Script

Run this to audit any page's block structure before cloning:

```bash
curl -s "https://api.notion.com/v1/blocks/{PAGE_ID}/children?page_size=100" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" | python3 -c "
import json,sys
d=json.load(sys.stdin)
for b in d.get('results',[]):
    t=b.get('type','?')
    bid=b.get('id','')[:8]
    if t=='synced_block':
        ref=b.get('synced_block',{}).get('synced_from',{}).get('reference_id','?')[:8]
        print(f'  [synced_block] {bid} → reference_id={ref} (needs extra GET)')
    elif t in ('to_do','paragraph','heading_1','bulleted_list_item'):
        txt=''.join(r.get('plain_text','') for r in b.get(t,{}).get('rich_text',[]))[:40]
        print(f'  [{t}] {bid}: {txt}')
    else:
        print(f'  [{t}] {bid}')
"
```

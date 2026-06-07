# Notion API Patterns

> Python + urllib 写入 Notion Block 的可靠模式。无需 SDK。

## 基础写法

```python
import urllib.request, json

TOKEN = "[NOTION_TOKEN]"
def notion(method, url, data=None):
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body,
        headers={"Authorization": f"Bearer {TOKEN}",
                 "Notion-Version": "2025-09-03",
                 "Content-Type": "application/json"}, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode()}
```

## 追加 Block 到页面

```
PATCH https://api.notion.com/v1/blocks/{page_id}/children
Body: {"children": [block, block, ...]}
```

**重要**：
- 每个 block 必须是完整的富文本结构，不能遗漏 `object: "block"` 和 `type` 字段
- Notion 会拒绝已存在的 block（报错 `code: "invalid_block"`），但不会中断整批
- **永远用 `replace_all=True` 抹掉旧块**（避免重复写入）

## 写入模式（经过验证可靠）

```python
import time

def write_blocks(page_id, blocks, chunk_size=5, delay=1.5):
    """分批写入 blocks 到 Notion 页面，避免 30 req/s 限流"""
    for i in range(0, len(blocks), chunk_size):
        chunk = blocks[i:i+chunk_size]
        time.sleep(delay)
        result = notion("PATCH",
            f"https://api.notion.com/v1/blocks/{page_id}/children",
            {"children": chunk})
        if "error" in result:
            print(f"Chunk {i//chunk_size}: ERR {result['error']}")
        else:
            print(f"Chunk {i//chunk_size}: OK ({len(result.get('results',[]))} blocks)")
```

## 常见 Block 类型示例

### heading_2
```python
{"object":"block","type":"heading_2",
 "heading_2":{"rich_text":[{"text":{"content":"标题"}}],"is_toggleable":False}}
```

### bulleted_list_item
```python
{"object":"block","type":"bulleted_list_item",
 "bulleted_list_item":{"rich_text":[{"text":{"content":"内容"}}]}}
```

### paragraph
```python
{"object":"block","type":"paragraph",
 "paragraph":{"rich_text":[{"text":{"content":"内容"}}]}}
```

## 已知限制 / Pitfalls

1. **重复写入**：Notion 不允许同一 block 重复创建。如果 chunk 中有已存在的 block，整批失败并报 `code: "invalid_block"`。用 `replace_all=True` 覆盖是标准解法。
2. **Rate Limit**：30 req/s。分批 + sleep 是最简单可靠的方案。
3. **Token 版本**：Notion-Version 推荐 `2025-09-03`，旧版可能不支持某些新 block type。
4. **HTTPError 处理**：需要 `.read().decode()` 才能拿到错误体，光 `str(e)` 只有状态码。

## 查询页面现有 Block

```
GET https://api.notion.com/v1/blocks/{page_id}/children
```

返回 `{ "results": [...], "has_more": true/false, "next_cursor": "xxx" }`
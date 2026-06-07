# Notion API 实战笔记

## Linked Database（关联数据库）的识别和处理

### 症状
```bash
GET /v1/databases/{id}
# 返回: { "object": "database", "properties": null, "data_sources": [{...}] }
```

### 为什么 properties 为空
当 Notion 数据库是通过「关联另一个数据库」创建的（多维表格/linked database），
API 返回的是**关联层**，不是底层数据表。关联层没有独立的 schema。

### 两种解法

**解法A：找到底层数据库（data_sources.id）**
```python
import uuid
import requests

def get_real_db_id(linked_id: str, api_key: str) -> str:
    """传入32位短ID，返回底层数据库的UUID格式ID"""
    # 转换为标准UUID（Notion API需要36位格式）
    formatted = str(uuid.UUID(hex=linked_id.replace('-', '')))
    resp = requests.get(
        f"https://api.notion.com/v1/databases/{formatted}",
        headers={"Authorization": f"Bearer {api_key}", "Notion-Version": "2025-09-03"}
    )
    db = resp.json()
    if db.get("data_sources"):
        return db["data_sources"][0]["id"]  # 底层真实数据库ID
    return formatted  # 本身就是真实数据库
```

**解法B：直接写父页面的 blocks（推荐，绕过权限问题）**
```bash
PAGE_ID="355cd9aa-41cc-8183-a037-d8150b1875f7"  # 父页面ID（URL中?v=前的部分）
curl -s -X PATCH "https://api.notion.com/v1/blocks/${PAGE_ID}/children" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "children": [
      {
        "object": "block",
        "type": "heading_2",
        "heading_2": {
          "rich_text": [{"text": {"content": "5月收支汇总"}}]
        }
      }
    ]
  }'
```

## 蛮子的数据库

| 用途 | 32位短ID | UUID格式 |
|------|----------|---------|
| 我的财富蓄水池-月度追踪 | `355cd9aa41cc8183a037d8150b1875f7` | `355cd9aa-41cc-8183-a037-d8150b1875f7` |

## 创建页面时的属性名问题

**症状**：`validation_error: XXX is not a property that exists`

**原因**：用错了属性名（中文列名 ≠ API属性名）

**检查步骤**：
1. `GET /v1/databases/{id}` → 看 `properties` 下的 key 名称
2. 常用映射：`Name/标题/title` → `{"title": [...]}`

## ID 格式

| 格式 | 示例 | 用途 |
|------|------|------|
| 32位短ID | `355cd9aa41cc8183a037d8150b1875f7` | Notion URL |
| 36位UUID | `355cd9aa-41cc-8183-a037-d8150b1875f7` | API调用 |

```python
import uuid
def format_id(short: str) -> str:
    return str(uuid.UUID(hex=short.replace('-', '')))
```
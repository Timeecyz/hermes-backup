# Notion Page Creation — Common Pitfalls

## Problem

Creating a workspace-level page directly fails with:
```
"Provide a `parent.page_id` or `parent.database_id` parameter to create a page,
or use a public integration with `insert_content` capability."
```

Notion internal integrations cannot create top-level workspace pages. They must attach to an existing `page_id` or `database_id`.

## Solution: Find a parent page first

```bash
# Step 1: Search for an existing page that can be used as parent
curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"query": "客户档案"}' | jq '.results[0].id'

# Step 2: Use the found page_id as parent
curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"page_id": "PARENT_PAGE_ID"},
    "properties": {
      "title": [{"text": {"content": "新页面标题"}}]
    }
  }' | jq '{id: .id, url: .url}'
```

## Alternative: Use a database as parent

```bash
# Query databases and pick one
curl -s "https://api.notion.com/v1/databases/$DATABASE_ID/query?page_size=5" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03"

# Create page inside a database
curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"database_id": "$DATABASE_ID"},
    "properties": {
      "Name": {"title": [{"text": {"content": "页面标题"}}]}
    }
  }'
```

## Key insight

For 蛮子's use case (client档案), the parent page choice matters:
- Create under an existing "客户档案" page or similar container
- Document the page URL after creation so it can be referenced later
- Memory then stores: `客户名：核心结论，详见Notion（URL）`
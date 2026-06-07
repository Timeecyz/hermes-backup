# Notion Block API — Append vs Replace + Annotation Pitfalls

## Append to existing page (PATCH children) — preferred over page creation

When creating a new page fails (auth, parent_id format issues), append blocks to an **existing known page** instead:

```python
import urllib.request, json, os

NOTION_KEY = os.popen('grep NOTION_API_KEY ~/.hermes/.env | cut -d= -f2').read().strip()
PAGE_ID = '349cd9aa-41cc-80ad-a3f5-ea207dff2e2a'

blocks = [
    {"object": "block", "type": "heading_2",
     "heading_2": {"rich_text": [{"text": {"content": "Section title"}}]}},
    {"object": "block", "type": "paragraph",
     "paragraph": {"rich_text": [{"text": {"content": "Some text"}}]}},
    {"object": "block", "type": "bulleted_list_item",
     "bulleted_list_item": {"rich_text": [{"text": {"content": "Bullet point"}}]}},
]

payload = json.dumps({"children": blocks}).encode("utf-8")
req = urllib.request.Request(
    "https://api.notion.com/v1/blocks/" + PAGE_ID + "/children",
    data=payload,
    method="PATCH",
    headers={"Authorization": "Bearer " + NOTION_KEY,
             "Notion-Version": "2022-06-28",
             "Content-Type": "application/json"}
)
resp = urllib.request.urlopen(req, timeout=15)
result = json.loads(resp.read())
print("Success: " + str(len(result.get("results", []))) + " blocks added")
```

## Critical pitfall: annotations inside PATCH fail silently

```python
# WRONG — annotations cause 400 validation_error
{"object": "block", "type": "paragraph",
 "paragraph": {"rich_text": [{"text": {"content": "text",
               "annotations": {"italic": True}}]}}}

# RIGHT — omit annotations
{"object": "block", "type": "paragraph",
 "paragraph": {"rich_text": [{"text": {"content": "text"}}]}}
```

Error: `body.children[N].paragraph.rich_text[0].text.annotations should be not present, instead was {"italic": true}`

**Fix**: Strip all `annotations` keys from text objects when appending via PATCH.

## Delete/Archive a block (before re-appending)

```bash
NOTION_KEY=$(grep NOTION_API_KEY ~/.hermes/.env | cut -d'=' -f2)
BLOCK_ID="35ccd9aa-41cc-80e7-b2cd-ce6ca772478b"

curl -s -X DELETE "https://api.notion.com/v1/blocks/$BLOCK_ID" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2022-06-28" | jq '{archived: .archived}'
```

## Read blocks

```bash
NOTION_KEY=$(grep NOTION_API_KEY ~/.hermes/.env | cut -d'=' -f2)
PAGE_ID="349cd9aa-41cc-80ad-a3f5-ea207dff2e2a"

curl -s "https://api.notion.com/v1/blocks/$PAGE_ID/children?page_size=100" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2022-06-28" \
  | jq '.results[] | {type, content: (
    if .paragraph then (.paragraph.rich_text | map(.text.content) | join(""))
    elif .heading_2 then .heading_2.rich_text[0].text.content
    elif .bulleted_list_item then .bulleted_list_item.rich_text[0].text.content
    else "[" + .type + "]" end
  )}'
```

## page_id format for 蛮子's workspace

| Page | UUID (no dashes) |
|------|-----------------|
| 头脑琐事便利贴 | `349cd9aa-41cc-80ad-a3f5-ea207dff2e2a` |
| Quick Notes DB | `318cd9aa-41cc-80a2-a014-f82b2e49a671` |
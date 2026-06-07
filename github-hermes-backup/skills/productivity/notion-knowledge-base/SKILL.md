---
name: notion-knowledge-base
description: Notion 知识库存取 — 按关键词读取页面内容，或将内容写入指定页面/新建条目。蛮子的个人知识中枢。
version: 1.0.0
author: Hermes
metadata:
  hermes:
    tags: [Notion, 知识库, 笔记]
    created: 2026-05-22
prerequisites:
  env_vars: [NOTION_API_KEY]
  status: 已验证可用 (2026-05-22)
---

# Notion 知识库

## 已验证的 Notion 页面

| 用途 | Page ID | 说明 |
|------|---------|------|
| Claire 健身计划 | `35ccd9aa41cc8073914eff870e42553c` | 21天刷脂·增肌计划 |
| (待补充) | | |

> 通用搜索：POST /v1/search，传入关键词 query，返回匹配页面列表

## 核心操作

### 1. 按关键词搜索页面

```bash
curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"query": "关键词"}' | jq '.results[] | {id: .id, title: .properties.Name.title[0].text.content}'
```

### 2. 读取页面内容（全部 block）

```bash
PAGE_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
curl -s "https://api.notion.com/v1/blocks/${PAGE_ID}/children?page_size=100" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" | jq '.results[] | {type, content: (...)}'
```

block 类型判断：
- `paragraph` → `.paragraph.rich_text[0].text.content`
- `heading_1/2/3` → `.heading_N.rich_text[0].text.content`
- `bulleted_list_item` → `.bulleted_list_item.rich_text[0].text.content`
- `numbered_list_item` → `.numbered_list_item.rich_text[0].text.content`
- `table` → table 类型需单独获取 children
- `divider` → 跳过

### 3. 向页面追加内容

```bash
PAGE_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
curl -s -X PATCH "https://api.notion.com/v1/blocks/${PAGE_ID}/children" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "children": [
      {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
          "rich_text": [{"text": {"content": "要写入的内容"}}]
        }
      }
    ]
  }'
```

### 4. 在数据库中新建页面

```bash
DATABASE_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"database_id": "'$DATABASE_ID'"},
    "properties": {
      "Name": {"title": [{"text": {"content": "页面标题"}}]}
    }
  }'
```

## 蛮子的使用方式

- **读取**：「从 Notion 读 [关键词]」
- **写入**：「把 [内容] 存到 Notion [关键词/页面名]」
- 所有操作自动使用 `NOTION_API_KEY`，无需每次提供

## 常见问题

- **Page ID 格式**：`35ccd9aa41cc8073914eff870e42553c`（URL）是安全的 ID，但 API 调用需要完整 UUID 格式。详见 `references/page-id-format.md`

- **workspace 页面创建限制**：不能直接用 `parent: {type: workspace}` 创建页面，必须指定 `parent.page_id` 或 `parent.database_id`。解决方案：先找一个已存在的页面作为父页面，或查询一个 database 作为父容器。详见 `references/notion-page-creation.md`

## 注意事项

- Page ID 是 UUID 格式（35ccd9aa41cc8073914eff870e42553c）
- 读取长页面注意分页（page_size 最大 100）
- 写入新内容默认追加到页面底部
- 涉及美国税务/港险等敏感情量息时，需注意 Notion 页面分享权限

## 蛮子专属：记忆管理原则

> **触发条件**：当 memory 使用率 > 85% 时，立即触发本原则。

**原则**：详细客户档案、话术、长文本内容 → Notion；记忆只保留**一句话结论**（成交概率 / 核心障碍 / 下一动作）。

**操作**：
1. 查询目标客户的 Notion 页面（`POST /v1/search` by name）
2. 如果不存在，找一个已有页面作为父级，创建新页面
3. 将详细档案写入 Notion
4. 记忆替换为：`客户名：核心结论，详见Notion（URL）`

**原因**：记忆 2,200 字符硬限制，长档案会挤掉用户偏好、Subagent 信息等真正需要常驻的内容。

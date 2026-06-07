# WeChat Article → Notion Pipeline

## The "不躺平的钱"公众号 Content库

**Database ID (for page creation):** `34acd9aa-41cc-818f-aae0-c6ce9e77036f`
**Data Source ID (for querying):** `34acd9aa-41cc-8134-91bd-000bfc98b4eb`

```
Parent page: "不躺平的钱"公众号内容库
URL: https://www.notion.so/34acd9aa41cc8154a26bece3be7e21ec
```

## Standard Property Map for This Database

| Property | API key | Type | Example |
|----------|---------|------|---------|
| 名称 | `Name` (title) | title | "【热点解读】标题" |
| 状态 | `状态` | select | "待发布" / "已发布" / "草稿" |
| 发布日期 | `发布日期` | date | `{"date": {"start": "2026-05-23"}}` |
| 负责人 | `负责人` | rich_text | "蛮子" |
| 类型 | `类型` | select | "热点解读" / "产品分析" / "话术模板" |
| 标签 | `标签` | multi_select | `[{"name": "港险"}, {"name": "热点"}]` |
| 网址 | `网址` | url | "https://mp.weixin.qq.com/..." |
| 配图 | `配图` | files | (array, optional) |

## Workflow: Push WeChat Article to Notion Draft

### Step 1: Create Page in Database

```python
import json, subprocess

NOTION_KEY = "[NOTION_TOKEN_REDACTED]"
DB_ID = "34acd9aa-41cc-818f-aae0-c6ce9e77036f"

payload = json.dumps({
    "parent": {"database_id": DB_ID},
    "properties": {
        "名称": {"title": [{"text": {"content": "【类型】文章标题"}}]},
        "状态": {"select": {"name": "待发布"}},
        "负责人": {"rich_text": [{"text": {"content": "蛮子"}}]},
        "类型": {"select": {"name": "热点解读"}},
        "标签": {"multi_select": [{"name": "港险"}, {"name": "热点"}]},
        "网址": {"url": "https://..."},
        "发布日期": {"date": {"start": "2026-05-23"}}
    }
})

r = subprocess.run(
    ["curl", "-s", "-X", "POST",
     "https://api.notion.com/v1/pages",
     "-H", f"Authorization: Bearer {NOTION_KEY}",
     "-H", "Notion-Version: 2025-09-03",
     "-H", "Content-Type: application/json",
     "-d", payload],
    capture_output=True, text=True
)
page_id = json.loads(r.stdout)["id"]
```

### Step 2: Append Blocks (after page creation)

```python
def make_block(type_, content, **kwargs):
    rt = [{"type": "text", "text": {"content": content}}]
    if type_ == "heading_2":
        return {"object": "block", "type": "heading_2", "heading_2": {"rich_text": rt}}
    if type_ == "heading_3":
        return {"object": "block", "type": "heading_3", "heading_3": {"rich_text": rt}}
    if type_ == "callout":
        icon = kwargs.get("icon", {"emoji": "💡"})
        return {"object": "block", "type": "callout", "callout": {"rich_text": rt, "icon": icon, "color": "yellow_background"}}
    if type_ == "divider":
        return {"object": "block", "type": "divider", "divider": {}}
    if type_ == "bulleted_list_item":
        return {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": rt}}
    # paragraph
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rt}}

blocks = [
    make_block("callout", "🚨 开头金句 / 核心事件", icon={"emoji": "🚨"}),
    make_block("heading_2", "一、..."),
    make_block("paragraph", "正文..."),
    # ... build all content blocks
]

payload = json.dumps({"children": blocks})
r = subprocess.run(
    ["curl", "-s", "-X", "PATCH",
     f"https://api.notion.com/v1/blocks/{page_id}/children",
     "-H", f"Authorization: Bearer {NOTION_KEY}",
     "-H", "Notion-Version: 2025-09-03",
     "-H", "Content-Type: application/json",
     "-d", payload],
    capture_output=True, text=True
)
print("Blocks added:", len(json.loads(r.stdout).get("results", [])))
```

## Block Type Reference

| Block Type | API Key | Notes |
|------------|---------|-------|
| Paragraph | `paragraph` | Default fallback |
| Heading 1 | `heading_1` | Use sparingly |
| Heading 2 | `heading_2` | Main section headers |
| Heading 3 | `heading_3` | Sub-section headers |
| Bulleted list | `bulleted_list_item` | Separate items = separate blocks |
| Callout | `callout` | Emphasized box; use emoji icon + yellow_background |
| Divider | `divider` | `{"object": "block", "type": "divider", "divider": {}}` |
| Quote | `quote` | For testimonials / citations |
| Image | `image` | Use `{"type": "external", "external": {"url": "..."}}` |

### Callout Colors

- `yellow_background` — key takeaways, warnings
- `red_background` — urgent alerts
- `green_background` — positive/approved
- `blue_background` — informational
- `default` — neutral

## Article Rewriting Guidelines (for "不躺平的钱")

When re-writing a source article for this account, apply these transformations:

| Element | Original | Rewritten |
|---------|----------|-----------|
| Opening | Often sensationalist / fear-driven | Lead with the concrete data point (numbers, dates) |
| Structure | Dense paragraphs | H2 headers + callout boxes + bullet lists |
| Product placement | Hard sell | Embed naturally inside "legitimate channels" framework |
| Closing | Author CTA / QR | End with engagement prompt, then static CTA line |
| Tone | WeChat virality / clickbait | Still engaging but structured — more Notion-friendly |

### Article Type Tags

- `热点解读` — breaking news / market events
- `产品分析` — insurance product deep-dives
- `话术模板` — sales scripts / objection handling
- `客户案例` — anonymized client story
- `学习笔记` — seminar / training notes

## Article Rewriting Guidelines (for "不躺平的钱")

> ⚠️ **重要：发布前必须对照 `viral-article-checklist.md` 自检！**

### Claire 风格核心要素

| 元素 | 要求 |
|------|------|
| 账号名片 | 开头必须放 📌 callout（蓝底）账号介绍块 |
| 标题 | 必须含：数字 + 情绪词 + 受众标签 |
| 结构 | 每个 section 用 【PART X】编号 |
| 人称 | 第一人称 Claire，"说人话" |
| 语气 | 禁止命令句（"你必须…"）；推荐"你可以…" |
| 产品植入 | 自然嵌入合规渠道中，不硬推 |
| 结尾 | 互动引导 → 静态CTA → 原创声明 |

### 禁止出现的内容

- 连续感叹号超过3个
- "毫无疑问"、"毋庸置疑"
- 无来源的股价/政策数据
- 投资建议表述（"建议抄底"等）
- 纯政策文件摘要
- 与原文超过15字连续重复

### 原创度要求

- 核心事实（数字/时间）保留，但描述方式必须独立
- 逻辑结构重组超过50%
- 词汇替换率超过30%
- 每一句都经过"这句话原文是怎么说的？我能不能换一个说法？"

## Troubleshooting

**subprocess JSON error "bytes object has no attribute 'encode'"**
→ Pass payload as string to curl `-d` flag, not bytes. Use `subprocess.run(..., capture_output=True, text=True)` and pass payload string directly. Do NOT use `input=payload` with bytes.

**Page created but blocks fail to append**
→ Page ID is correct from creation response. Use `PAGE_ID` variable and re-run block append in same script.

**Database query returns 0 items**
→ The database has TWO IDs: `database_id` (for creating pages) and `data_source_id` (for querying). Use `data_source_id` in `/data_sources/{id}/query` requests.

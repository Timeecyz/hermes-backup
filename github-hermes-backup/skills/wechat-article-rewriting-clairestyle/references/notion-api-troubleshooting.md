# Notion API 排错：数据库字段与 400 Bad Request

## 本次教训
蛮子的 Quick Notes 数据库（318cd9aa-41cc-80a2-a014-f82b2e49a671）只有以下字段：

| 字段名 | 类型 |
|--------|------|
| Name | title |
| 文件和媒体 | files |
| 人员 | people |
| Tags | multi_select |
| 网址 | status |
| Date | last_edited_time |

**没有：** `状态`、`类型`、`负责人`、`备注`、`金额` 等常见字段。

第一次写入失败（400），是因为我传了数据库里不存在的字段名。

## 正确做法
创建页面之前，先用 `GET /databases/{id}` 查数据库的 properties 类型，只传数据库里真实存在的字段：

```python
db = notion_req(f'/databases/{DB_ID}')
props = db.get('properties', {})
for k, v in props.items():
    print(f"{k}: {v.get('type')}")  # title / rich_text / multi_select / etc.
```

## Notion API 400 常见原因优先级
1. **字段不存在**（本次）→ 先查 `properties` 接口确认字段
2. **parent 格式错误** → `{database_id: "xxx"}` 而非 `{page_id: "xxx"}`
3. **emoji 无效** → callout/icon 的 emoji 要用字符串，不加 emoji picker 语法
4. **block children 分块** → 每批最多 20 条，超过要分多个请求
5. **rich_text 超长** → 每条 rich_text 单元 content ≤ 1000 chars，超出要拆
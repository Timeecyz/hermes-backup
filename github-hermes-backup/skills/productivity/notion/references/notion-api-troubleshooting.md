# Notion API 踩坑笔记

## Database ID 格式：链接 → UUID

当用户发来 Notion 数据库链接时，URL 中的 ID 是 32 位无连字符字符串。

示例：
- 链接中：`349cd9aa41cc80ada3f5ea207dff2e2a`（32位，无dash）
- 还原为标准 UUID 格式：`349cd9aa-41cc-80ada-3f5ea-207dff-2e2a`

转换规则：8-4-4-4-12（第9、14、19、24位后加 `-`）

```python
raw = "349cd9aa41cc80ada3f5ea207dff2e2a"
uuid = f"{raw[:8]}-{raw[8:12]}-{raw[12:16]}-{raw[16:20]}-{raw[20:]}"
# → 349cd9aa-41cc-80ada-3f5ea-207dff-2e2a
```

## 诊断步骤：数据库访问失败

**症状**：直接 GET `/databases/{id}` 返回空或 404。

**排查流程**：
```
1. 用 POST /search + filter {object:database} 列出所有可访问的 DB
2. 找到目标 DB 的正确 ID 和标题
3. 再用正确 ID 查询
```

**注意**：`/search` 返回的 DB 在某些 API 版本中 `object` 类型可能是 `data_source` 而非 `database`。

## Quick Notes 数据库确认

- DB ID: `318cd9aa-41cc-80a2-a014-f82b2e49a671`
- 标题: "Quick Notes移除碎片-净化CPU"
- 字段: Name(title), Tags(multi_select), 网址(url), 人员(people), Date(date), 文件和媒体(files)
- 可用状态：✅ 已验证

## "点滴思考" 页面

- 搜索 "点滴思考" 在 Quick Notes DB 中找到
- 页面 title 字段为空（显示为无标题），但内容标签含 Idea/Personal/Work/Planning/Reminder
- 写入悬案回顾时，标题格式：`【悬案】YYYY.MM.DD 待跟进事项`
- Tags 用：["悬案回顾", "Reminder"]

# Notion 页面 ID 格式转换

## URL vs API UUID

Notion 分享链接有两种格式：

| 格式 | 示例 | 用途 |
|------|------|------|
| **URL-safe (分享链接)** | `35ccd9aa41cc8073914eff870e42553c` | 用户分享时给出 |
| **UUID with dashes (API 用)** | `35ecd9aa-41cc-81e2-8b27-cab38a3edd7b` | API 调用时用 |

**转换规则：** 每 8-4-4-4-12 插入横杠
```
35ccd9aa + 41cc + 8073 + 914e + ff870e42553c
→ 35ecd9aa-41cc-81e2-8b27-cab38a3edd7b
```

**注意：** 不是简单加横杠！上面示例的数字不是直接对应关系，实际以 API 返回的 `/search` 结果中的 `id` 字段为准。

## 推荐的正确流程

1. 用 `POST /v1/search` 按关键词搜，返回结果中取 `id`（带横杠格式）
2. 用返回的 UUID 直接调用 `GET /v1/pages/{id}` 或 `GET /v1/blocks/{id}/children`
3. 不要手动转换 URL ID → UUID，可能不匹配

## 已验证页面

| 页面 | URL ID | API UUID (verified) |
|------|---------|----------------------|
| Claire 健身计划 | `35ccd9aa41cc8073914eff870e42553c` | `35ecd9aa-41cc-81e2-8b27-cab38a3edd7b` |

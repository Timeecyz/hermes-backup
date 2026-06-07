# Notion API — 技术备忘录

## 可靠写入方案：用 curl（subprocess）而非 urllib

Python `urllib.request.urlopen` 对 Notion API 的 PATCH 写入极不稳定，
表现为连接重置（`Connection reset by peer`）或 400 Bad Request，
即使 retries 足够也会间歇性失败。

**已验证可靠方案**：
```python
import subprocess, json

def run_notion(url, payload, method='POST'):
    with open('/tmp/notion_req.json', 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    result = subprocess.run([
        'curl', '-s', '-X', method, url,
        '-H', f'Authorization: Bearer {NOTION_TOKEN}',
        '-H', 'Notion-Version: 2022-06-28',
        '-H', 'Content-Type: application/json; charset=utf-8',
        '--data-binary', '@/tmp/notion_req.json',
        '--tlsv1.3'
    ], capture_output=True, text=True)
    return json.loads(result.stdout.strip())
```

关键参数：`--tlsv1.3`（TLS 1.3 强制），`--data-binary @/tmp/notion_req.json`（避免 shell 转义）。

## 模板 block 数量动态增长

| 日期 | synced_block 子 blocks 数 |
|------|--------------------------|
| 2026-06-03 | 100 |
| 2026-06-04 | 126 |

**不要硬编码 block 数量**，每次执行必须 `GET /blocks/{synced_id}/children` 实时读取。

## block_to_dict 处理规范

以下字段在写入时必须剔除（会导致 400）：
- `id`
- `synced_from`
- `created_by` / `last_edited_by`
- `created_time` / `last_edited_time`
- **`icon: null`**（尤其 paragraph / callout / to_do / bulleted_list_item）

## 批量写入上限

- 单批 ≤20 blocks；推荐 10 blocks/批
- 每批间隔 1-2 秒
- PATCH 后验证 `'results' in response`

## 数据库查询注意

- 字段名：`发送日期`（不是 `Date`）
- 日期格式：`YYYY-MM-DD`（ISO 格式）
- 不要用 search API（在本 integration 下始终返回 0 结果）
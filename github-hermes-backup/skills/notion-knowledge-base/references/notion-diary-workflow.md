# Notion 日记工作流 — 经验积累

## 本次任务执行记录

**日期**: 2026.05.29
**任务**: 生成当日日记（定时任务 06:45）
**结果**: ✅ 成功 — 61个模板子块全部写入新页面

---

## 关键发现

### 1. API 连接稳定性
- `urllib` + `urlopen` 在高频调用时出现 `Connection reset by peer`
- `curl` subprocess 调用更稳定，成功率更高
- **解决方案**: 切换到 `subprocess.run(['curl', ...])` 方式调用 Notion API

### 2. 批量写入失败，单条写入成功
- PATCH `/blocks/{page_id}/children` 批量写入（10条/批）在第1批之后就大量失败
- 单条写入逐个调用，每次间隔 2.5s，全部成功
- **结论**: Notion API 对批量写入有严格限流，必须降速单条写入

### 3. `paragraph.icon: null` 验证错误
- 模板中的段落 block 包含 `"icon": null`
- Notion API PATCH 时拒绝 `null` 值，要求是 object 或 `undefined`
- **解决方案**: 写入前删除 `icon: null` 字段

### 4. To Do 区块处理
- 模板中 to_do 的 rich_text 不搬迁（按设计要求）
- 全部写为 `checked: false, rich_text: []` 的空 checkbox

---

## 飞书通知失败

- Webhook URL: `https://open.feishu.cn/open-apis/bot/v2/hook/875c6867-1c31-4dba-b423-9175f8873880`
- 错误: `code:19001, msg: "param invalid: incoming webhook access token invalid"`
- **原因**: 飞书机器人 Webhook access token 无效，需重新配置

---

## API 调用参数

```
NOTION_TOKEN = [NOTION_TOKEN_REDACTED]
DATABASE_ID = 318cd9aa-41cc-8098-803e-ed230c9c7e80
TEMPLATE_PAGE_ID = 34acd9aa-41cc-8194-8639-cae39559b759
SYNCED_BLOCK_ID = 368cd9aa-41cc-8098-bbe7-e149040545e9
New Page ID: 36ecd9aa-41cc-8120-b332-d46f5a657497
```

---

## 推荐的 Python 脚本模式

```python
import subprocess, json, time

NOTION_TOKEN = "[NOTION_TOKEN]"
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def curl_get(url, retries=3):
    for attempt in range(retries):
        r = subprocess.run(['curl', '-s', '-H', f'Authorization: Bearer {NOTION_TOKEN}',
            '-H', 'Notion-Version: 2022-06-28', url, '--max-time', '25'],
            capture_output=True, text=True, timeout=30)
        if r.stdout: return json.loads(r.stdout)
        time.sleep(3)
    return None

def curl_patch(url, body, retries=5):
    for attempt in range(retries):
        r = subprocess.run(['curl', '-s', '-X', 'PATCH',
            '-H', f'Authorization: Bearer {NOTION_TOKEN}',
            '-H', 'Notion-Version: 2022-06-28',
            '-H', 'Content-Type: application/json',
            '-d', json.dumps(body), url, '--max-time', '25'],
            capture_output=True, text=True, timeout=30)
        if r.stdout:
            result = json.loads(r.stdout)
            if result.get('object') == 'error':
                print(f"  Error: {result.get('message')}")
            else:
                return result
        time.sleep(3)
    return None

# Clean block: remove null icon before writing
def clean_block(b):
    t = b['type']
    c = dict(b.get(t, {}))
    if c.get('icon') is None: del c['icon']
    if c.get('color') is None: c['color'] = 'default'
    if t == 'to_do':
        c['checked'] = False
        c['rich_text'] = []
    return {"type": t, t: c}
```
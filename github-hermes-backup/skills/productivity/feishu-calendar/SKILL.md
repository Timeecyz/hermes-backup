---
name: feishu-calendar
description: 飞书日历读写 — 查询、创建、管理日程。当蛮子说"查日历"、"加日程"、"打通飞书日历"时触发。
version: "1.0.0"
credentials:
  - name: FEISHU_APP_ID
    description: 飞书应用 App ID（已在 ~/.hermes/.env）
  - name: FEISHU_APP_SECRET
    description: 飞书应用 App Secret（已在 ~/.hermes/.env）
---

# feishu-calendar

**触发词：** 查日历、加日程、查日程、打通飞书日历、飞书日历

## 凭证速查（已配置，无需再问）

| 字段 | 值 |
|------|-----|
| App ID | cli_aa9abc638cf91bb4 |
| App Secret | 2anV19EgpXL3r14ITxgoug2yatBn2eut |
| 应用权限 | 日历读写（需在飞书开放平台开启 calendar权限） |
| 蛮子日历 ID | feishu.cn_5GEgXsatRydgAX8tDqxbtd@group.calendar.feishu.cn（primary，owner） |

## API 认证 — 必须用 tenant_access_token

飞书日历 API 用 **tenant_access_token**（不是 user_access_token），通过 `POST /open-apis/auth/v3/tenant_access_token/internal` 获取。

```python
import requests

r = requests.post(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={"app_id": "cli_aa9abc638cf91bb4", "app_secret": "2anV19EgpXL3r14ITxgoug2yatBn2eut"}
)
tenant_token = r.json()['tenant_access_token']
```

## 核心操作模板

### 查询某日日程

```python
import requests, datetime, time

CAL_ID = "feishu.cn_5GEgXsatRydgAX8tDqxbtd@group.calendar.feishu.cn"
today = datetime.datetime.today()
start_ts = int(time.mktime(today.replace(hour=0, minute=0, second=0).timetuple()))
end_ts = int(time.mktime(today.replace(hour=23, minute=59, second=59).timetuple()))

url = f"https://open.feishu.cn/open-apis/calendar/v4/calendars/{CAL_ID}/events"
params = {"start_time": start_ts, "end_time": end_ts, "page_size": 50}
r = requests.get(url, params=params, headers={"Authorization": "Bearer " + tenant_token})
items = r.json()['data']['items']
for e in items:
    st = str(e.get('start_time', ''))
    et = str(e.get('end_time', ''))
    print(f"  {st[:16]} - {et[:16]} | {e.get('summary', '(无标题)')}")
```

### 创建日程

```python
import requests, datetime, time

CAL_ID = "feishu.cn_5GEgXsatRydgAX8tDqxbtd@group.calendar.feishu.cn"
start = datetime.datetime(2026, 6, 10, 10, 0)
end = datetime.datetime(2026, 6, 10, 11, 0)

payload = {
    "summary": "蛮子客户会议",
    "start_time": {"timestamp": str(int(time.mktime(start.timetuple()))), "timezone": "Asia/Shanghai"},
    "end_time": {"timestamp": str(int(time.mktime(end.timetuple()))), "timezone": "Asia/Shanghai"},
}
r = requests.post(
    f"https://open.feishu.cn/open-apis/calendar/v4/calendars/{CAL_ID}/events",
    json=payload,
    headers={"Authorization": "Bearer " + tenant_token}
)
print(r.json())
```

## 已知坑

1. **page_size 最小值 50**：查询日程时 `page_size` 不能小于 50，否则报 99992402 validation failed
2. **时间格式用 Unix timestamp**：飞书日历 API 用秒级 Unix 时间戳，不是 ISO 字符串
3. **calendar_id 含特殊字符**：主日历 ID 含 `@group.calendar.feishu.cn`，直接放 URL 路径中无需额外编码（requests 库自动处理）
4. **tenant_access_token有效期 2 小时**：需要每次调用前重新获取

## 相关技能

- `working-playbook`：蛮子协作工作流，日历数据用于每日提醒
- `notion`：日历事件可同步存入 Notion 记录
# Feishu Calendar API — Known Quirks

**Last verified: 2026-06-07**

---

## page_size Minimum: 50

Feishu Calendar event list API requires `page_size >= 50`. Values below 50 return:

```json
{"code": 99992402, "msg": "field validation failed",
 "error": {"field": "page_size", "description": "the min value is 50"}}
```

**Fix:** Always use `page_size=50` (never20).

---

## Calendar ID Format

The `calendar_id` for the primary calendar has special characters (`@`, `.calendar.feishu.cn`). Pass it as-is in the URL path — URL-encoding `@` as `%40` is NOT needed and actually causes 400.

```python
CAL_ID = "feishu.cn_5GEgXsatRydgAX8tDqxbtd@group.calendar.feishu.cn"
# Use directly — requests handles the @ correctly
requests.get(f"https://open.feishu.cn/open-apis/calendar/v4/calendars/{CAL_ID}/events", ...)
```

---

## Token: Tenant Access Token (not User Token)

Calendar API uses tenant access token (from app credentials), NOT user token. Get it via:

```python
requests.post(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={"app_id": APP_ID, "app_secret": APP_SECRET}
).json()['tenant_access_token']
```

Token expires in 2 hours — refresh before each session.

---

## Primary Calendar Discovery

If `calendar_id` is unknown, list all calendars first:

```
GET https://open.feishu.cn/open-apis/calendar/v4/calendars
```

The primary calendar has `role: "owner"` and typically contains "Hermes" in the summary name.

---

## Get Today's Events

```python
import requests, datetime, time

APP_ID = "..."
APP_SECRET = "..."

# Get token
r = requests.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={"app_id": APP_ID, "app_secret": APP_SECRET})
token = r.json()['tenant_access_token']

CAL_ID = "feishu.cn_XXXXXXXX@group.calendar.feishu.cn"
today = datetime.datetime.today()
start_ts = int(time.mktime(today.replace(hour=0, minute=0, second=0).timetuple()))
end_ts = int(time.mktime(today.replace(hour=23, minute=59, second=59).timetuple()))

r2 = requests.get(
    f"https://open.feishu.cn/open-apis/calendar/v4/calendars/{CAL_ID}/events",
    params={"start_time": start_ts, "end_time": end_ts, "page_size": 50},
    headers={"Authorization": "Bearer " + token}
)
items = r2.json()['data']['items']
for e in items:
    print(e['start_time'][:16], "-", e.get('summary', '(无标题)'))
```
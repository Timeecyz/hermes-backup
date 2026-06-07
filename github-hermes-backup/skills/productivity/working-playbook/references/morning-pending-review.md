# 晨报悬案回顾 — 工作流文档

## 触发条件

cron job（工作日早6:30或6:45）自动执行，扫描昨天蛮子所有对话，识别未完成事项。

## 数据来源

**Hermes state.db（会话历史）**

路径：`/home/agentuser/.hermes/state.db`

关键表：
- `sessions` — 会话元数据（id, started_at, ended_at, end_reason, message_count）
- `messages` — 消息内容（session_id, role, content, timestamp）

**注意**：`session_search` 工具在 cron 环境下不可用，必须直接查库。

## Step-by-Step 执行流程

### Step 1：查最近3天会话列表

```python
import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('/home/agentuser/.hermes/state.db')
cur = conn.cursor()

three_days_ago = (datetime.now() - timedelta(days=3)).timestamp()
cur.execute("""
    SELECT id, started_at, title, message_count, end_reason
    FROM sessions
    WHERE started_at > ?
    ORDER BY started_at DESC
""", (three_days_ago,))
```

过滤条件：
- 排除 cron session（id 以 `cron_` 开头），保留真实用户对话
- 重点关注昨天白天用户主动发起的 session

### Step 2：拉取用户消息

```python
cur.execute("""
    SELECT session_id, role, content, timestamp
    FROM messages
    WHERE session_id IN (?, ?, ...)
    AND role = 'user'
    ORDER BY session_id, timestamp
""", target_sessions)
```

### Step 3：识别悬案信号

关键词扫描（在用户 content 中）：
- `未完成`、`待办`、`之后再说`、`回头再聊` — 聊到一半
- `记一下`、`存一下`、`帮我` — 需要跟进的承诺
- 链接类（notion.so、feishu.cn、mp.weixin.qq.com）— 可能是未完成的任务引用
- 任务句式：`处理任务`、`帮我做`、`你可以...吗`

### Step 4：分类整理

| 状态 | 含义 |
|------|------|
| 待决策 | 蛮子还没拍板，需要确认方向 |
| 待执行 | 方案已定，等执行 |
| 待确认 | 不确定是否已完成，需验证 |
| 待更新skill | 蛮子明确要求固化到skill |

### Step 5：写入 Notion Quick Notes DB

**DB ID**：`318cd9aa-41cc-80a2-a014-f82b2e49a671`

**注意**：该 DB 是「关联数据库」，有两个 ID：
- `database_id`（创建页面时用）：`318cd9aa-41cc-80a2-a014-f82b2e49a671`
- `data_source_id`（查询时用）：`318cd9aa-41cc-81d3-afa8-000b54e7d381`

页面 title 格式：`【悬案】YYYY.MM.DD 待跟进事项`
Tags：`["悬案回顾", "Reminder"]`

### Step 6：输出晨报摘要

格式：
```
🌅 蛮子，早上好！
昨天我们聊到一半的事，帮你整理好了：

📌 待跟进（N条）
1. [事项] — [状态/来源]

💡 今天可以顺手处理的：
- ...

已存入 Notion Quick Notes ✅
📎 [URL]
```

## 已知 Notion API 陷阱

见 `notion` skill — 关联数据库的 data_source_id vs database_id 区别。

## Notion Quick Notes DB 字段（实测）

| 字段 | type | 用途 |
|------|------|------|
| Name | title | 页面标题 |
| Tags | multi_select | Tags |
| Date | last_edited_time | — |
| 网址 | status | URL 字段 |
| 人员 | people | — |
| 文件和媒体 | files | — |
| 上次编辑时间 | last_edited_time | — |
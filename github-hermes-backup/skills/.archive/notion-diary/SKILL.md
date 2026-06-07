---
name: notion-diary
description: Notion 日记系统 — 生成当日日记、同步未完成项、读写 Notion API
trigger: 读取/写入 Notion 页面 | 生成日记/日报 | Notion API 调用 | 日记模板复制
---

# Notion 知识库 · 日记系统

## 触发场景
当用户提到以下任何一项时使用：
- 读取/写入 Notion 页面
- 生成日记/日报/周报
- Notion API 调用
- 日记模板复制

## 核心能力
- 通过 Notion API 读写页面 blocks
- 搜索页面（按标题/数据库）
- 复制日记模板结构
- 跨日 To Do 同步

## 凭证与环境
- API Key: `[NOTION_TOKEN_REDACTED]`
- 模板页 ID: `34acd9aa-41cc-8194-8639-cae39559b759`
- synced_block 实际含 **100 个子 blocks**（2026-06-03 验证）
- 日记数据库 ID: `318cd9aa-41cc-8098-803e-ed230c9c7e80`
- 日记数据库 Date 字段名：**`发送日期`**（2026-06-01 验证）
- 模板 synced_block 实际含 **100 个子 blocks**（2026-06-03 验证，非 61 个）

## 重要架构发现
模板页本身的直接子块只有一个 `synced_block` 子块；日记模板的 blocks 嵌套在该 synced_block 内。
读取模板的正确路径：
1. `GET /blocks/{模板页ID}/children` → 获取 synced_block ID
2. `GET /v1/blocks/{synced_block_id}/children` → 返回实际的 blocks

**实测数据**：
- 2026-06-03：模板 synced_block 含 100 个子 blocks
- 2026-06-04：模板 synced_block 含 126 个子 blocks（`368cd9aa-41cc-8098-bbe7-e149040545e9`）
- 结论：模板内容会动态增长，必须实时读取，不能硬编码 block 数量
## 晚间日记总结（22:00 cron）
**目标**：读取当日日记 → 生成管家点评 → 写入 Notion → 推送飞书

**步骤**：
1. 用数据库 date filter 查询今日页面（字段名 `发送日期`，格式 `YYYY-MM-DD`）
2. 读取所有 blocks（过滤 to_do 的 checked 状态、paragraph 文本）
3. 统计：Have Done 完成数、To Do 勾选数、17项打卡完成数、饮食/运动/睡眠记录
4. 生成管家点评（见下方格式）
5. **追加 blocks 到日记页**（格式见 API 参考，注意必须用 `{"children": [...]}` 包装）
6. 发送飞书通知

**管家点评格式**：
```
🌙 今日管家点评
[鼓励话语，50-100字，要有温度，发现亮点就夸，不说教]

💡 明日建议
• 建议1
• 建议2
```

### 飞书推送（晚间总结）
使用已配置的 Feishu App（`FEISHU_APP_ID` / `FEISHU_APP_SECRET` 在 `~/.hermes/.env`）：
1. `POST /auth/v3/tenant_access_token/internal` 获取 token
2. `POST /im/v1/messages?receive_id_type=open_id` 发送文本消息
   - `receive_id`：从 `FEISHU_ALLOWED_USERS` 读取（格式 `ou_xxx`）
   - `msg_type`: `text`，`content`: `{"text": "..."}`

## 推荐工作流：生成当日日记（cron 06:45）
1. 计算今日日期（如 `2026.5.30`）
2. **查询数据库是否已存在今日页面**（Date filter 查询）：
   - 如已存在，打印「已生成」并跳过创建，直接发通知
   - 如不存在，继续步骤 3
3. **创建今日页面**（数据库母级，属性含 Date/Name/Tags）
4. 读取模板 blocks（走 synced_block 两层路径）
5. **清理 icon: null** 的 paragraph blocks（防止 400 错误）
6. 批量追加 blocks（每批 ≤10，间隔 1-2 秒，失败重试一次）
7. 发送飞书通知（如已配置 webhook）

## 昨天→今天的 To Do 同步逻辑
**目标**：昨天 To Do 区 checked=false 的项，追加到今天 Have Done List 区。

**实现步骤**：
1. ~~搜索昨天的日记页~~（search API 在本 integration 下始终返回 0 结果，不要用）
2. **用数据库 date filter 查询**（唯一可靠方式）：
   ```bash
   curl -s -X POST "https://api.notion.com/v1/databases/{DIARY_DB_ID}/query" \
     -H "Authorization: Bearer $TOKEN" -H "Notion-Version: 2022-06-28" \
     --data-binary @/tmp/query.json --tlsv1.3
   # payload: {"filter": {"property": "发送日期", "date": {"equals": "2026-05-30"}}, "page_size": 10}
   ```
   → 返回 `results[0].id` 是完整的 36 字符 UUID（注意：字段名是 `发送日期`，不是 `Date`）
3. 读取该页所有 blocks，过滤 `type==to_do` 且 `checked==false` 的项
4. 在今天的 Have Done List 区插入这些未完成项（checked=false，文本保留）
5. 今天 To Do 区保留空的 unchecked 项（重新开始）

**已验证的未完成项**（2026.5.30 → 2026.5.31，10 项）：
- 华为电脑清理+优化 / 📰 Macro News 1h / 🤖 AI Study 1h / 📖 Reading 30min / 🏋️ Workout 30min⁺ / 👌Doing planks / ❌ NO Sugar / 💪 Kegel 5min⁺ / 💊 Supplements / ⚙️ SYSTEM DRIVEN?

## API 参考
见 `references/notion-diary-api.md`（技术备忘录，含 curl 模板和 urllib 注意事项）
- `references/monthly-summary.md` — 月度打卡汇总方法，含17项习惯 Key 名称、汇总脚本逻辑、报告格式模板

## 已知约束
- Python urllib 多次写入不稳定；用 bash/curl 更可靠
- Notion API 需每请求重试（connection reset 时）
- emoji 直接作为 `text.content` 传入即可
- 新建日记页后，页面 children 接口返回空 blocks（内容已写入，但 API 读取存在延迟或缓存）；读取昨日 unchecked items 时应搜索昨日日记页的 block 内容，不要依赖今日新建页的内容回读
- 日记页搜索时标题要精确匹配（含完整 emoji）；搜索 `"2026.5.29 日记"` 比 `"2026.5.29"` 更精准，避免匹配到悬案页等其他页面
- **paragraph block 不得含 `icon: null`** — Notion API 拒绝 `icon: null` 的 paragraph（非 toggle 子块）。读取模板 blocks 时必须过滤掉 `icon` 字段或替换 `null` 为 absent。
- **paragraph / to_do / bulleted_list_item / callout 不得含 `icon: null`** — 这四种 block 类型均不接受 `icon: null`（传 `null` 也报 400），写入前对所有 block 类型统一 `pop('icon', None)` 最安全。
- **批量写入上限**：单批建议 ≤20 blocks；超过 20 blocks 的批量写入容易触发 `Connection reset by peer`，推荐分批（如每批 10）+ 请求间隔 1-2 秒。
- **curl vs urllib**：写入操作用 curl（`subprocess.run`）比 Python urllib 更稳定，应作为首选。

## 文件结构
```
references/
  notion-diary-api.md    # 技术备忘录（含 API 模板和已知问题）
scripts/
  create_diary.py       # 已验证的完整脚本，直接 python3 create_diary.py 即可生成当日日记
```
# Notion 日记 · 月度打卡汇总参考

## 场景
对某个月份的所有日记页进行习惯完成率统计，生成月度报告。

---

## 日记数据库 ID
```
DIARY_DB_ID = "318cd9aa-41cc-8098-803e-ed230c9c7e80"
NOTION_TOKEN = "[NOTION_TOKEN_REDACTED]"
```

---

## 17 项习惯 Key 名称（to_do 文本中的关键字）

| Key（脚本内变量） | to_do 文本包含 |
|---|---|
| `Clients` | `Clients` |
| `Financial` | `Financial` |
| `Macro` | `Macro` |
| `AI Study` | `AI Study` |
| `Reading` | `Reading` |
| `Writing` | `Writing` |
| `Workout` | `Workout` |
| `Duolingo` | `Duolingo` |
| `English` | `English` |
| `Nap` | `Nap` |
| `Water` | `Water` |
| `Meditation` | `Meditation` |
| `Kegel` | `Kegel` |
| `Supplements` | `Supplements` |
| `BETTER` | `BETTER` |
| `BENEFIT` | `BENEFIT` |
| `SYSTEM` | `SYSTEM` |

---

## 汇总方法：查询 + Block 读取

### Step 1: 获取当月所有日记页 ID
```bash
curl -s -X POST "https://api.notion.com/v1/databases/${DIARY_DB_ID}/query" \
  -H "Authorization: Bearer ${NOTION_TOKEN}" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {
      "property": "Name",
      "title": {"contains": "2026.5"}
    },
    "sorts": [{"property": "Name", "direction": "ascending"}],
    "page_size": 50
  }' | python3 -c "
import sys, json
d = json.load(sys.stdin)
for r in d.get('results', []):
    title = r['properties']['Name']['title'][0]['text']['content'] if r['properties']['Name']['title'] else 'no title'
    print(r['id'], title)
"
```

> 注意：返回的 ID 是完整 36 字符 UUID（如 `352cd9aa-41cc-8104-92a2-c0678f5c5b3f`），不是 search API 返回的截断形式。

### Step 2: 读取每日 blocks 并提取 to_do 状态
每个日记页用 `GET /blocks/{page_id}/children?page_size=100` 读取所有 blocks，遍历 `type=="to_do"` 的 block，比对关键字是否出现在 `rich_text` 中，记录 `checked` 状态。

### Step 3: None / False / True 三态含义
| 值 | 含义 |
|---|---|
| `True` | 找到了该 habit 关键字且 checked=true |
| `False` | 找到了该 habit 关键字且 checked=false |
| `None` | 该日记页有内容，但 to_do 列表中未出现该关键字 |

### Step 4: 特殊页面类型
- **`synced_block` 页面**：页面只有 1 个 `synced_block`，内容在同步源的子块里，当 `None` 处理。
- **完全空白页**：API 返回 `results: []`，也是 `None`。
- **内容丰富但习惯区不完整**：如 5/15（79 blocks 有内容但习惯区不完整），`None` 项不计入完成率分母，仅 False/True 计入。

---

## 已知问题
- 某些页面有内容但习惯 to_do 区不完整，属日记格式不统一而非系统问题
- 5/23、5/24、5/25 连续空白为真实未打卡
- Notion API 有速率限制，循环内加 `time.sleep(0.5)` 避免 429

---

## 月度报告格式模板
```
## 📊 {月份} 月打卡月度总结（{start}–{end}）

### 打卡概况
- 应打卡天数：{days_in_month}
- 有记录天数：{days_with_entries}
- 整体打卡率：{rate}%

### 17项习惯完成率
[表格：习惯 | 完成天数 | 完成率 | 备注]

### 关键洞察
- 最强项：{top1}、{top2}
- 最弱项：{bottom1}、{bottom2}
- 空白日分析：{blank_days_summary}

### 下月建议
{personalized_suggestion}
```
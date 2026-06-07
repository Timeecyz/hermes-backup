# 微信/支付宝账单 → Notion 月度收支汇总写入流程

## 完整流程（2026-06-02 实测可用）

### Step 1: 解析账单文件

**微信支付（xlsx）**
```python
import pandas as pd
wx_raw = pd.read_excel('微信账单路径.xlsx', header=None)
wx = wx_raw.iloc[17:].copy()
wx.columns = wx.iloc[0]
wx = wx.iloc[1:].reset_index(drop=True)
wx.columns = ['交易时间','交易类型','交易对方','商品','收/支','金额(元)','支付方式','当前状态','交易单号','商户单号','备注']
wx['金额(元)'] = pd.to_numeric(wx['金额(元)'], errors='coerce')
```

**支付宝（csv，gbk编码，含制表符分隔字段）**
```python
import csv
raw = open('支付宝账单路径.csv', 'rb').read().decode('gbk')
lines = raw.split('\n')
data = []
for i in range(24, len(lines)):  # 表头在第24行（0索引）
    line = lines[i].rstrip('\r\n')
    if not line.strip(): continue
    reader = csv.reader([line])
    for row in reader:
        data.append(row)
# 前12列有效，最后一列是空串
ali = pd.DataFrame(data, columns=['交易时间','交易分类','交易对方','对方账号','商品说明','收/支','金额','收/付款方式','交易状态','交易订单号','商家订单号','备注','_extra'])
ali = ali.drop(columns=['_extra'])
ali['金额'] = pd.to_numeric(ali['金额'], errors='coerce')
```

### Step 2: 分类统计

**微信支出分类逻辑**
```python
def classify_wx(row):
    t = row['交易类型']
    who = str(row['交易对方'])
    desc = str(row['商品'])
    if row['收/支'] == '收入':
        return '红包收入' if '红包' in t else '转账收入'
    if t == '转账' or t == '微信红包':
        return '转账/红包'  # 不计入真实消费
    # 商户消费用关键词匹配分类...
```

**关键：微信转账/红包要剔除**，它们是资金流转（子玉、Logan等个人转账），不是消费。

### Step 3: 写入 Notion（child_page 类型页面）

**目标页面类型判断**
```python
# GET /v1/blocks/{page_id} 返回 type="child_page" → 可以直接写 blocks
# 关联数据库的条目在 API 里就是 child_page，其 ID = 页面 ID
```

**Python 写入函数**
```python
import json, urllib.request, ssl

NOTION_KEY = "[NOTION_TOKEN]"

def notion_patch(path, data):
    url = f"https://api.notion.com/v1/{path}"
    body = json.dumps(data).encode()
    headers = {"Authorization": f"Bearer {NOTION_KEY}", "Notion-Version": "2025-09-03", "Content-Type": "application/json"}
    req = urllib.request.Request(url, data=body, headers=headers, method='PATCH')
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, context=ctx, timeout=20) as r:
        return json.load(r)

# 追加 blocks
result = notion_patch(f"blocks/{PAGE_ID}/children", {"children": blocks})
```

**更新已有 block（修改标题）**
```python
result = notion_patch(f"blocks/{block_id}", {
    "heading_2": {"rich_text": [{"type": "text", "text": {"content": "新标题"}}]}
})
```

**删除 block**
```python
def notion_delete(block_id):
    url = f"https://api.notion.com/v1/blocks/{block_id}"
    req = urllib.request.Request(url,
        data=json.dumps({}).encode(),
        headers={"Authorization": f"Bearer {NOTION_KEY}", "Notion-Version": "2025-09-03", "Content-Type": "application/json"},
        method='DELETE')
    with urllib.request.urlopen(req) as r:
        return json.load(r)
result = notion_delete("block_id")
# 成功返回 {"object": "block", "archived": true, ...}
```

### Step 4: ID 格式转换（32位短ID → 36位UUID）
```python
import uuid
short = "355cd9aa41cc8183a037d8150b1875f7"  # Notion URL 中的 ID
formatted = str(uuid.UUID(hex=short))       # "355cd9aa-41cc-8183-a037-d8150b1875f7"
```

## 关键陷阱

1. **微信 xlsx 跳过前17行**（前10行是表头说明，第17行才是列名行）
2. **支付宝 csv 第24行（0索引）是表头**，前23行是账单说明
3. **支付宝有45笔"不计收支"**：包含余额宝收益、退款、咖啡机款（¥13,300×3笔）。咖啡机是商家重复扣款后的退款，实际只需记一笔。
4. **微信 ¥16,000 转账-退款不是收入**：对方把钱退回来，不要计入收入
5. **关联数据库的 properties 为空**：不要尝试用 `/databases/{id}/query`，直接写 child_page 的 blocks
6. **批次 ≤20 blocks**：大批次有失败率，本环境用 ssl context 防 Connection reset
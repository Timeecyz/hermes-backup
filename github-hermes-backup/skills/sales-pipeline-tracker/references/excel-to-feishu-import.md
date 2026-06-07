# Excel → 飞书多维表格 导入流程

## 完整工作流（2025-05-28 实测）

### Step 1: 判断文件类型
```bash
file yourfile.xlsx
# 输出 "CDFV2 Encrypted" = 旧版加密 xls/xlsx
# 输出 "Zip archive" = 正常 xlsx
```

### Step 2: 加密文件解密
```python
import msoffcrypto, io

pwd = '密码'
with open('yourfile.xlsx', 'rb') as f:
    file = msoffcrypto.OfficeFile(f)
    file.load_key(password=pwd)
    decrypted = io.BytesIO()
    file.decrypt(decrypted)
    decrypted.seek(0)
    with open('/tmp/decrypted.xlsx', 'wb') as out:
        out.write(decrypted.read())
```

> ⚠️ 解密后文件用 `openpyxl` 直接读取（不需要 xlrd）

### Step 3: 读取 Excel 数据
```python
import openpyxl
wb = openpyxl.load_workbook('/tmp/decrypted.xlsx', read_only=True, data_only=True)
ws = wb['客户总表']  # 按实际工作表名
headers = [cell.value for cell in ws[3]]  # 第3行是表头（1-indexed）
clients = [dict(zip(headers, row)) for row in ws.iter_rows(min_row=4, values_only=True) if row[3]]
```

### Step 4: 获取飞书现有记录（去重）
```python
import json

def parse_f(val):
    if val is None: return ''
    if isinstance(val, list) and len(val) > 0:
        first = val[0]
        if isinstance(first, dict): return first.get('text', str(first))
        return str(first)
    if isinstance(val, dict): return val.get('text', str(val))
    return str(val)

# 分页拉取所有 records，建立 (姓名小写, 电话后4位) 去重集合
existing_keys = set()
for item in existing:
    f = item['fields']
    name = parse_f(f.get('昵称', '')).strip().lower()
    phone_raw = parse_f(f.get('客户其它重要信息', ''))
    phone_last4 = phone_raw[-4:] if phone_raw and len(phone_raw) >= 4 else ''
    if name: existing_keys.add((name, phone_last4))
```

### Step 5: 字段映射（Excel → 飞书）
| Excel 列 | 飞书字段 | 注意事项 |
|---------|---------|---------|
| 姓名 | 昵称 | |
| 分级(A/B/C/D) | 未来业务价值-客户级别 | 需映射为完整字符串 |
| 编号 | 客户编号（INI/FUI...） | |
| 电话 | 客户其它重要信息 | 格式："电话: xxx" |
| 来源 | 客户来源 | |
| 关联介绍人 | 客户推荐人 | |
| 成交时间 | 实际成交时间 | Excel日期serial → 毫秒时间戳 |
| 上次联系时间 | 最近一次联系时间 | 同上 |
| 基金/保险等 | 需求类型 | 多选字段，传 list |

**日期转换**（Excel serial → 飞书毫秒时间戳）：
```python
from datetime import datetime, timedelta
def excel_date_to_ts(serial):
    if isinstance(serial, datetime):
        return int(serial.timestamp() * 1000)
    d = datetime(1899, 12, 30) + timedelta(days=int(serial))
    return int(d.timestamp() * 1000)
```

**客户级别映射**：
```python
LEVEL_MAP = {
    'A': 'A类-已成交过客户',
    'B': 'B类-跟进中待成交客户',
    'C': 'C类-已开口铺垫业务但没有递交计划书客户',
    'D': 'D类-从未开口过业务的客户',
}
```

### Step 6: 批量导入飞书
```python
# 每批10条，batch_create API
payload = {"records": [{"fields": fields_dict}] * 10}
url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records/batch_create"
# 飞书限制每批最大100条，10条/批是安全值
```

---

## 常见错误码
| code | 含义 | 解决 |
|------|------|------|
| 99991672 | 缺权限（sheets API） | 开通 sheets:spreadsheet 权限 |
| 404 page not found | token错误或文档不在该组织 | 确认 APP_TOKEN 格式 |
| 1770002 | 文档不存在（docx API） | 确认是 bitable 还是 docx |

---

## 蛮子客户数据特征（2025-05-28）
- Excel 来源表：`客户总表25年11月24日`，200条客户（198有效）
- 飞书目标表：`tblSroifTqF6xJ6w`，导入前82条，导入后270条
- 去重策略：(姓名小写, 电话后4位)，跳过10条重复
- Excel中部分行的「分级」「编号」字段为空，需要兼容处理
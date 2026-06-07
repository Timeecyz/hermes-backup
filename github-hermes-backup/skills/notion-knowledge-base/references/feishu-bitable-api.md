# 飞书 Bitable vs Spreadsheet API 区分

## 快速判断

| 飞书链接格式 | 类型 | API 端点 |
|------------|------|---------|
| `/base/xxxxx` | 多维表格（Bitable） | `/bitable/v1/apps/{id}` |
| `/sheets/xxxxx` | 电子表格（Spreadsheet） | `/sheets/v3/spreadsheets/{id}` |

## Bitable API 基础

```bash
TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{"app_id": "...", "app_secret": "..."}' | python3 -c "import sys,json; print(json.load(sys.stdin)['tenant_access_token'])")

# 列出所有 tables
curl -s "https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables" \
  -H "Authorization: Bearer $TOKEN"

# 查询 records（含 filter）
curl -s -X POST "https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records/search" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"page_size": 100, "filter": {"conjunction": "and", "conditions": [...]}}'
```

## 权限陷阱（已验证）

### 1. 自建应用需单独开通 Bitable 权限
错误代码：`99991672` — 需要在飞书开放平台申请 `bitable:app` 权限。

路径：开放平台 → 应用 → 权限管理 → 添加 `bitable:app` → 创建版本 → 发布（企业版需管理员审批）

### 2. 关联数据库（Linked Database / Multi-factory）
当 database 的 `data_sources` 字段非空时：
- GET `/databases/{id}` 返回的 `properties` 为空字典
- POST `/databases/{id}/query` 返回 400 "invalid_request_url"
- 底层 source DB 未共享时 → 404 "object_not_found"

**解法**：让用户在页面内新建普通 inline Table。

## Known app_id（留余家族办公室）
- app_id: `cli_aa9abc638cf91bb4`
- app_secret: `2anV19EgpXL3r14ITxgoug2yatBn2eut`
- 客户管理 database: `Mvz2bNhJraRqVesXjgBcUCjcncf`
- 飞书多维表格 app_token: `WXghb4GgCa1NO1sydjIcNCpZn2g` ← 实际使用的客户总表

## Tables 列表（2026-05）
| 表名 | table_id |
|------|----------|
| 客户总表 | tblSroifTqF6xJ6w |
| 经纪人及渠道信息表 | tblgynK5zoms92K4 |
| 跟进记录表 | tblfY4JRoO5vlWDF |
| 客户详细信息表 | tblxOdaFGe1i1j4L |

### 客户总表关键字段ID映射（tblSroifTqF6xJ6w, 84条记录）
| 字段名 | field_id | 类型 |
|--------|----------|------|
| 昵称 | fldpd6JPzr | Text |
| 未来业务价值-客户级别 | flds7Oexzj | SingleSelect |
| 意向状态 | fld4zGV1w2 | SingleSelect |
| 客户来源 | fldBj4ndg4 | Text |
| 需求类型 | fldXMit4u6 | MultiSelect |
| 成交业务标签 | fldZ0AjplP | MultiSelect |
| 最近一次联系时间 | fldokhjkfk | DateTime |
| 预计下一次联系时间 | fldgAXuEE4 | DateTime |
| 客户爱好 | fldZUl9Rf0 | Text |
| 备注 | fldMm1kDGQ | Text |

**客户级别选项值：**
- A类-有明确需求，最近要签（1个月内）
- B类-有意向但还在考虑（1-3个月）
- C类-有需求但还没到时机（3个月以上）
- D类-联系过但没下文了
- E类-从未联系过，完全空白

**意向状态选项值：**
- 潜在客户 / 咨询中 / 方案沟通 / 成交 / 流失

**数据分布（84条记录）：** 成交39 / 未填45 / B类19 / C类38 / D类20 / E类5 / A类2
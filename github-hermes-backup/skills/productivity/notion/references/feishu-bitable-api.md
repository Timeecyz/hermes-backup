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

# 读取 database meta
curl -s "https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}" \
  -H "Authorization: Bearer $TOKEN"

# 列出所有 tables
curl -s "https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables" \
  -H "Authorization: Bearer $TOKEN"

# 查询 records
curl -s -X POST "https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"page_size": 10}'
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

## 已知 app_id（留余家族办公室）
- app_id: `cli_aa9abc638cf91bb4`
- app_secret: `2anV19EgpXL3r14ITxgoug2yatBn2eut`
- 客户管理 database: `Mvz2bNhJraRqVesXjgBcUCjcncf`

## Tables 列表（2026-05）
| 表名 | table_id |
|------|----------|
| 客户总表 | tblapoe6xRO8nQGG |
| 经纪人及渠道信息表 | tbl24L1btLJPKrPT |
| 跟进记录表 | tbl9RGrcMUQKuHgo |
| 客户详细信息表 | tblXlTqRz0NXp616 |
| ... | ... |

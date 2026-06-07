# Feishu API 路由判断清单

## 如何判断 Feishu 链接类型

拿到一个 Feishu URL，先看路径第二个 segment：

| URL pattern | 类型 | API endpoint |
|------------|------|---------------|
| `/sheets/...` | 飞书电子表格 (Spreadsheet) | `GET /sheets/v3/spreadsheets/{token}` |
| `/base/...` | 多维表格 (Bitable) | `GET /bitable/v1/apps/{token}` |
| `/docs/...` | 文档 (Doc) | `GET /doc/v2/doc/{token}` |

**本Session教训**：`cli_aa9abc638cf91bb4` 这个 app 有 `drive:drive` 权限，可以访问 Bitable，但缺少 `sheets:spreadsheet` 权限。导致用 sheets API 访问 base URL 始终报 99991672。

**经验**：飞书自建应用默认可能只有部分权限，需要在开放平台手动添加权限 + 创建版本发布后才能生效。

## Bitable vs Spreadsheet 核心差异

- **Spreadsheet（电子表格）**：类 Excel，API: `/sheets/v3/`，需要 `sheets:spreadsheet` scope
- **Bitable（多维表格）**：类 Airtable，API: `/bitable/v1/`，需要 `bitable:app` scope（通常自建应用默认有）
- **同名冲突**：`Mvz2bNhJraRqVesXjgBcUCjcncf` 这个 token 在 sheets 里"not exist"，在 bitable 里却存在——说明同一个 token 在不同 API 下有不同含义

## 已知可用 token（截至 2026-05-27）

| 名称 | Token | 类型 |
|------|-------|------|
| 留余家族办公室-客户及渠道管理 | `Mvz2bNhJraRqVesXjgBcUCjcncf` | Bitable |
| App ID | `cli_aa9abc638cf91bb4` | 应用 |
| App Secret | `2anV19EgpXL3r14ITxgoug2yatBn2eut` | 秘钥 |

Bitable 表格列表：
- 客户总表：`tblapoe6xRO8nQGG`
- 经纪人及渠道信息表：`tbl24L1btLJPKrPT`
- 跟进记录表：`tbl9RGrcMUQKuHgo`
- 客户详细信息表：`tblXlTqRz0NXp616`

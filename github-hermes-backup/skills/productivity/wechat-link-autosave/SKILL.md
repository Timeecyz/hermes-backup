---
name: wechat-link-autosave
description: 蛮子发微信链接+10秒沉默 → 自动提取+打标签+存Notion。触发条件：收到微信文章链接且10秒内无后续指令。
tags:
  - notion
  - 微信
  - auto-save
  - 蛮子专用
last_updated: 2025-05-31
---

# 微信链接自动学习存入 Notion

## 触发条件
蛮子发来微信文章链接，且10秒内没有补充指令。

## 完整流程

### ⚠️ 默认语言：中文
所有正文内容、标签、摘要全部用中文写。蛮子明确要求"你默认中文，内容也帮我改中文"，不写英文。

### ⚠️ 必须保存原文链接
存入 Notion 时，**必须**在页面的"网址"字段写入微信/原网站链接。
用途：万一蛮子要看原文，可以直接点进去。
这个字段是自动存入流程的强制要求，不是可选项。

### Step 1: 提取内容
```bash
web_extract urls=["<链接>"]
```
微信被拦时用 `browser_navigate`，遇到验证码截图告知蛮子。

### Step 2: 存入 Notion 数据库
数据库ID：`349cd9aa-41cc-8017-a0f9-ff07a4a76b7d`

**建页：**
```bash
curl -s -X POST 'https://api.notion.com/v1/pages' \
  -H "Authorization: Bearer <NOTION_KEY>" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"database_id": "349cd9aa-41cc-8017-a0f9-ff07a4a76b7d"},
    "properties": {
      "文档-命名规则-期数.播客/书籍名字.节目名称.摘抄": {"title": [{"text": {"content": "<标题>"}}]},
      "网址": {"url": "<原文链接>"},
      "Tags": {"multi_select": [{"name": "公众号"}, {"name": "AI学习"}]},
      "类别": {"multi_select": [{"name": "公众号"}]},
      "领域": {"multi_select": [...]}
    }
  }'
```

### Step 3: 写摘要正文
用 `PATCH /v1/blocks/{page_id}/children` 写：
- 核心观点（callout + emoji 💡）
- 关键章节/角色介绍
- 要点总结（numbered callout）

### Step 4: 打标签（动态）
基础标签：`公众号`（固定）
按内容匹配：
- AI相关 → `AI学习`、`AI工作流`、`AI团队搭建`
- 个人成长 → `个人成长`、`决策及系统化思考`
- 保险/财富 → `保险`、`财富管理`
- 自媒体 → `自媒体运营`

### Step 5: 通知蛮子
存好后告知：「已存Notion，附链接」

## 排错
- 微信被拦 → browser_navigate；验证码 → 截图告知蛮子
- emoji 报错 → 换标准emoji
- 建页失败 → 查 validation_error 详情
- Notion API 访问数据库404，但token正确 → URL里的ID可能是视图ID，不是数据库ID。让蛮子从数据库页面 **"..." → Copy link** 获取真正的数据库ID，或者通过查询数据库内容反查ID
- API限流报 "Connection reset" → 等30秒再试，分批写入
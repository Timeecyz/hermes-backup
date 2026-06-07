---
name: weread
description: 微信读书（WeRead）数据查询与笔记管理技能。获取书架、搜索书籍、查看阅读进度/时长、获取笔记划线、热门书评、章节信息、随机笔记抽取和批量导出。当用户提到"微信读书"、"WeRead"、"书架"、"读书进度"、"划线"、"笔记"、"书评"、"在读"、"读完"、"阅读时长"、"读书回顾"、"导出笔记"时使用。
---

# 微信读书 Skill

通过微信读书 Web API 获取用户的阅读数据。依赖 API Key 认证。

## 认证方式（API Key，Bearer Token）

```
Gateway: https://i.weread.qq.com/api/agent/gateway
Header:  Authorization: Bearer <wrk-xxx>
Content-Type: application/json
```

所有请求均为 POST，JSON body 格式：
```json
{"api_name": "/endpoint", "skill_version": "1.0.5", ...其他参数}
```

**认证 Header 格式：** `Authorization: Bearer <wrk-xxx>`（Bearer 前有空格）

**API Key 有效期：** key 绑定了微信读书账号，账号变更或重新登录后 key 可能失效（返回 401）。

## 已知可用端点（skill_version=1.0.5）

| 端点 | 用途 | 必填参数 |
|------|------|---------|
| `/store/search` | 搜索书籍 | keyword, count |
| `/book/info` | 书籍详情 | bookId |
| `/book/chapterinfo` | 章节目录 | bookId |
| `/book/getprogress` | 阅读进度 | bookId（返回 progress 0-100） |
| `/book/bookmarklist` | 划线内容 | bookId |
| `/review/list/mine` | 个人想法/点评 | bookid, count |
| `/user/notebooks` | 有笔记的书列表 | count, skill_version |
| `/readdata/detail` | 阅读统计 | mode: overall |
| `/shelf/sync` | 书架同步 | — |

## 已知不可用端点（返回 499 ERR）

以下端点均返回 499，不可使用：
- `/notebook/list`、`/notes/list`、`/book/notes`
- `/book/chapterinfo`（带 skill_version 参数时报 499，需先调 `/book/info`）
- `/book/underlines`、`/book/bestbookmarks`（需先获取 chapterUid）
- `/readstate/list`、`/reading/booklist`

## 合集书与多版本陷阱

**合集书（搜索结果第一个往往是错的）：**
- ❌ 「诺贝尔经济学奖8册」bookId=3003944801 → 0 条划线
- ✅ 「思考快与慢」单独搜索 → 可用独立 bookId
- ❌ 「沉思录」搜索第一个结果往往是无笔记版本
- ✅ 沉思录正确版本：bookId=26797118（实操验证 124 条划线）
- ✅ 「贫穷的本质」搜索第一个是增订版，修订版另有 bookId，需多搜几个结果确认

**单本书多版本：** 微信读书同一本书常有多个版本（精装/平装/新版），只有读过的那个版本有笔记。换版本后数据清零。

## 当前有效 API Key（2026-06-07 实测）

- `wrk-Xe508qCLT1mmtNkaRefYmgAA` — 蛮子主账号，116 本有笔记的书
- 旧 key `wrk-NC8GUZ0jSe2F8AGayw_wBwAA` 已作废
- 存储位置：`~/.hermes/secret&API.md`（与飞书 App 凭证同文件）

## 蛮子的书架数据（2026-06-07 实测）

- 116 本有笔记的书，共 9 个主题分类
- 主题分布：理财9本、思维8本、成长12本、哲学3本、AI/科技若干、健康若干
- 笔记量最大的书：《跨越不可能》262条划线+50条想法，《掌控习惯》209条

## 已验证可用的 bookId（蛮子书架，2026-06-07）

| 书名 | bookId | 划线 | 想法 |
|------|--------|------|------|
| 金钱的艺术 | 3300189789 | 126 | 35 |
| 财富方程式 | 3300128302 | 156 | 32 |
| 纳瓦尔宝典 | 44026191 | 122 | 50 |
| 贪婪的多巴胺 | 41626009 | 85 | 50 |
| 跨越不可能 | 3300059487 | 262 | 50 |
| 掌控习惯 | 26934843 | 209 | 50 |
| 深度工作 | 909893 | 118 | 50 |
| 一生之敌 | 3300120540 | 92 | 48 |
| 沉思录 | 26797118 | 124 | 50 |
| 深度关系 | 3300076204 | 0 | 0（无笔记） |
| 当下的力量 | 848673 | 129 | 49 |
| 臣服实验 | 3001378060 | 0 | 0（无笔记） |
| 贫穷的本质 | 3300187091 | 0 | 0（增订版无笔记，需换版本） |

## 批量写入 Notion 的标准工作流

当需要将多本书的笔记批量写入 Notion 时：

1. **搜索确认 bookId** — 每本书单独 `/store/search`，取第一个结果
2. **验证笔记数量** — 调 `/book/bookmarklist` + `/review/list/mine`，确认 > 0 再创建页面
3. **收集全部数据** — 按章节分组划线，想法按 chapterName 归类
4. **批量写入** — 每批 20 blocks + 0.5s 间隔，中断用指数退避重试（最多 5 次）
5. **分批启动** — 单次超过 10 本书时分批启动（每批间隔 2s），避免连接过载

**Notion 页面创建字段（蛮子的读书笔记库）：**
- `title`: 书名
- `Tags`: multi_select（主题标签，如"理财""思维""成长"）
- `类别`: multi_select（统一填"书籍"）
- `Date`: date（统一填当天日期）
- `网址`: url（微信读书链接）

**连接中断处理（Notion API）：**
- 原因：连续写入 40+ blocks 后偶发 `Connection reset by peer`（errno 104）
- 策略：`time.sleep(3 ** attempt)` 指数退避 + 最多 5 次重试
- 建议每批间隔 1-2s，网络质量差时比 0.5s 更稳
- 等待 5s 后重试对恢复性错误特别有效

**已知偶发连接中断的书（验证可重试成功）：**
- 有限与无限的游戏（3300014694）、原则（921568）
- 最小阻力之路（3300060301）、自信的陷阱（38458536）
- 跨越不可能（3300059487）、掌控习惯（26934843）、一生之敌（3300120540）

## 返回码诊断

| 状态码 | 含义 | 处理 |
|--------|------|------|
| 401 LOGIN ERR | API Key 无效或格式错误 | 检查 `Bearer ` 前缀是否正确 |
| 499 ERR | 端点不存在或参数缺失 | 检查 `skill_version` 是否为 `1.0.5` |
| 200 + totalBookCount=0 | Key 有效但账号无笔记数据 | 换主账号 key（https://weread.qq.com/r/weread-skills 登录确认） |
| Connection reset by peer | 网络波动或服务端断开 | 指数退避重试，等待 5s 后再试 |

## 回退策略：Web 搜索替代方案

当 weread API 无法使用时（无有效 key / 连接失败）：

1. **用户直接分享** — 从微信读书 App「笔记」页截图或复制划线内容发给管家
2. **公开信息补全** — 用 web_search + web_extract 抓取豆瓣/当当书籍页面获取简介/目录
3. **手动提供 Cookie** — 用户 Chrome 登录 weread.qq.com → F12 → Application → Cookies → 找到 `wr_sid`

---

## 脚本路径说明

weread API 脚本可能未安装在标准路径。如遇 `file not found`，用 `execute_code` + `urllib` 直接调 API，不依赖本地脚本。

**存储位置：** `~/.hermes/secret&API.md`（与飞书 App 凭证同文件）

---

## 蛮子的私人笔记库

蛮子会单独写「点滴思考」类短内容存入 Notion（个人感悟/哲学思考）。
**点滴思考的 Notion 数据库 ID**: `35ccd9aa41cc80f2b550e111aeceb6bd`
**读书笔记数据库 ID**: `349cd9aa-41cc-8017-a0f9-ff07a4a76b7d`